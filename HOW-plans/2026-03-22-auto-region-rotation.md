# Plan: Auto-Region Rotation System

**Created:** 2026-03-22
**Status:** Draft
**Type:** Full
**Request:** Build a system that automatically rotates through Australian regions, scraping new leads daily, ensuring no duplicates, and prioritising regional/suburban areas over CBDs.

---

## Overview

### What This Accomplishes
The lead pipeline currently only searches "Perth, Western Australia". This plan adds a **region queue** in Supabase that the n8n workflow reads each morning — it picks the next region to scrape, runs the full pipeline (scrape → score → personalise → store), marks the region as done, and moves on. When Perth is exhausted, it automatically starts hitting Mandurah, Bunbury, Geraldton, then expands to Melbourne suburbs, Brisbane, Adelaide, and beyond — all without manual intervention.

### Why This Matters
- **Scale:** 65 categories × 50 results × 1 region = ~3,250 leads per run. Rotating through 200+ regions means 600,000+ potential leads across Australia.
- **No duplicates:** Supabase UNIQUE constraints + region tracking means the same business never gets scraped or contacted twice.
- **Regional priority:** Aaron's insight — businesses in residential/suburban postcodes are owner-operated and convert better. Regional towns (Karratha, Dubbo, Toowoomba) are goldmines because they're underserved by agencies.
- **100+/day target:** With auto-rotation, the pipeline can produce 100+ fresh scored leads daily without running out.

---

## Current State

### Relevant Existing Structure
- **Apify node:** Hardcoded to `"Perth, Western Australia"` with 65 search categories
- **leads table:** Has `suburb`, `postcode`, `state` columns but `state` defaults to `'WA'`
- **Dedup:** UNIQUE on phone, UNIQUE on ABN, fallback UNIQUE on `lower(business_name) + lower(suburb)`
- **Postcode classifier:** Perth-specific (6000-6999 range, 26 commercial/industrial postcodes)
- **ABR script:** Filters `state='WA'` only
- **Email personaliser:** System prompt says "Aaron, a web designer in Perth, Western Australia"
- **Address type classification:** Only works for Perth postcodes

