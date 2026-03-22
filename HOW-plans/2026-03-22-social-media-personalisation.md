# Plan: Advanced Social Media Personalisation for Outreach

**Created:** 2026-03-22
**Status:** Draft
**Type:** Full
**Request:** Scrape leads' recent social media activity (Facebook/Instagram) and feed it into email personalisation for ultra-specific, human-sounding outreach.

---

## Overview

### What This Accomplishes
Adds a social media enrichment step to the lead pipeline that scrapes a business's recent Facebook/Instagram posts and feeds the most interesting one into the email prompt. Instead of generic "saw you don't have a website", Aaron's emails reference specific things: "saw your post about the kitchen reno in Applecross, the client looked stoked". This makes cold emails feel like they came from someone who actually follows the business, not a bot.

### Why This Matters
- **Reply rates:** Generic cold emails get 1-3% reply rates. Hyper-personalised ones get 8-15%. The difference is whether it feels like a real person wrote it.
- **Credibility:** When Aaron cold calls and the lead says "yeah I got your email", referencing a specific post proves he actually looked at their business. Instant trust.
- **Competitive moat:** No other agency in Perth (or Australia) is doing this level of automated personalisation. It's the kind of thing that makes people screenshot the email and share it.

---

## Current State

### Relevant Existing Structure
- **Google Maps scraper:** Returns `website` field — sometimes this IS a Facebook URL (flagged as `website_is_facebook: true`). Does NOT return separate social media links.
- **Filter & Normalise:** Extracts basic lead data. Now includes `top_reviewer_name` and `second_reviewer_name` for review name-dropping.
- **Build Prompt A/B → OpenAI HTTP → Parse:** 3-node architecture. Social data slots into Build Prompt's `leadContext`.
- **Apify budget:** $30/mo. Currently most of this goes to Google Maps scraper.
- **Pipeline flow:** Apify → Filter → Website Checker → Scorer → Tag → Build Prompt → OpenAI → Parse → Log

