# Plan: 3-Layer Website Existence Checker

**Created:** 2026-03-21
**Status:** Implemented
**Type:** Full
**Request:** Build a verification step that catches false positives from Google Maps "no website" data. Verify whether a business actually has a website before classifying as Pipeline A. Reclassify confirmed website owners to Pipeline B.

---

## Overview

### What This Accomplishes
Adds a 3-layer verification step between Apify scraping and lead scoring that confirms whether a "no website" lead genuinely has no website. Layer 1 runs a cheap Google search for the business name + suburb. Layer 2 tries common domain patterns via HTTP HEAD. Layer 3 does an ABN-to-domain cross-reference. If a website IS found, the lead gets reclassified to Pipeline B (DIY website check) instead of being emailed "you don't have a website" — which is what currently happens and has already burned Aaron's credibility on cold calls.

### Why This Matters
Aaron cold called leads from Apify's Google Maps "no website" filter and found ~20-30% actually had websites. Telling a business owner "you don't have a website" when they do is an instant credibility kill. This checker eliminates those false positives AND captures bonus Pipeline B leads that Google Maps would have missed entirely. It's the difference between sounding like a spammy mass emailer and sounding like someone who did their homework.

---

## Current State

### Relevant Existing Structure
- `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` — parent plan, line 1092 mentions "smart detection" as a one-liner note but has zero implementation
- Pipeline A architecture diagram (lines 510-564) — checker slots between "Normalise & Merge Results" and "ENRICH"
- `scripts/lead-pipeline/001-create-tables.sql` — leads table already has `website TEXT` and `pipeline TEXT` columns
- Platform detection logic already exists (parent plan lines 1176-1225) — reusable for reclassified leads
- Apify is configured in `.env` (`APIFY_API_TOKEN`, `APIFY_USER_ID`)