### Gaps Being Addressed
1. No region tracking — can't tell what's been scraped
2. No auto-rotation — everything is hardcoded to Perth
3. Postcode classifier is Perth-only — can't score residential/commercial outside 6000-6999
4. Email personaliser references Perth specifically — sounds wrong for Melbourne leads
5. No way to know when a region is "exhausted"
6. ABR script only queries WA businesses

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/lead-pipeline/005-add-region-tables.sql` | Supabase migration: `regions` queue table + `region` column on leads |
| `scripts/lead-pipeline/006-seed-regions.sql` | Seed 200+ Australian regions with priority ordering |
| `scripts/lead-pipeline/region-picker.js` | n8n Code node: queries Supabase for next region to scrape |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| n8n workflow (via API) | Replace hardcoded Apify search with dynamic region from region-picker |
| n8n workflow — Filter & Normalise | Use region's state instead of hardcoded 'WA' |
| n8n workflow — AI Email Personaliser (A+B) | Make location dynamic in system prompt |
| n8n workflow — Supabase: Store Leads | Include `region` field when storing |
| `scripts/lead-pipeline/abr-query.py` | Parameterise state filter (WA → any state) |
| `scripts/lead-pipeline/postcode-classifier.js` | Replace Perth-only map with national classification |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — the pipeline plan (`HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` line 2002) lists "Multi-city expansion" as a planned enhancement. Auto-region rotation is the implementation of that.
- **Decision required:** None — this extends existing scope, doesn't change WHAT we're delivering.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Supabase | `SUPABASE_URL`, `SUPABASE_ANON_KEY` | Present |
| Apify | `APIFY_API_TOKEN` | Present |
| OpenAI | `OPENAI_API_KEY` | Present (just renewed) |
| n8n API | `N8N_API_KEY`, `N8N_API_URL` | Present |

No new env vars needed.

---

## Skills to Use

None — this is pure infrastructure work (SQL + n8n Code nodes + Python script updates).

---

## Design Decisions

### 1. Region = a Google Maps search location, not a postcode
**Rationale:** Apify's `locationQuery` field accepts natural language like "Mandurah, Western Australia" or "Toowoomba, Queensland". This is the unit of rotation — not individual postcodes (too granular) or states (too broad). Each region maps to roughly one town/city or metro sub-region.

### 2. Single workflow with dynamic region, not per-region workflows
**Rationale:** Aaron prefers one consolidated workflow. The region-picker node runs first, fetches the next region, and passes it downstream. All other nodes read the region from the item data. No workflow duplication.

### 3. National postcode classifier using ranges, not lookup tables
**Rationale:** Australian postcodes follow predictable state-based ranges (2000-2999 NSW, 3000-3999 VIC, 4000-4999 QLD, 5000-5999 SA, 6000-6999 WA, 7000-7999 TAS, 0800-0899 NT, 2600-2619 ACT). CBD postcodes for each capital are well-known (Sydney 2000, Melbourne 3000, Brisbane 4000, etc.). Everything else defaults to residential. This is the same 80/20 approach as the Perth classifier — just national.

### 4. Region priority: WA first, then regional Australia, then metro
**Rationale:** Aaron is Perth-based — WA leads are warmest (local, same timezone, can meet in person). Regional towns second (underserved, owner-operated, high conversion). Metro last (competitive, harder to win).

### 5. "Exhausted" = all categories scraped with <5 new leads found
**Rationale:** A region is exhausted when a full scrape across all 65 categories returns fewer than 5 leads that aren't already in Supabase. The region gets marked `exhausted` and won't be picked again until a cooldown period (90 days — new businesses register constantly).

### 6. Email personaliser uses region context dynamically
**Rationale:** Instead of "Aaron, a web designer in Perth", the prompt says "Aaron, a web designer based in Perth who works with businesses across Australia". The lead's suburb/city is already used in the email body — no change needed there.

### Alternatives Considered

**Per-state workflows:** Rejected — creates maintenance burden, violates Aaron's preference for consolidated workflows.

**Postcode-level rotation:** Rejected — too granular. 2,500+ postcodes in Australia. Region-level (200-300 regions) is the right granularity.

**Separate Instantly campaigns per region:** Not needed — Instantly handles sender rotation across all leads regardless of location. One campaign, many regions.

### Open Questions

1. **Email sending limit:** How many emails/day can Instantly handle once warmup is done? This caps how many leads/day we actually outreach (scraping 100/day is useless if we can only send 30 emails/day). — *Can check Instantly plan limits.*
2. **Apify budget:** 65 categories × 50 results per region = one big API call. At $30/mo cap, how many regions can we scrape per month? — *Need to check Apify pricing per run.*
3. **Do we want to personalise by state?** E.g., different email tone for a Melbourne cafe vs a Karratha plumber? Or keep it generic "Australian businesses"? — *Recommend: keep it generic for now, personalise by lead data not region.*

---

## Step-by-Step Tasks

### Step 1: Create `regions` table in Supabase

Add a region queue table that tracks scraping progress.

**Actions:**
- Write migration `005-add-region-tables.sql`
- Add `region` column to existing `leads` table
- Run migration against Supabase pipeline DB

**Schema:**

```sql
-- Region queue for auto-rotation
CREATE TABLE regions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,                    -- "Mandurah, Western Australia"
  state TEXT NOT NULL,                   -- "WA", "VIC", "NSW", etc.
  priority INT NOT NULL DEFAULT 50,      -- Lower = higher priority (WA=10, regional=20, metro=40)
  status TEXT NOT NULL DEFAULT 'pending', -- pending, in_progress, scraped, exhausted, cooldown
  last_scraped_at TIMESTAMPTZ,
  leads_found INT DEFAULT 0,
  new_leads_found INT DEFAULT 0,         -- Leads that weren't already in DB
  scrape_count INT DEFAULT 0,            -- How many times this region has been scraped
  cooldown_until TIMESTAMPTZ,            -- Don't re-scrape until this date
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(name)
);

-- Index for the region picker query
CREATE INDEX idx_regions_next ON regions (priority, status, cooldown_until);