### Gaps Being Addressed
1. No social media URLs extracted from any source
2. No scraping of recent posts/activity
3. Email personalisation relies only on reviews, suburb, and category — all static data
4. No "what have they been up to lately" signal

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/lead-pipeline/social-enricher.js` | n8n Code node: extracts Facebook/Instagram URLs from lead data, calls Apify to scrape recent posts |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| n8n workflow — Filter & Normalise (both) | Extract Facebook/Instagram URLs from Google Maps `website` field and any social links in raw data |
| n8n workflow — new "Social Enricher" HTTP Request node | Calls Apify Facebook/Instagram scraper for each lead with a social profile |
| n8n workflow — new "Parse Social Data" Code node | Extracts best recent post from Apify response |
| n8n workflow — Build Email Prompt A/B | Add social context fields to lead context passed to OpenAI |
| n8n workflow — connections | Insert social enrichment between Website Checker and Lead Scorer |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — enhances the existing email personalisation pipeline, which is core scope.
- **Decision required:** None.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Apify | `APIFY_API_TOKEN` | Present |
| Apify Facebook Scraper | Uses same token | No new vars needed |

---

## Skills to Use

None.

---

## Design Decisions

### 1. Scrape Facebook only (not Instagram) to start
**Rationale:** Facebook Pages are public and Apify has mature, cheap scrapers for them. Instagram requires login-based scraping (more expensive, rate-limited, breaks more often). Most small Australian businesses have a Facebook page. Instagram can be added later as a v2.

### 2. Use Apify's `apify/facebook-posts-scraper` actor (not the full page scraper)
**Rationale:** We only need recent posts, not the full page profile. The posts scraper is cheaper per run and returns exactly what we need: post text, date, engagement (likes/comments), and any images.

### 3. Only scrape social for leads scoring 5+ (pre-filter)
**Rationale:** Social scraping costs compute units. Scraping 500 leads' Facebook pages would blow the budget. Instead, only scrape the top leads (score 5+) that are actually worth personalising. This might be 20-50 leads per run, not 500.

### 4. Insert social enrichment AFTER scoring, BEFORE email prompt
**Rationale:** Score first (cheap, instant), then only spend Apify credits on leads worth emailing. The flow becomes:
```
Scorer → Tag (score 5+) → Social Enricher → Build Prompt → OpenAI → Parse → Log
```

### 5. Graceful fallback: no social = use existing personalisation
**Rationale:** Many businesses won't have Facebook pages, or their pages will be dormant. The Build Prompt node checks if social data exists — if yes, uses it. If no, falls back to reviewer name-dropping and standard context. No lead is skipped because of missing social data.

### 6. Extract the "most interesting" post, not just the most recent
**Rationale:** The most recent post might be "We're closed for Australia Day". We want the post with the most engagement (likes + comments) from the last 30 days. If no posts in 30 days, fall back to most recent post regardless of date.

### 7. Store social data in Supabase for reuse
**Rationale:** If the same business appears in future scrapes (e.g., re-scraping a region after cooldown), don't re-scrape their social. Check Supabase first, only scrape if no social data or data is >30 days old.

### Alternatives Considered

**Instagram scraping:** Rejected for v1. Apify Instagram scrapers require proxy rotation, are more expensive ($0.50-1.00 per profile vs $0.05-0.10 for Facebook), and break more often due to Meta's anti-scraping. Facebook is the better starting point for Australian small businesses.

**Google Search for social profiles:** Could Google "[business name] [suburb] facebook" to find their page URL. Cheaper than Apify but less reliable. Could be a good Layer 1 (free search) before Layer 2 (Apify scrape). Worth considering as enhancement.

**Manual social lookup:** Too slow for 100+ leads/day. The whole point is automation.

### Open Questions

1. **Which Apify Facebook actor is cheapest/most reliable?** Options: `apify/facebook-posts-scraper`, `apify/facebook-pages-scraper`, `microworlds/facebook-page-post-scraper`. Need to compare cost per run. — *Can test during implementation.*
2. **Should we also extract the business's Facebook "About" description?** This often has info not in Google Maps (services offered, years in business, awards). — *Recommend: yes, cheap and useful.*
3. **Photo/image posts vs text posts:** Some businesses only post photos with no text (e.g., before/after shots). Should we describe the image in the prompt or skip imageless posts? — *Recommend: skip for v1, mention "saw your recent photos" generically if only image posts exist.*

---

## Step-by-Step Tasks

### Step 1: Add social URL extraction to Filter & Normalise

Extract Facebook and Instagram URLs from the Google Maps scraper data. The `website` field sometimes contains a Facebook URL. Some Apify Google Maps actors also return a `socialMedia` or `links` field.

**Actions:**
- Check if `website` contains `facebook.com` → extract as `facebook_url`
- Check if `website` contains `instagram.com` → extract as `instagram_url`
- Check raw scraper output for any `socialMedia`, `socialProfiles`, or `links` fields
- Pass these URLs through the pipeline

**Fields added to lead:**
```javascript
facebook_url: 'https://facebook.com/businesspage' || null
instagram_url: 'https://instagram.com/businesshandle' || null
has_social_profile: true/false
```

**Files affected:**
- n8n workflow: Filter & Normalise (both Pipeline A and B)

---

### Step 2: Add Supabase columns for social data

Add social media fields to the leads table.

**Actions:**
- Write migration `007-add-social-fields.sql`
- Run against Supabase pipeline DB

**Schema:**
```sql
ALTER TABLE leads ADD COLUMN IF NOT EXISTS facebook_url TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_url TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS social_best_post TEXT;       -- Best recent post text (truncated)
ALTER TABLE leads ADD COLUMN IF NOT EXISTS social_post_date TEXT;       -- When the post was made
ALTER TABLE leads ADD COLUMN IF NOT EXISTS social_post_engagement INT;  -- likes + comments
ALTER TABLE leads ADD COLUMN IF NOT EXISTS social_about TEXT;           -- Facebook "About" text
ALTER TABLE leads ADD COLUMN IF NOT EXISTS social_scraped_at TIMESTAMPTZ;
```

**Files affected:**
- `scripts/lead-pipeline/007-add-social-fields.sql` (new)

---

### Step 3: Build social enricher — find Facebook URL

For leads without a direct Facebook URL, try to find one via Google search.

**Actions:**
- New Code node: "Find Social Profile" (runOnceForEachItem)
- Logic:
  1. If `facebook_url` already set → pass through
  2. If not → try URL pattern: `facebook.com/[businessname-slug]`
  3. Quick HEAD request to check if it exists
  4. If found → set `facebook_url`
  5. If not found → mark `has_social_profile: false`, skip social scraping

**Files affected:**
- n8n workflow: new "Find Social Profile" Code node

---

### Step 4: Build social scraper — Apify Facebook Posts

HTTP Request node that calls Apify to scrape recent Facebook posts for leads with a Facebook URL.

**Actions:**
- New HTTP Request node: "Scrape Facebook Posts"
- Calls Apify Facebook posts scraper actor (run-sync-get-dataset-items)
- Input: `facebook_url` from previous node
- Parameters: `maxPosts: 5`, date range: last 30 days
- Output: array of posts with text, date, engagement

**Configuration:**
```json
{
  "startUrls": [{ "url": "{{ $json.facebook_url }}" }],
  "maxPosts": 5,
  "resultsType": "posts"
}
```

**Timeout handling:** 30-second timeout per request. If Apify is slow, skip social data for this lead.

**Files affected:**
- n8n workflow: new "Scrape Facebook Posts" HTTP Request node

---

### Step 5: Parse social data — extract best post

Code node that picks the most interesting post from the Apify response.

**Actions:**
- New Code node: "Parse Social Data" (runOnceForEachItem)
- Logic:
  1. Get posts from Apify response
  2. Filter to last 30 days
  3. Sort by engagement (likes + comments)
  4. Take the top post
  5. Extract: post text (first 200 chars), date, engagement count
  6. Also extract Facebook "About" section if returned
  7. Merge with lead data from upstream node

**Output fields added:**
```javascript
social_best_post: "Just finished this kitchen reno in Applecross..."
social_post_date: "2026-03-15"
social_post_engagement: 47  // likes + comments
social_about: "Family-owned plumbing business since 2015"
social_scraped_at: "2026-03-22T..."
```

**Files affected:**
- n8n workflow: new "Parse Social Data" Code node

---

### Step 6: Update Build Prompt A/B to include social context

Add social data to the lead context passed to OpenAI.

**Actions:**
- Add to `buildLeadContext()`:
```javascript
if (lead.social_best_post) {
  parts.push(`Recent Facebook post (${lead.social_post_date}): "${lead.social_best_post}"`);
  parts.push(`Post engagement: ${lead.social_post_engagement} likes/comments`);
}
if (lead.social_about) {
  parts.push(`Facebook About: "${lead.social_about.substring(0, 150)}"`);
}
```

- Add new variant to VARIANTS array:
```javascript
{
  name: 'social_activity',
  instruction: 'Reference their most recent Facebook post specifically. Mention what it was about, who was in it, or what they were doing. Make it sound like you follow their page. If they posted about a job they did, comment on it naturally.'
}
```

- Update system prompt to include social personalisation guidance:
```
If social media post data is provided, USE IT. Reference the specific post naturally.
Examples of good social references:
- "saw your post about the kitchen reno in Applecross, looked mint"
- "that pop-up at the gallery looked like a good turnout"
- "looks like [customer name] was stoked with that job you did"
Don't say "I saw on your Facebook" — just reference the content naturally as if you came across it.
```

**Files affected:**
- n8n workflow: Build Email Prompt A, Build Email Prompt B

---

### Step 7: Wire up the new nodes in n8n

Connect the social enrichment nodes into the pipeline.

**New Pipeline A flow:**
```
Scorer A → Tag & Pass (score 5+) → Find Social Profile → Scrape Facebook Posts → Parse Social Data → Build Prompt A → OpenAI → Parse A → Log
```

**New Pipeline B flow:**
```
Scorer B → Tag & Pass B (score 5+) → Find Social Profile B → Scrape Facebook Posts B → Parse Social Data B → Build Prompt B → OpenAI → Parse B → Log
```

**Actions:**
- Update connections via n8n API
- Position new nodes between Tag and Build Prompt
- Ensure leads without social data still flow through (continueOnFail on scraper node)

**Files affected:**
- n8n workflow: connections object
- `scripts/deploy-social-enricher.py` (new deployment script)

---

### Step 8: Update Supabase: Store Leads to include social fields

Add social data fields to the store node.

**Actions:**
- Add to row object:
```javascript
facebook_url: lead.facebook_url || null,
instagram_url: lead.instagram_url || null,
social_best_post: lead.social_best_post || null,
social_post_date: lead.social_post_date || null,
social_post_engagement: lead.social_post_engagement || null,
social_about: lead.social_about || null,
social_scraped_at: lead.social_scraped_at || null,
```

**Files affected:**
- n8n workflow: Supabase: Store Leads node

---

### Step 9: Budget guardrails

Prevent social scraping from blowing the Apify budget.

**Actions:**
- Add a daily scrape counter in the social enricher
- Max 50 social scrapes per day (well within $30/mo budget)
- If counter exceeded, skip social enrichment, use fallback personalisation
- Log skipped scrapes for monitoring

**Files affected:**
- n8n workflow: Find Social Profile node (adds counter logic)

---

### Step 10: Test and validate

**Actions:**
- Run pipeline manually with 10 test leads
- Verify social URLs are extracted correctly
- Verify Apify scraper returns post data
- Verify OpenAI generates emails referencing specific posts
- Check Apify cost per scrape to validate budget assumptions
- Update learnings-register.md with any gotchas

**Files affected:**
- `learnings-register.md`
- `context/WHERE-current-data.md`

---

## Validation Checklist

- [ ] Social URLs extracted from Google Maps data where available
- [ ] Facebook posts scraped via Apify for scored leads (5+)
- [ ] Best post selected by engagement, not just recency
- [ ] OpenAI references specific post content in generated emails
- [ ] Leads without social profiles still get personalised emails (fallback works)
- [ ] Apify budget stays within $30/mo (daily scrape cap enforced)
- [ ] Social data stored in Supabase for reuse
- [ ] No timeouts (all scraping via HTTP Request nodes, not Code nodes)
- [ ] Em dashes still stripped from output
- [ ] No "Mycelium AI" in any output
- [ ] CLAUDE.md updated if structure changed
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. **At least 30% of scored leads get social-enriched emails** (i.e., reference a specific Facebook post)
2. **Emails referencing social activity are indistinguishable from manually written ones** — no "I noticed on your Facebook page" corporate language
3. **Apify social scraping costs < $10/mo** within the existing $30 budget
4. **No pipeline timeouts** — social scraping uses HTTP Request nodes, not Code nodes
5. **Fallback is seamless** — leads without social data get reviewer name-dropping or standard personalisation, not empty/broken emails

---

## Notes

- **v2 enhancement — Instagram:** Once Facebook scraping is proven, add Instagram. Apify Instagram scrapers are more expensive (~10x) but Instagram is where younger business owners post. Could target specific industries (cafes, salons, fitness) where Instagram is primary.
- **v2 enhancement — Google search discovery:** Before calling Apify, do a free Google search for "[business name] [suburb] facebook" to find their page URL. This is cheaper than Apify and catches businesses whose Facebook URL isn't in Google Maps.
- **v2 enhancement — A/B test social vs non-social:** Track which emails get replies. If social-enriched emails outperform, the system can automatically prioritise leads with social profiles (score boost). This connects to Aaron's request for the system to "double down on what's working".
- **v2 enhancement — Image description:** For businesses that post photos without text (tradies love before/after shots), use GPT-4o's vision to describe the image and generate personalisation from it. E.g., "saw that bathroom reno you posted, the tiling looked clean".
- **Privacy note:** All scraped data is publicly available Facebook posts. No private profiles, no login-wall content, no DMs. This is the same data anyone could see by visiting their Facebook page.