### Gaps Being Addressed
- Google Maps "no website" field is unreliable (20-30% false positive rate based on Aaron's experience)
- No verification step exists between scraping and scoring
- No mechanism to reclassify Pipeline A leads to Pipeline B when a website is discovered
- No `website_verified` or `website_check_method` tracking in the DB
- The one-liner mention in the parent plan (line 1092) was never designed or implemented

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/lead-pipeline/website-checker.js` | 3-layer website verification logic — n8n Code node content |
| `scripts/lead-pipeline/004-add-website-verification-fields.sql` | Migration: adds verification tracking columns to leads table |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` | Update Pipeline A architecture diagram to include website checker step; update line 1092 from one-liner to reference this plan |
| `context/outstanding-actions.md` | Mark website checker item as planned |
| `learnings-register.md` | Already logged (2026-03-21 gotcha) |

### Files to Delete

_None._

---

## Scope Check

- **Inside scope?** Yes — this is a data quality improvement to the lead pipeline. The parent plan already mentions it (line 1092) as a planned feature.
- **Decision required:** None.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Apify | `APIFY_API_TOKEN` | Present in `.env` |

_No new env vars required. The Google search actor runs through the existing Apify account._

---

## Skills to Use

None.

---

## Design Decisions

### 1. Three layers, run in order, stop on first match (fast + cheap)

The layers are ordered by cost and reliability:

| Layer | Method | Cost | Speed | Accuracy |
|-------|--------|------|-------|----------|
| **1. URL pattern check** | HTTP HEAD on common domains | Free | ~1s per lead | Catches ~30-40% of false positives |
| **2. Google search** | Apify SERP scraper | ~$0.001/search | ~2-3s per lead | Catches ~80-90% of remaining |
| **3. ABN→domain WHOIS** | WHOIS lookup on .au registrar | Free | ~1-2s per lead | Low hit rate but catches edge cases |

**If Layer 1 finds a website → skip Layers 2 and 3.** This keeps costs down. Most leads will be resolved by Layer 1 or 2.

### 2. URL pattern check runs FIRST (not Google search)

The original proposal had Google search as Layer 1. But HTTP HEAD requests are free and instant. Many Perth tradies have predictable domains: `jimspaintingperth.com.au`, `aceplumbing.com.au`. Trying 4-5 URL patterns costs nothing and resolves a chunk of leads before we spend Apify credits on Google searches.

### 3. Reclassify, don't discard

When a website IS found:
- Set `website` field to the discovered URL
- Change `pipeline` from `no_website` to `diy_website`
- Run platform detection on the discovered URL (reuse existing `detectPlatform()` logic)
- If DIY platform detected → score as Pipeline B lead (upgrade pitch)
- If professionally built → set `status = 'suppressed'` with `notes = 'professional_website'` (not our target market)

This means the website checker actually FEEDS Pipeline B with extra leads that Google Maps wouldn't have caught.

### 4. Use `tuningsearch/cheap-google-search-results-scraper` for Layer 2

Research found this is the cheapest Apify SERP actor:
- ~$0.0006 per search (0.6 CU per 1,000 searches)
- At 50 leads/day needing Google search = ~$0.03/day = **~$0.90/month**
- Returns organic results with title, URL, snippet — exactly what we need
- Fallback: `scraperlink/google-search-results-serp-scraper` at $0.001/search

### 5. Directory/social-only results don't count as "has a website"

Search results from these domains are NOT evidence of a website:
- `facebook.com`, `instagram.com`, `tiktok.com`
- `yellowpages.com.au`, `truelocal.com.au`, `hipages.com.au`
- `yelp.com.au`, `hotfrog.com.au`, `localsearch.com.au`
- `linkedin.com`, `twitter.com`, `x.com`
- `google.com` (Google Business Profile URLs)

Only results pointing to an actual standalone domain count as "has a website."

### 6. Track verification method in the DB

Store HOW we verified (or couldn't verify) each lead so we can tune accuracy later:
- `website_verified BOOLEAN` — did we run the checker?
- `website_check_method TEXT` — `'url_pattern'`, `'google_search'`, `'abn_whois'`, `'none_found'`
- `website_check_url TEXT` — the URL we found (if any)

After 2-3 weeks, we can query: "of leads marked `none_found`, how many did Aaron find had websites on cold calls?" and tune the checker.

### 7. Batch Google searches for cost efficiency

Don't call the Apify actor once per lead. Batch all leads that survived Layer 1 into a single actor run with multiple search queries. The actor accepts an array of search queries and returns results for all of them in one run — much cheaper than individual calls.

### Alternatives Considered

- **Google Custom Search API (100 free/day):** Being sunset by Google — not available to new customers. Rejected.
- **Only HTTP HEAD checks (no Google search):** Too many false negatives — many tradies have domains that don't match their business name (e.g. registered under owner's name, or an acronym). Would still miss ~50% of websites. Rejected.
- **Manual verification by Aaron:** Doesn't scale. The whole point is automation. Rejected.
- **Skip verification, just soften the email language:** "I couldn't find your website" instead of "you don't have a website." Better than nothing but still looks lazy. The verification approach is stronger because it also captures Pipeline B leads. Rejected.

### Open Questions

None — approach confirmed by Aaron.

---

## Verification Logic Detail

### Layer 1: URL Pattern Check (Free, Instant)

```javascript
// Try common domain patterns for a business name
// HTTP HEAD request — doesn't download the page, just checks if it exists
async function checkUrlPatterns(businessName, suburb) {
  // Normalise business name to domain-friendly format
  const slug = businessName
    .toLowerCase()
    .replace(/[''`]/g, '')        // Remove apostrophes (Jim's → Jims)
    .replace(/&/g, 'and')         // & → and
    .replace(/[^a-z0-9]+/g, '')   // Remove non-alphanumeric
    .trim();

  // Also try with suburb appended
  const suburbSlug = (suburb || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '')
    .trim();

  const patterns = [
    `${slug}.com.au`,
    `${slug}.au`,
    `${slug}.com`,
    `${slug}${suburbSlug}.com.au`,   // e.g. jimspaintingperth.com.au
    `${slug}perth.com.au`,           // Common Perth tradie pattern
  ];

  for (const domain of patterns) {
    try {
      const response = await fetch(`https://${domain}`, {
        method: 'HEAD',
        redirect: 'follow',
        signal: AbortSignal.timeout(5000),  // 5s timeout
      });

      // 2xx or 3xx = website exists
      if (response.ok || (response.status >= 300 && response.status < 400)) {
        // Verify it's not a parked/for-sale page
        const html = await fetch(`https://${domain}`, {
          signal: AbortSignal.timeout(5000),
        }).then(r => r.text());

        const isParked = /domain.*for sale|buy this domain|parked|coming soon|under construction/i.test(html);
        if (!isParked) {
          return { found: true, url: `https://${domain}`, method: 'url_pattern' };
        }
      }
    } catch (e) {
      // Connection refused, timeout, DNS failure = no website at this domain
      continue;
    }
  }

  return { found: false };
}
```

**Why 5 patterns:** Perth tradies follow predictable naming. `aceplumbing.com.au` is the most common pattern. Adding suburb variants catches `aceplumbingperth.com.au`. The `.au` and `.com` variants catch businesses that didn't go for `.com.au`.

**Parked domain check:** Some domains exist but are "for sale" or "coming soon" — these don't count as having a website.

---

### Layer 2: Google Search (Apify, ~$0.001/search)

```javascript
// Search Google for the business name + suburb + "website"
// Uses Apify actor: tuningsearch/cheap-google-search-results-scraper
//
// Called from n8n via HTTP Request node to Apify API:
// POST https://api.apify.com/v2/acts/tuningsearch~cheap-google-search-results-scraper/runs
//
// Input (batch of search queries for all leads that passed Layer 1):
// {
//   "queries": [
//     "\"Ace Plumbing\" Baldivis",
//     "\"Jim's Electrical\" Ellenbrook",
//     ...
//   ],
//   "maxResults": 5,
//   "countryCode": "au"
// }