-- Add region to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS region TEXT;
```

**Files affected:**
- `scripts/lead-pipeline/005-add-region-tables.sql` (new)

---

### Step 2: Seed Australian regions with priority ordering

Populate the regions table with 200+ Australian regions, prioritised.

**Actions:**
- Write seed SQL `006-seed-regions.sql`
- Priority tiers:
  - **Tier 1 (priority 10):** Perth metro sub-regions — "Perth CBD", "Fremantle", "Joondalup", "Rockingham", "Midland", "Armadale", "Wanneroo", "Stirling"
  - **Tier 2 (priority 15):** WA regional — "Mandurah", "Bunbury", "Geraldton", "Kalgoorlie", "Albany", "Broome", "Karratha", "Port Hedland", "Busselton", "Esperance"
  - **Tier 3 (priority 20):** Regional Australia (goldmine) — "Toowoomba QLD", "Bendigo VIC", "Ballarat VIC", "Cairns QLD", "Townsville QLD", "Launceston TAS", "Orange NSW", "Wagga Wagga NSW", "Albury NSW", "Shepparton VIC", "Mackay QLD", "Rockhampton QLD", "Gladstone QLD", "Tamworth NSW", "Dubbo NSW", "Bathurst NSW", "Mildura VIC", "Warrnambool VIC", etc.
  - **Tier 4 (priority 30):** Outer metro — "Geelong VIC", "Wollongong NSW", "Newcastle NSW", "Gold Coast QLD", "Sunshine Coast QLD", "Central Coast NSW", "Ipswich QLD", "Logan QLD"
  - **Tier 5 (priority 40):** Capital city metros — "Melbourne VIC", "Sydney NSW", "Brisbane QLD", "Adelaide SA", "Hobart TAS", "Darwin NT", "Canberra ACT"

**Files affected:**
- `scripts/lead-pipeline/006-seed-regions.sql` (new)

---

### Step 3: Build region-picker n8n Code node

New Code node that runs FIRST in the pipeline — queries Supabase for the next region to scrape.

**Actions:**
- Write `region-picker.js` Code node logic
- Query: `SELECT * FROM regions WHERE status IN ('pending', 'scraped') AND (cooldown_until IS NULL OR cooldown_until < NOW()) ORDER BY priority ASC, last_scraped_at ASC NULLS FIRST LIMIT 1`
- Mark region as `in_progress` immediately (prevents double-picks if workflow runs twice)
- Output: region name, state, priority — passed to all downstream nodes

**Logic:**
```
1. Query Supabase for next available region
2. If none available: return empty (skip pipeline run)
3. Mark region as in_progress
4. Pass region data downstream: { region_name, region_state, location_query }
```

**Files affected:**
- `scripts/lead-pipeline/region-picker.js` (new)
- n8n workflow: new node before Apify, connected to trigger

---

### Step 4: Make Apify node dynamic

Replace hardcoded `"Perth, Western Australia"` with the region from region-picker.

**Actions:**
- Change Apify HTTP Request node from static JSON body to expression-based
- `locationQuery` reads from `{{ $json.location_query }}` (output of region-picker)
- Search strings stay the same 65 categories but append the region: `"plumber {{ $json.region_name }}"` instead of `"plumber Perth WA"`
- Update via n8n API (Python script)

**Files affected:**
- n8n workflow: `Apify: Google Maps (No Website)` node

---

### Step 5: Update Filter & Normalise to use dynamic state

Currently hardcodes `state: 'WA'`. Change to use the region's state.

**Actions:**
- Read state from the region data passed through the pipeline
- Update both `Filter & Normalise` and `Filter & Normalise (Has Website)` nodes

**Files affected:**
- n8n workflow: both Filter & Normalise nodes

---

### Step 6: National postcode classifier

Replace Perth-only postcode classification with national version.

**Actions:**
- Define CBD postcodes for all capitals:
  - Sydney: 2000, 2001
  - Melbourne: 3000, 3001
  - Brisbane: 4000, 4001
  - Perth: 6000, 6001, 6003, 6004, 6005
  - Adelaide: 5000, 5001
  - Hobart: 7000, 7001
  - Darwin: 0800, 0801
  - Canberra: 2600, 2601
- Define known commercial/industrial zones per state (extend current Perth list)
- Default: everything else = residential (same 80/20 approach)
- Update both n8n Code nodes (Lead Scorer A, Lead Scorer B) and `postcode-classifier.js`

**Files affected:**
- n8n workflow: Lead Scorer A, Lead Scorer B (inline postcode classification)
- `scripts/lead-pipeline/postcode-classifier.js`

---

### Step 7: Update email personaliser for national context

Remove hardcoded "Perth" from system prompts. Make location dynamic.

**Actions:**
- Change: "Aaron, a web designer in Perth, Western Australia" → "Aaron, a web designer based in Perth who works with businesses across Australia"
- The lead's suburb is already injected into the user prompt via `buildLeadContext()` — no change needed there
- The email will naturally reference the lead's location (e.g., "Found your business in Toowoomba") because the lead data includes suburb

**Files affected:**
- n8n workflow: AI Email Personaliser (Pipeline A), AI Email Personaliser1 (Pipeline B)

---

### Step 8: Update Supabase: Store Leads to include region

Add `region` field to the stored lead data.

**Actions:**
- Pass region name through the pipeline to the store node
- Add `region: lead.region || null` to the row object

**Files affected:**
- n8n workflow: Supabase: Store Leads node

---

### Step 9: Add region completion logic

After the pipeline run, update the region's stats and status.

**Actions:**
- New Code node at the end of the pipeline (after Log Pipeline Run)
- Counts: total leads found, new leads stored (non-duplicates)
- Updates region: `leads_found += count`, `new_leads_found = new_count`, `last_scraped_at = NOW()`
- If `new_leads_found < 5`: mark region as `exhausted`, set `cooldown_until = NOW() + 90 days`
- Otherwise: mark as `scraped` (can be re-scraped later for new businesses)

**Files affected:**
- n8n workflow: new "Update Region Status" Code node

---

### Step 10: Update ABR script for multi-state

Parameterise the ABR query to support any Australian state.

**Actions:**
- Add `--state` CLI argument (default: all states)
- Remove Perth postcode filter (6000-6999) — accept all Australian postcodes
- Use national postcode classifier
- The n8n Execute Command node passes the region's state

**Files affected:**
- `scripts/lead-pipeline/abr-query.py`

---

### Step 11: Deploy all changes via Python update script

Single script that pushes all n8n workflow changes.

**Actions:**
- Write `scripts/deploy-region-rotation.py`
- Reads current workflow, updates all affected nodes, pushes via API
- Runs migrations against Supabase
- Tests region-picker with a dry run

**Files affected:**
- `scripts/deploy-region-rotation.py` (new)

---

### Step 12: Update context files

**Actions:**
- Update `context/WHERE-current-data.md` with region rotation status
- Update `learnings-register.md` if learnings emerge during implementation
- Update `CLAUDE.md` Active Projects section

**Files affected:**
- `context/WHERE-current-data.md`
- `CLAUDE.md`

---

## Validation Checklist

- [ ] `regions` table created in Supabase with 200+ seeded regions
- [ ] `leads` table has `region` column
- [ ] Region picker returns correct next region (priority order, skips exhausted)
- [ ] Apify search uses dynamic region (not hardcoded Perth)
- [ ] Filter & Normalise uses dynamic state
- [ ] Postcode classifier works for all Australian states
- [ ] Email personaliser doesn't mention Perth for non-Perth leads
- [ ] Supabase stores `region` on each lead
- [ ] Region status updates correctly after pipeline run
- [ ] Exhausted regions get 90-day cooldown
- [ ] No duplicate leads across regions (phone/ABN/name+suburb unique constraints)
- [ ] ABR script supports multi-state queries
- [ ] CLAUDE.md updated if structure changed
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. **Pipeline runs daily and automatically picks the next region** — no manual intervention
2. **Perth runs first** (priority 10), then WA regional, then national — correct ordering
3. **Zero duplicate leads** — same business in overlapping regions only stored once
4. **Region exhaustion works** — when a region returns <5 new leads, it's marked exhausted with 90-day cooldown
5. **100+ leads/day achievable** — with 65 categories × 50 results, each region run produces enough leads
6. **Emails sound natural for any location** — no "Perth" references in Toowoomba leads

---

## Notes

- **Email warmup is the real bottleneck:** The pipeline can scrape 3,000+ leads per region, but Instantly can only send ~50-100 emails/day per warmed account. With 3 accounts warming (target ready ~2026-04-17), that's 150-300 sends/day. Scraping will outpace sending — which is fine. Build the lead database now, send when ready.
- **Apify budget consideration:** Each region scrape costs compute units. With 65 categories × 50 max results, a single region run might cost $1-3. At $30/mo cap, that's ~10-15 regions per month. If we need more, bump the budget.
- **Future enhancement — parallel region scraping:** Once budget allows, run 2-3 regions per day instead of 1. The architecture supports this (region picker just picks the next N regions).
- **Future enhancement — smart re-scraping:** Instead of blanket 90-day cooldown, track new business registration rates per region (via ABR) and re-scrape regions with high registration activity more frequently.
