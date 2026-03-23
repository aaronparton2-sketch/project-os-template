# Plan: Multi-Source Lead Pipeline — 4 Sources, 100 Leads/Day, Smart Digest

**Created:** 2026-03-23
**Status:** Implemented
**Type:** Full
**Request:** Connect all 4 lead sources (Google Maps, HiPages, ABR, DIY websites) with percentage-based daily allocation targeting 100 leads/day. Overhaul daily digest with source splits, call numbers, spreadsheet links, and reply analytics.

---

## Overview

### What This Accomplishes

Transforms the pipeline from a single-source system (Google Maps only) into a 4-source machine that pulls from Google Maps (no website), HiPages (trades not on Google), ABR (fresh registrations), and Google Maps (DIY websites) — with a Source Allocator controlling the daily mix. The daily digest becomes a proper command centre: source breakdown, region map, phone numbers for cold calling, links to call scripts, and live reply analytics with improvement suggestions.

### Why This Matters

Every cold outreach agency scrapes Google Maps. That's table stakes. Pulling from HiPages catches businesses that never bothered with Google. ABR catches them the week they register. DIY website leads are businesses that tried but failed online. Each source has different conversion characteristics — tracking which one works best gives Aaron a data-driven edge. Targeting 100 leads/day across mixed sources is Hormozi's Rule of 100 applied to outbound.

---

## Current State

### Relevant Existing Structure

| Component | Status | What Exists |
|-----------|--------|-------------|
| **Pipeline A (Google Maps, no website)** | Fully working | Region Picker → Apify → Filter → Website Checker → Scorer → Social → Personalise → Store. 51 nodes. |
| **Pipeline B (DIY websites)** | 60% complete | All processing nodes wired (Platform Detector → PageSpeed → Scorer B → Personaliser B). **Missing: Apify scraper to feed it data.** Trigger exists but is orphaned. |
| **ABR** | Script exists | `scripts/lead-pipeline/abr-query.py` — queries ABR API, returns JSON. **Not wired into n8n.** |
| **HiPages** | Not started | Mentioned in master plan. No scraper, no nodes. |
| **Daily digest** | Basic | `Build HTML Digest` node exists. Shows lead count + priority list. No source splits, no analytics. |
| **Source Allocator** | Doesn't exist | No concept of multi-source orchestration yet. |

### Gaps Being Addressed

1. **Single source dependency** — only Google Maps is feeding leads. HiPages, ABR, and Pipeline B are planned but disconnected.
2. **No source-level tracking** — can't compare which source produces better leads.
3. **Daily digest is bare** — no phone numbers, no spreadsheet links, no reply analytics, no suggestions.
4. **Pipeline B has no data source** — 9 processing nodes wired but nothing feeding them.
5. **No daily volume target** — pipeline processes whatever comes in rather than targeting a specific number.

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/deploy-multi-source.py` | Main deploy script — adds Source Allocator, HiPages scraper, ABR node, Pipeline B scraper, upgraded digest |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| n8n workflow (via deploy script) | Add ~12 new nodes: Source Allocator, HiPages scraper, ABR query, Pipeline B Apify scraper, Merge Results, upgraded Daily Digest |
| `context/WHERE-current-data.md` | Update with multi-source status |
| `context/outstanding-actions.md` | Update action items |
| `learnings-register.md` | Log any learnings during implementation |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — the master plan (`HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`) explicitly includes HiPages, ABR, and Pipeline B as planned data sources. This is finishing what was scoped.
- **Scope delta:** None.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Apify | `APIFY_API_TOKEN` | Present |
| ABR | `ABR_GUID` | Present |
| Supabase (pipeline) | `SUPABASE_PIPELINE_PROJECT_REF`, `SUPABASE_ACCESS_TOKEN` | Present |
| n8n REST API | `N8N_API_URL`, `N8N_API_KEY` | Present |
| OpenAI | `OPENAI_API_KEY` | Present |
| Google Sheets | `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID` | Present |

No new integrations needed.

---

## Skills to Use

None.

---

## Design Decisions

### 1. Architecture: Source Allocator Pattern

**Decision:** One daily trigger → Source Allocator (Code node) → fan out to 4 parallel sources → Merge → shared scoring/personalisation pipeline.

```
Daily 6am AWST
    ↓