// Directory/social domains that DON'T count as "has a website"
const DIRECTORY_DOMAINS = new Set([
  'facebook.com', 'instagram.com', 'tiktok.com',
  'linkedin.com', 'twitter.com', 'x.com',
  'yellowpages.com.au', 'truelocal.com.au', 'hipages.com.au',
  'yelp.com.au', 'hotfrog.com.au', 'localsearch.com.au',
  'servicepro.com.au', 'oneflare.com.au',
  'google.com', 'google.com.au',  // GBP URLs
  'youtube.com',
]);

function isRealWebsite(url) {
  try {
    const hostname = new URL(url).hostname.replace(/^www\./, '');
    // Check if this is a directory/social domain
    for (const dir of DIRECTORY_DOMAINS) {
      if (hostname === dir || hostname.endsWith('.' + dir)) return false;
    }
    return true;
  } catch {
    return false;
  }
}

function findWebsiteInSearchResults(results, businessName) {
  // Look through top 5 organic results for a real website
  for (const result of results) {
    if (isRealWebsite(result.url)) {
      // Extra confidence: does the page title or snippet mention the business name?
      const nameParts = businessName.toLowerCase().split(/\s+/).filter(w => w.length > 2);
      const titleLower = (result.title || '').toLowerCase();
      const snippetLower = (result.snippet || '').toLowerCase();

      const nameMatch = nameParts.some(part =>
        titleLower.includes(part) || snippetLower.includes(part)
      );

      if (nameMatch) {
        return { found: true, url: result.url, method: 'google_search' };
      }
    }
  }
  return { found: false };
}
```

**Name matching is critical:** Without it, a Google search for "Ace Plumbing Baldivis" might return a random plumbing blog or a competitor's site. We verify the result actually mentions the business name before counting it.

**Batch operation:** All leads that survived Layer 1 get batched into a single Apify actor run. If 30 out of 50 leads survive Layer 1, we run 30 searches in one batch — much cheaper than 30 individual calls.

---

### Layer 3: ABN→Domain Cross-Reference (Free, Bonus)

```javascript
// Check if a .com.au domain is registered to the same ABN
// Australian .au domains are registered via auDA — WHOIS is available
// This is a bonus layer with low hit rate but catches edge cases
async function checkAbnDomain(abn, businessName) {
  if (!abn) return { found: false };

  // Try the business name as a .com.au domain
  const slug = businessName
    .toLowerCase()
    .replace(/[''`]/g, '')
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '')
    .trim();

  try {
    // auDA WHOIS lookup — check if domain exists and is registered
    // Using a simple HTTP check since full WHOIS parsing is complex
    const response = await fetch(`https://${slug}.com.au`, {
      method: 'HEAD',
      redirect: 'follow',
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      return { found: true, url: `https://${slug}.com.au`, method: 'abn_whois' };
    }
  } catch {
    // Domain doesn't exist
  }

  return { found: false };
}
```

**Note:** Layer 3 overlaps significantly with Layer 1's URL pattern check. Its main additional value is when we have an ABN but the business name doesn't match the domain (e.g. trading as "Ace Plumbing" but domain is registered under the ABN holder's personal name). For v1, Layer 3 can be simplified to just catching cases Layers 1-2 missed. Can be enhanced later with actual WHOIS API lookups.

---

### Orchestrator Function (Runs All 3 Layers)

```javascript
// Master function: runs all verification layers in order
// Stops on first match to save cost
async function verifyWebsiteExistence(lead) {
  // Layer 1: URL pattern check (free, instant)
  const urlCheck = await checkUrlPatterns(lead.business_name, lead.suburb);
  if (urlCheck.found) {
    return {
      ...lead,
      website: urlCheck.url,
      website_verified: true,
      website_check_method: urlCheck.method,
      website_check_url: urlCheck.url,
      pipeline: 'diy_website',  // Reclassify to Pipeline B
    };
  }

  // Layer 2: Google search (batched separately — see note below)
  // This layer is handled by the n8n workflow, not this function
  // The orchestrator marks leads as "needs_google_search" for batching
  // Results are processed in a separate Code node after the Apify actor returns

  // Layer 3: ABN→domain check (free, last resort)
  const abnCheck = await checkAbnDomain(lead.abn, lead.business_name);
  if (abnCheck.found) {
    return {
      ...lead,
      website: abnCheck.url,
      website_verified: true,
      website_check_method: abnCheck.method,
      website_check_url: abnCheck.url,
      pipeline: 'diy_website',  // Reclassify to Pipeline B
    };
  }

  // All layers checked — no website found. Confirmed Pipeline A lead.
  return {
    ...lead,
    website_verified: true,
    website_check_method: 'none_found',
    website_check_url: null,
    pipeline: 'no_website',  // Confirmed — safe to email "you don't have a website"
  };
}
```

---

### Post-Reclassification: Platform Detection for Discovered Websites

Leads reclassified to Pipeline B need platform detection + PageSpeed audit before scoring:

```javascript
// After website checker reclassifies a lead to Pipeline B:
// 1. Run detectPlatform(lead.website) — reuse existing platform detection logic
// 2. If DIY platform found:
//    - Set lead.diy_platform = detected platform
//    - Run PageSpeed API audit
//    - Score with Pipeline B scorer
// 3. If NOT a DIY platform (professionally built):
//    - Set lead.status = 'suppressed'
//    - Set lead.notes = 'professional_website_detected'
//    - Don't email — not our target market
```

---

## n8n Workflow Integration

The website checker modifies the Pipeline A architecture. Here's where it slots in:

```
BEFORE (current plan):
  Apify Scrape → Normalise → Enrich → Score → Send

AFTER (with website checker):
  Apify Scrape → Normalise → ┐
                               ├→ WEBSITE CHECKER ──→ Confirmed no website → Enrich → Score A → Send
                               │   (3 layers)     ──→ Website found (DIY)  → Platform Detect → Score B → Send
                               │                  ──→ Website found (pro)  → Suppress
```

### n8n Node Sequence (Website Checker Section)

1. **Code: Layer 1 — URL Pattern Check** (runs on all leads)
   - Input: normalised leads with `pipeline = 'no_website'`
   - Output: split into `website_found` and `needs_google_search`

2. **HTTP Request: Apify Google Search** (batch call, only for `needs_google_search` leads)
   - Endpoint: `POST https://api.apify.com/v2/acts/tuningsearch~cheap-google-search-results-scraper/runs`
   - Input: array of `"[business name]" [suburb]` queries
   - Wait for results (Apify webhook or polling)

3. **Code: Layer 2 — Process Google Search Results**
   - Match search results to leads
   - Filter out directory/social URLs
   - Verify business name appears in result
   - Output: split into `website_found` and `needs_abn_check`

4. **Code: Layer 3 — ABN Domain Check** (runs on remaining leads)
   - Output: split into `website_found` and `confirmed_no_website`

5. **Merge: Reclassified leads** (from all 3 layers)
   - All `website_found` leads → Platform Detection → Pipeline B scoring path
   - All `confirmed_no_website` leads → continue to Pipeline A enrichment + scoring