Source Allocator (determines today's mix)
    ↓ (4 parallel branches)
    ├─→ Apify: Google Maps (No Website) ──→ Filter A ──→ Website Checker ──→ Scorer A
    ├─→ Apify: HiPages Trades ──────────→ Filter HiPages ──→ Scorer A
    ├─→ ABR: New Registrations ─────────→ Filter ABR ──→ Scorer A
    └─→ Apify: Google Maps (Has Website) → Filter B ──→ Platform Detector → PageSpeed → Scorer B
    ↓
Merge All Sources
    ↓
Deduplicate (by phone/ABN/place_id)
    ↓
Social Enrichment (existing: Find Social → Scrape FB → Parse)
    ↓
Build Email Prompt (existing: trade lingo, social gating, humour)
    ↓
OpenAI → Parse → Store → Log
```

**Rationale:** The Source Allocator runs first and decides how many leads each source should contribute today based on the percentage split. Each source runs in parallel (faster). All leads merge into one stream before personalisation — this means the trade lingo, social gating, humour A/B, and call scripts all apply regardless of source.

### 2. Percentage Split — Starting Point

**Decision:** Start with this split (tunable — stored in Source Allocator code, easy to change):

| Source | % | Target/Day | Rationale |
|--------|---|-----------|-----------|
| Google Maps (no website) | 30% | ~30 leads | Proven, high volume, keep running |
| HiPages (trades) | 20% | ~20 leads | Untapped source, trades-focused |
| ABR (new registrations) | 20% | ~20 leads | Perfect timing, free API |
| DIY websites (Pipeline B) | 30% | ~30 leads | Different pitch angle, high intent |

**Total target: 100 leads/day.** Source Allocator sets `maxItems` for each scraper dynamically.

**Rationale:** Aaron said "not exact percentages" — this is a starting point. After 2 weeks of data, the weekly digest recommends adjustments based on reply rates per source. The Allocator can also auto-adjust over time (future enhancement).

### 3. HiPages Scraper — Apify Actor

**Decision:** Use Apify's Google Maps scraper with a HiPages URL approach, OR use a dedicated HiPages scraper actor if one exists. If no HiPages actor exists, scrape HiPages directly using Apify's Web Scraper actor.

**Research needed during implementation:** Check Apify actor marketplace for "HiPages" or "hipages.com.au" scraper. If none exists, use Apify's Cheerio Crawler or Puppeteer actor to scrape `hipages.com.au/find/[category]/[location]`.

**HiPages data we want:**
- Business name, phone, category, location
- Number of HiPages jobs completed
- Star rating on HiPages
- Whether they have a website linked
- Whether they appear on Google Maps (cross-reference)

**Key value:** HiPages businesses that are NOT on Google Maps = leads nobody else is reaching.

### 4. ABR Integration — Execute Script vs HTTP Request

**Decision:** Use n8n Code node with HTTP request to ABR SOAP API directly, rather than Execute Command calling the Python script.

**Rationale:** The Python script uses `zeep` SOAP library which adds a dependency. The ABR API is simple enough to call via HTTP with a SOAP envelope in a Code node. This keeps everything self-contained in n8n. However, if the SOAP envelope is too complex for a Code node, fall back to Execute Command calling the Python script.

**ABR query parameters:**
- State: WA (expand nationally as regions rotate)
- Date: yesterday (new registrations)
- Trade categories: match the 65 categories from Google Maps
- Filter Perth metro postcodes (6000-6999) initially, expand with region rotation

### 5. Pipeline B Scraper — Same Apify Actor, Different Filter

**Decision:** Use the same Apify Google Maps scraper as Pipeline A, but WITHOUT the "no website" filter. Then Platform Detector identifies DIY sites.

**Rationale:** Google Maps is the same source for both pipelines — the difference is the filter. Pipeline A = no website. Pipeline B = has website, but it's a DIY platform (Wix, Squarespace, etc.) with poor performance. Same actor, different parameters, different processing chain.

### 6. Daily Digest Overhaul

**Decision:** Complete rebuild of `Build HTML Digest` and `Query Today's Data` nodes. The new digest includes:

```
DAILY LEAD DIGEST — [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
  Total leads processed: 98
  Sent to outreach: 72
  Priority calls: 15

SOURCE BREAKDOWN
  Google Maps (no website):    32 leads (33%)  ██████████
  HiPages:                     18 leads (18%)  ██████
  ABR (new registrations):     22 leads (22%)  ███████
  DIY websites:                26 leads (27%)  ████████

REGION: Joondalup, Western Australia (Tier 1)

PRIORITY CALLS (score 7+)
  ┌──────────────────────┬──────────┬──────────┬──────────┬────────┐
  │ Business             │ Trade    │ Phone    │ Score    │ Source │
  ├──────────────────────┼──────────┼──────────┼──────────┼────────┤
  │ Dave's Plumbing      │ Plumber  │ 0412...  │ 9/10     │ GMaps  │
  │ Spark Electrical     │ Sparky   │ 0423...  │ 8/10     │ HiPg   │
  │ Fresh Builds WA      │ Builder  │ 0498...  │ 8/10     │ ABR    │
  └──────────────────────┴──────────┴──────────┴──────────┴────────┘

  📎 Full list + call scripts: [CRM Spreadsheet Link]

REPLY ANALYTICS (last 7 days)
  Emails sent:     487
  Opened:          203 (42%)
  Replied:          31 (6.4%)
  Interested:       12
  Not interested:    8
  Bounced:          15 (3.1%)

  Best performing source:    ABR (9.2% reply rate)
  Best performing trade:     Plumber (8.1% reply rate)
  Best performing variant:   social_active (11.3% reply rate)

SUGGESTIONS
  - ABR leads converting 2x better than Google Maps — consider increasing ABR allocation to 30%
  - Plumbers reply more than electricians — bump plumber search volume
  - Humour emails tracking at 7.2% vs 5.8% standard — keep the humour experiment running
  - 3 bounced emails from hipages source — verify email extraction quality
```

### 7. CRM Spreadsheet Integration

**Decision:** Each lead in the daily digest links to the CRM spreadsheet row. Pipeline writes leads to a new "Pipeline Leads" tab in the master Google Sheet (alongside the existing CRM tab) with columns:

| Column | Data |
|--------|------|
| Date | When processed |
| Business Name | From scrape |
| Trade | Category |
| Phone | For cold calling |
| Email | For reference |
| Score | 0-10 |
| Source | google_maps / hipages / abr / diy_website |
| Region | From region rotation |
| Email Variant | Which variant sent |
| Email Subject | What was sent |
| Email Body | Full email text |
| Call Script | Generated call script |
| Call Outcome | Dropdown (Aaron fills in) |
| Call Date | When called |
| Reply Status | Auto-updated from Instantly tracking |

**Rationale:** Aaron said he wants a spreadsheet he can look at and update. This gives him everything in one place — the email that was sent, the call script, space to log call outcomes, and auto-populated reply data.

### Alternatives Considered

1. **Separate workflows per source** — Rejected. Aaron prefers one consolidated workflow (learnings register).
2. **Sequential source scraping (one after another)** — Rejected. Parallel is faster and the 6am→8am window is tight.
3. **Dynamic percentage adjustment** — Deferred to Phase 2. Start with fixed splits, add auto-tuning once we have 2+ weeks of data.
4. **Dedicated HiPages API** — HiPages doesn't have a public API. Must scrape.

### Open Questions

1. **HiPages scraping approach:** Need to check Apify marketplace during implementation. If no HiPages actor exists, we build a custom scraper config. This may add $5-10/mo to Apify costs.
2. **Pipeline Leads tab vs existing CRM tab:** Should leads go into the existing CRM tab (clutters it with 100 leads/day) or a separate "Pipeline Leads" tab (cleaner, but two places to look)? Recommend separate tab with a link from the daily digest.
3. **ABR national expansion:** Currently the ABR script filters for WA postcodes only. Should we expand to match whatever region the Region Picker selects? Recommend yes — ABR is free, might as well query the region being scraped.

---

## Step-by-Step Tasks

### Step 1: Supabase Schema — Source Tracking

Add `source` tracking to existing tables and create a source_performance view.

**Actions:**
- Add `source_allocation` table (tracks daily intended vs actual per source)
- Create `source_performance` view (joins outreach_events with leads to compare sources)
- Ensure `leads.source` column captures all 4 sources distinctly

**Files affected:**
- Supabase pipeline DB (migration 006)

---

### Step 2: Source Allocator Node

New Code node that runs first in the pipeline. Determines today's source mix.

**Actions:**
- Query yesterday's lead counts per source from Supabase
- Calculate today's target per source based on percentage split
- Account for region rotation (use the Region Picker output)
- Return source configuration object consumed by downstream scrapers
- Store daily allocation in `source_allocation` table

**Files affected:**
- n8n workflow (new node after Region Picker)

---

### Step 3: HiPages Scraper

New Apify HTTP Request node for HiPages.

**Actions:**
- Search Apify marketplace for HiPages actor
- If exists: configure with category + region parameters
- If not: use Apify Web Scraper with HiPages URL pattern (`hipages.com.au/find/[category]/[region]`)
- Extract: business name, phone, category, location, HiPages jobs count, rating, website
- Filter: exclude businesses already in Google Maps results (cross-reference by phone/name)
- Set `maxItems` from Source Allocator output

**Files affected:**
- n8n workflow (new HTTP Request node + Filter node)

---

### Step 4: Wire ABR Into n8n

Connect the ABR query to the pipeline.

**Actions:**
- Create ABR Query Code node that calls ABR SOAP API via HTTP
- Use region from Region Picker to determine which state/postcodes to query
- Filter for yesterday's registrations
- Map ABR output to lead schema (business_name, abn, postcode, state, category, source='abr')
- Set `source: 'abr'` and `pipeline: 'no_website'`

**Files affected:**
- n8n workflow (new Code node)

---

### Step 5: Pipeline B Scraper

Add Apify scraper for businesses WITH websites.

**Actions:**
- Duplicate the Pipeline A Apify node configuration
- Remove the "no website" filter (or set to "has website")
- Use same region from Region Picker
- Set `maxItems` from Source Allocator (target ~30 results)
- Wire output to existing `Filter & Normalise (Has Website)` node

**Files affected:**
- n8n workflow (new HTTP Request node, wire to existing Pipeline B chain)

---

### Step 6: Merge + Deduplicate

Merge all 4 source outputs into one stream.

**Actions:**
- Add Merge node (waits for all 4 sources)
- Add Deduplicate Code node (by phone number, then by business name + suburb)
- Tag each lead with its source for tracking
- Pass merged stream to Social Enrichment → Personalisation pipeline

**Files affected:**
- n8n workflow (new Merge + Dedup nodes)

---

### Step 7: Pipeline Leads Tab in Google Sheet

Create a new tab in the master spreadsheet for pipeline leads.

**Actions:**
- Create "Pipeline Leads" tab with columns: Date, Business Name, Trade, Phone, Email, Score, Source, Region, Email Variant, Personalisation Type, Has Humour, Email Subject, Email Body, Call Script, Call Outcome, Call Date, Reply Status
- Update Supabase Store node OR add a new "Write to Sheet" node that pushes each lead to the spreadsheet
- Include a link to this tab in the daily digest

**Files affected:**
- Google Sheets (new tab)
- n8n workflow (new Code node to write to sheet)

---

### Step 8: Overhaul Daily Digest

Rebuild the daily digest email with full analytics.

**Actions:**
- Replace `Query Today's Data` with a comprehensive query that pulls:
  - Today's leads by source, region, trade, score tier
  - Last 7 days of outreach_events for reply analytics
  - Source-level reply rates
  - Trade-level reply rates
  - Variant + humour performance
- Replace `Build HTML Digest` with the full template (see Design Decision #6)
- Include:
  - Source breakdown with visual bars
  - Priority call table with phone numbers
  - Link to Pipeline Leads spreadsheet tab
  - Reply analytics (7-day rolling)
  - AI-generated improvement suggestions (simple rules: if source X reply rate > 2x average, suggest increasing allocation)

**Files affected:**
- n8n workflow (replace 2 existing nodes)

---

### Step 9: Rewire Connections

Connect all new nodes into the existing workflow.

**Actions:**
- Wire: Daily trigger → Region Picker → Source Allocator → [4 parallel branches]
- Wire: 4 branches → Merge → Deduplicate → Social Enrichment → existing pipeline
- Wire: Pipeline B branch into existing Pipeline B nodes (Platform Detector → PageSpeed → Scorer B)
- Remove orphaned `Daily 6am AWST1` trigger (Pipeline B gets data from Source Allocator now)
- Keep Manual Trigger connected (for testing)
- Add sticky notes for new sections

**Files affected:**
- n8n workflow (connections restructure)

---

### Step 10: Test & Validate

**Actions:**
- Run Manual Trigger with all 4 sources
- Verify each source returns expected data format
- Verify deduplication works across sources
- Verify daily digest shows source breakdown
- Verify Pipeline Leads tab gets populated
- Check Apify cost per run (should stay within $30/mo budget)
- Verify ABR returns results for current region

---

## Cost Analysis

| Source | Apify Cost | API Cost | Est. Monthly |
|--------|-----------|----------|-------------|
| Google Maps (no website) | ~$0.50/run × 30 days | — | ~$15/mo |
| Google Maps (DIY websites) | ~$0.30/run × 30 days | — | ~$9/mo |
| HiPages | ~$0.20/run × 30 days | — | ~$6/mo |
| ABR | — | Free | $0/mo |
| Facebook social scraping | ~$0.75/run × 30 days | — | ~$5/mo (existing) |
| **Total Apify** | | | **~$35/mo** |

**Current budget:** $30/mo. **Expected cost: ~$35/mo** — a $5/mo increase.

**Mitigation:** Reduce Google Maps `maxItems` from 50 to 40 per category, or reduce HiPages to every other day instead of daily. ABR is free so that helps offset. The $5/mo over budget is negligible for 3x the source diversity.

---

## Validation Checklist

- [ ] All 4 sources return leads and feed into the pipeline
- [ ] Source Allocator distributes leads according to percentage split
- [ ] Deduplication catches cross-source duplicates (same business on Google Maps + HiPages)
- [ ] Each lead has `source` field correctly set (google_maps, hipages, abr, diy_website)
- [ ] Pipeline B processes DIY website leads end-to-end (scrape → detect → audit → score → personalise)
- [ ] ABR leads processed correctly (source='abr', pipeline='no_website')
- [ ] Daily digest shows source breakdown, phone numbers, spreadsheet link, reply analytics
- [ ] Pipeline Leads tab populated in Google Sheet with all lead data + call script
- [ ] Reply analytics pull from outreach_events views correctly
- [ ] Apify costs stay within ~$35/mo budget
- [ ] Region Picker still works (all sources use same region)
- [ ] Trade lingo, social gating, humour all still work with multi-source leads
- [ ] Manual Trigger still works for testing
- [ ] CLAUDE.md updated if structure changed
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated

---

## Success Criteria

1. **4 sources feeding leads daily** — Google Maps, HiPages, ABR, and DIY websites all producing leads in a single pipeline run
2. **100 leads/day target achievable** — Source Allocator distributes volume and each source contributes its share
3. **Daily digest is a command centre** — Aaron opens the email and knows exactly who to call, what was sent, and what's working
4. **Source-level analytics** — Can compare reply rates across sources after 2 weeks and make data-driven allocation changes
5. **Pipeline Leads spreadsheet** — Aaron can view all leads, call scripts, and log call outcomes in one place
6. **Cost stays under $40/mo** — Adding 3 sources doesn't blow the Apify budget

---

## Notes

- **Phase 2 (future):** Auto-adjusting source percentages based on reply rate data. Once we have 4+ weeks of multi-source data, the Source Allocator could shift percentage towards higher-converting sources automatically.
- **HiPages risk:** HiPages may block scraping or change their HTML structure. Have a fallback plan (Yellow Pages AU, True Local, or Oneflare as alternative sources).
- **ABR expansion:** Once region rotation moves beyond WA, ABR queries should expand to match. The ABR API supports national queries — just change the state/postcode filter.
- **Pipeline B email angle is different:** Pipeline B leads have a website — the pitch is "your website is losing you customers" not "you don't have a website." The Build Email Prompt B node already handles this, but verify the trade lingo and social gating upgrades also apply to Pipeline B.