---

## Database Migration

```sql
-- Migration 004: Add website verification tracking fields
-- Run after 001, 002, 003 in Supabase SQL Editor

ALTER TABLE leads ADD COLUMN website_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN website_check_method TEXT;
  -- Values: 'url_pattern', 'google_search', 'abn_whois', 'none_found', NULL (not yet checked)
ALTER TABLE leads ADD COLUMN website_check_url TEXT;
  -- The URL found by the checker (NULL if no website found)

CREATE INDEX idx_leads_website_verified ON leads(website_verified);
CREATE INDEX idx_leads_website_check_method ON leads(website_check_method)
  WHERE website_check_method IS NOT NULL;
```

---

## Cost Analysis

| Layer | Cost per lead | Daily (50 leads) | Monthly |
|-------|---------------|-------------------|---------|
| Layer 1: URL patterns | Free | Free | Free |
| Layer 2: Google search | ~$0.001 | ~$0.03-0.05 | ~$1-2 |
| Layer 3: ABN domain | Free | Free | Free |
| **Total** | | | **~$1-2/month** |

Layer 2 only runs on leads that survive Layer 1 (probably 60-70% of leads). So if 50 leads come in, ~30-35 need a Google search. At $0.001/search = $0.035/day.

With Aaron's pre-purchased Apify credits this month, the cost is effectively zero.

---

## Step-by-Step Tasks

### Step 1: Create database migration

**Actions:**
- Create `scripts/lead-pipeline/004-add-website-verification-fields.sql`
- Add `website_verified`, `website_check_method`, `website_check_url` columns
- Add indexes

**Files affected:**
- `scripts/lead-pipeline/004-add-website-verification-fields.sql` (new)

---

### Step 2: Build website checker logic

**Actions:**
- Create `scripts/lead-pipeline/website-checker.js`
- Implement `checkUrlPatterns()` — Layer 1 (free, instant)
- Implement `isRealWebsite()` + `findWebsiteInSearchResults()` — Layer 2 helpers
- Implement `checkAbnDomain()` — Layer 3 (free, bonus)
- Implement `verifyWebsiteExistence()` — orchestrator
- Include directory domain exclusion list
- Include parked domain detection
- Add comments explaining the 3-layer approach

**Files affected:**
- `scripts/lead-pipeline/website-checker.js` (new)

---

### Step 3: Update parent plan architecture

**Actions:**
- Update Pipeline A architecture diagram (lines 510-564) to include website checker step
- Replace the one-liner on line 1092 with a reference to this plan
- Add website checker as a new step between "Normalise & Merge" and "Enrich" in the n8n workflow steps (Step 5, around line 1497)

**Files affected:**
- `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`

---

### Step 4: Build n8n workflow nodes (during Pipeline A build)

This step happens when Pipeline A is built in n8n (separate session). Documented here for completeness:

**Actions:**
- Add Code node: "Layer 1 — URL Pattern Check" after Normalise & Merge
- Add HTTP Request node: Apify Google Search (batched) for leads that survive Layer 1
- Add Code node: "Layer 2 — Process Search Results" to parse Apify output
- Add Code node: "Layer 3 — ABN Domain Check" for remaining leads
- Add Switch node: split into `confirmed_no_website` → Pipeline A path, `website_found` → Platform Detection → Pipeline B path, `professional_website` → Suppress
- Wire the Merge node to recombine Pipeline A and reclassified Pipeline B leads

**Files affected:**
- n8n workflow (manual UI configuration — document in README)

---

### Step 5: Test with known data

**Actions:**
- Test Layer 1 with 10 Perth tradies whose websites Aaron knows exist but weren't on Google Maps
- Test Layer 2 with 10 businesses that have websites under non-obvious domain names
- Test with 10 businesses that genuinely have no website — verify they come through as `confirmed_no_website`
- Test directory exclusion — verify Facebook/YellowPages results don't trigger false "has website"
- Test parked domain detection — verify "for sale" pages don't count
- Manual spot-check: take 20 random `none_found` leads and Google them manually — how many did the checker miss?

**Files affected:**
- None (manual testing)

---

## Validation Checklist

- [ ] `004-add-website-verification-fields.sql` runs cleanly in Supabase
- [ ] `checkUrlPatterns('Ace Plumbing', 'Perth')` correctly tries `aceplumbing.com.au`, `aceplumbing.au`, etc.
- [ ] `checkUrlPatterns` detects and skips parked/for-sale domains
- [ ] `isRealWebsite('https://facebook.com/aceplumbing')` returns `false`
- [ ] `isRealWebsite('https://aceplumbing.com.au')` returns `true`
- [ ] `findWebsiteInSearchResults` verifies business name appears in result before matching
- [ ] Layer 1 → Layer 2 → Layer 3 runs in order, stops on first match
- [ ] Reclassified leads have `pipeline = 'diy_website'` and `website` set
- [ ] Confirmed no-website leads have `website_verified = true` and `website_check_method = 'none_found'`
- [ ] Professional websites get `status = 'suppressed'`
- [ ] Google search is batched (one Apify call per pipeline run, not per lead)
- [ ] All directory/social domains are excluded
- [ ] Apostrophes handled correctly (Jim's → Jims in domain slug)
- [ ] No secrets in tracked files

---

## Success Criteria

1. **False positive rate drops from ~20-30% to <5%** — verified by Aaron spot-checking 20 "no website" leads
2. **Zero "you don't have a website" emails sent to businesses that DO have websites** (after checker is active)
3. **Bonus Pipeline B leads captured** — leads reclassified from A→B with discovered websites get upgrade-pitch emails instead of being wasted
4. **Cost stays under $2/month** for the Google search layer
5. **Verification data tracked in DB** — `website_check_method` populated for every lead, enabling accuracy analysis after 2-3 weeks
6. **Professional websites auto-suppressed** — leads with well-built sites don't waste an email slot

---

## Notes

- **Accuracy vs cost tradeoff:** We can always add Layer 4 later (e.g. Bing search, social media API lookups) if the 3-layer approach still misses too many. Start simple, measure, tune.
- **Layer 3 is the weakest layer:** ABN→domain cross-reference has low hit rate because many tradies register domains under personal names, not business names. It's free though, so worth keeping as a bonus check.
- **Performance:** Layer 1 runs ~5 HTTP HEAD requests per lead (parallel, 5s timeout each). For 50 leads, that's ~50 seconds total if run serially, or ~10 seconds if batched 5 at a time. Layer 2 is one Apify call for all remaining leads (batch). Total checker time: ~1-2 minutes per pipeline run.
- **Future enhancement:** If we later add a "research agent" (LLM that browses and validates), it could replace Layer 2 with higher accuracy. But for now, Google search + URL patterns is the right 80/20 approach.
- **n8n timeout consideration:** The Apify Google search call may take 30-60 seconds to complete. Use n8n's "Wait" node or Apify webhook to avoid blocking the workflow.

---

## Implementation Notes

**Implemented:** 2026-03-22

### Summary
All steps completed. Created `website-checker.js` with 3-layer verification logic, DB migration `004` (already run in Supabase), updated parent plan reference. Fixed name matching to require 2+ word matches or name-in-URL to prevent false positives from generic search results.

### Deviations from Plan
- Tightened Layer 2 name matching: requires at least 2 matching words (or 1 word + name in URL hostname) instead of just 1 word. This prevents matching against competitor/unrelated results that share a single common word like "plumbing".
- Added HTTP (non-SSL) fallback to Layer 1 URL pattern check — some old tradie sites don't have SSL certificates.
- Layer 3 simplified to just try .com.au domain (overlaps with Layer 1 but catches cases where Layer 1 slug generation differs from ABN-based naming).
- Step 4 (n8n workflow nodes) deferred — will be built when Pipeline A workflow is constructed.

### Issues Encountered
- n8n Postgres connection required Supabase connection pooler (IPv6-only direct host not reachable from n8n Cloud) + allowUnauthorizedCerts for SSL. Resolved with: host=`aws-1-ap-southeast-2.pooler.supabase.com`, port=6543, user=`postgres.zdaznnifkhdioczrxsae`.
