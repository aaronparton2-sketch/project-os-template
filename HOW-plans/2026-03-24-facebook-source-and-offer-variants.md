# Plan: Facebook Business Scraper (5th Source) + Offer Variant Testing

**Created:** 2026-03-24
**Status:** Implemented
**Type:** Full
**Request:** Add Facebook as 5th lead source with strict qualification filtering, plus 2 new offer variants ("mates rates" and "portfolio transparency") for A/B testing.

---

## Overview

### What This Accomplishes
Adds Facebook business page discovery as a 5th lead source in the pipeline (alongside Google Maps, HiPages, ABR, DIY websites), with strict qualification to only surface high-quality leads. Also introduces 2 new email offer variants to test alternatives to the "free website" pitch — "mates rates end of month" and a transparency angle addressing the "free sounds suspicious" objection.

### Why This Matters
- Facebook has massive numbers of local businesses running pages instead of websites — untapped source
- More sources = more data = faster learning about what works
- Current "free website" offer may trigger suspicion — testing alternative angles gives us data on what converts better
- 5 sources at 100/day = serious volume for statistical testing within weeks

---

## Current State

### Relevant Existing Structure
- **Source Allocator** — Code node distributing daily 100 leads across 4 sources (30/20/20/30 split)
- **4 parallel branches** — Google Maps, HiPages, ABR, DIY websites, merging into shared pipeline
- **Scorer A** — scores no-website leads (max 10, min 6 for outreach)
- **Email personaliser** — Build Prompt → HTTP Request → Parse, 7 variants tracked
- **Social enrichment** — already scrapes Facebook posts for known pages via `danek~facebook-pages-posts-ppr`
- **outreach_events table** — tracks variant, trade, humour, personalisation type
- **5 Supabase analytics views** — variant, trade, humour, personalisation, weekly summary

### Gaps Being Addressed
1. No Facebook business discovery source — we only scrape Facebook for enrichment after finding leads elsewhere
2. Only 1 offer angle ("free website") — no A/B testing of the core value prop
3. No way to track which offer type performs best (free vs mates rates vs portfolio)

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/deploy-facebook-source.py` | n8n API deployment script for Facebook source branch nodes |
| `scripts/deploy-offer-variants.py` | Updates Build Prompt node with new offer variants |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `reference/emails/cold-outreach.md` | Add Template 7 (mates_rates) and Template 8 (portfolio_transparency) |
| `reference/trade-lingo.md` | No changes needed — existing lingo applies to Facebook leads too |
| `context/WHERE-current-data.md` | Update with Facebook source + new variants |
| `context/outstanding-actions.md` | Update Apify budget note (may need bump from $35 to $40) |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — the lead gen pipeline scope includes multi-source lead discovery and outreach testing. Facebook is a natural extension of the existing source architecture.
- **Decision required:** None — this is an enhancement to existing in-scope work.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Apify | `APIFY_API_TOKEN` | Present ✓ |
| Supabase (pipeline) | `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF` | Present ✓ |
| n8n API | `N8N_API_URL`, `N8N_API_KEY` | Present ✓ |
| OpenAI | `OPENAI_API_KEY` | Present ✓ |

No new env vars needed.

---

## Skills to Use

None.

---

## Design Decisions

### 1. Facebook Scraper Actor Selection

**Decision:** Use Apify's Facebook Pages scraper to search for business pages by location + category.

**Approach:** Search Facebook for "[trade] [suburb/city]" (e.g., "plumber Joondalup") — same pattern as Google Maps scraper. Facebook's business page search returns pages with: name, category, phone, website (if listed), address, about text, follower count, post activity.

**Candidate actors to evaluate during implementation:**
- `apify/facebook-pages-scraper` — official actor, searches by keyword
- `curious_coder/facebook-business-page-scraper` — business-focused
- `danek/facebook-pages-search` — from same developer as our posts scraper

**Fallback:** If no suitable "search" actor exists, use Facebook's public search URLs (`facebook.com/search/pages/?q=plumber+joondalup`) with a generic web scraper. Facebook search is public and doesn't require login for business pages.

### 2. Source Allocation (5 sources)

**Decision:** Redistribute from 4 to 5 sources:

| Source | Old % | New % | Target/Day |
|--------|-------|-------|------------|
| **Facebook (new)** | — | **30%** | **~30** |
| HiPages | 20% | 25% | ~25 |
| Google Maps (no website) | 30% | 20% | ~20 |
| ABR (new registrations) | 20% | 15% | ~15 |
| DIY websites | 30% | 10% | ~10 |

**Rationale:** Facebook gets 30% — untapped source with massive volume, strict qualification will keep quality high. HiPages bumped to 25% as a strong structured directory. Google Maps drops to 20% (still solid but well-mined). DIY websites down to 10% — lower priority pipeline. ABR stays at 15% for fresh registrations.

**Tuning:** After 2 weeks of data, weekly digest will recommend adjustments based on reply rates per source.

### 3. Facebook Lead Qualification (Strict)

**Decision:** Higher qualification threshold for Facebook leads (minimum score 7, not 6 like other sources).

Facebook will return massive volume. Quality filter must be aggressive:

**Facebook-specific scoring (max 12, min 7 for outreach):**

| Signal | Points | Why |
|--------|--------|-----|
| **No website listed on page** | +3 (required) | Core filter — only want businesses without websites |
| **Has phone number** | +2 (required) | Can't do outreach without contact info |
| **Active page (posted in last 90 days)** | +2 | Active = still operating, not abandoned |
| **Has business address in target region** | +1 | Confirms location match |
| **High-value trade category** | +1 | Plumber, electrician, builder, landscaper |
| **20+ page likes/followers** | +1 | Established enough to take seriously |
| **Residential address postcode** | +2 | Owner-operated signal (existing logic) |

**Hard filters (instant disqualify):**
- Has a website listed (not Facebook/Instagram URL) → skip
- No phone number → skip
- Page hasn't posted in 6+ months → skip (likely abandoned)
- Already in Supabase leads table (dedup by phone + business name) → skip

### 4. Offer Variant Design

**Decision:** Add 2 new offer types tracked via `offer_type` field:

| Offer Type | % of Emails | Description | Tracking |
|------------|-------------|-------------|----------|
| `free_website` | 80% | Current default — "I build free websites for tradies" | Existing (default) |
| `mates_rates` | 10% | "I'm doing mates rates for the end of this month" — urgency + feels less sus than free | New |
| `portfolio_build` | 10% | "Free website... sounds sus I know, but I started this biz in Jan and am building my portfolio" — honesty | New |

**Implementation:** The offer type is selected BEFORE the email variant. So you get combinations like:
- `social_active` + `mates_rates`
- `reviewer_namedrop` + `portfolio_build`
- `dead_simple` + `free_website`

**Selection logic:** Deterministic, same as humour — `(nameHash + dayOfYear) % 10`:
- 0 → `mates_rates`
- 1 → `portfolio_build`
- 2-9 → `free_website`

This way offer type and humour are independent dimensions we can A/B test separately.

### 5. "Mates Rates" Variant Copy Direction

**Tone:** Casual, time-limited, feels like a genuine deal not a scam.

**Key phrases:**
- "I'm doing mates rates til end of the month — websites from $299"
- "Normally charge $1,500-2,000 but I'm doing a few at cost to fill my calendar"
- "If you've been putting it off, now's the time"
- Keep trade lingo + social gating — just swap the offer

**NOT:** "Special limited time offer" or anything that sounds like marketing spam.

### 6. "Portfolio Transparency" Variant Copy Direction

**Tone:** Honest, self-aware, addresses the objection head-on.

**Key phrases:**
- "Free website... sounds suspicious I know"
- "I started this business in January and I'm building out my portfolio"
- "You get a free website, I get another build to show off — win-win"
- "No lock-in, you keep the code, worst case you've got a free site"

**NOT:** Desperate or begging. Still confident — just honest about the reason.

### Alternatives Considered

1. **Facebook Marketplace scraper** — Rejected. Marketplace is for products/listings, not business pages.
2. **Facebook Groups scraper** — Considered for future. Good for finding tradies posting in local groups, but harder to qualify (no structured business data). Could be a 6th source later.
3. **Higher Facebook allocation (30%)** — Rejected for launch. Start at 20%, increase if quality proves high.
4. **Separate offer variant table** — Rejected. Adding `offer_type` column to existing `outreach_events` is cleaner than a new table.

### Open Questions

None — all resolved:
1. ~~Apify budget~~ → Approved: $45/mo
2. ~~Mates rates pricing~~ → Use "$299" as concrete number
3. ~~End-of-month countdown~~ → Skip for now. Too many test variables already. Test offer types first, optimise winning variant later.

---

## Step-by-Step Tasks

### Step 1: Add `offer_type` column to Supabase

Add `offer_type` column to `outreach_events` table and update the analytics views.

**Actions:**
- Run SQL migration: `ALTER TABLE outreach_events ADD COLUMN offer_type TEXT DEFAULT 'free_website';`
- Add CHECK constraint: `offer_type IN ('free_website', 'mates_rates', 'portfolio_build')`
- Update `email_variant_performance` view to include offer_type breakdown
- Create new view `offer_type_performance` for direct comparison
- Update `weekly_outreach_summary` view to include offer type stats

**Files affected:**
- Supabase pipeline DB (SQL migration via MCP or script)

---

### Step 2: Add `lead_source` value for Facebook

Ensure the `leads` table can track Facebook as a source.

**Actions:**
- Verify `lead_source` column exists and accepts 'facebook' value
- If CHECK constraint exists, add 'facebook' to allowed values
- Add `facebook_page_url` column to leads table (TEXT, nullable) for linking back to the source page

**Files affected:**
- Supabase pipeline DB

---

### Step 3: Build Facebook source branch in n8n

Add 5th parallel branch after Source Allocator.

**Actions:**
- Create **Facebook Search** node (HTTP Request to Apify)
  - Input: region name + trade categories from Source Allocator
  - Searches: "[trade] [city/suburb]" on Facebook business pages
  - `maxItems` set dynamically from Source Allocator (target ~20/day)
- Create **Filter Facebook** node (Code)
  - Hard filter: must have phone, must NOT have website (or website = facebook.com/instagram.com only)
  - Must have posted in last 90 days
  - Must be in target region (address/suburb match)
  - Dedup against existing leads in Supabase (phone + business name)
- Create **Score Facebook** node (Code)
  - Apply Facebook-specific scoring (see Design Decision 3)
  - Minimum score 7 (stricter than other sources' min 6)
  - Output scored leads with `lead_source = 'facebook'`

**Files affected:**
- `scripts/deploy-facebook-source.py` (new)
- n8n workflow (via API)

---

### Step 4: Update Source Allocator for 5 sources

Modify the Source Allocator Code node to distribute across 5 sources.

**Actions:**
- Update allocation percentages: Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%
- Add Facebook branch output with `maxItems` calculated from allocation
- Update daily allocation logging to include Facebook

**Files affected:**
- `scripts/deploy-facebook-source.py` (same script, updates Source Allocator node)
- n8n Source Allocator Code node

---

### Step 5: Connect Facebook branch to Merge node

Wire the new Facebook branch into the existing merge point.

**Actions:**
- Add Facebook output to the Merge node (may need to chain a second Merge if n8n limits to 2 inputs)
- Verify deduplication handles Facebook leads (phone + business name matching)
- Facebook leads flow into shared pipeline: Social Enrichment → Email Personaliser → Store

**Files affected:**
- n8n workflow (Merge node connections)

---

### Step 6: Update Build Prompt with offer variants

Add offer type selection and variant-specific copy direction to the email personaliser prompt.

**Actions:**
- Add offer type selection logic: `(nameHash + dayOfYear) % 10` → 0=mates_rates, 1=portfolio_build, 2-9=free_website
- Add prompt instructions for each offer type:
  - `free_website`: existing copy (no change)
  - `mates_rates`: "I'm doing mates rates til end of the month" + urgency + casual pricing
  - `portfolio_build`: "Free website... sounds sus I know, but I started in Jan and am building my portfolio" + honesty + win-win
- Ensure offer type works independently of email variant (social_active, reviewer_namedrop, etc.)
- Include `offer_type` in the structured JSON output alongside variant, subject, body, call script
- Update call scripts to match offer type (different objection handlers for each)

**Files affected:**
- `scripts/deploy-offer-variants.py` (new)
- n8n Build Prompt Code node

---

### Step 7: Update Parse node and Supabase insert

Ensure new fields are captured and stored.

**Actions:**
- Parse node extracts `offer_type` from OpenAI response
- Supabase insert includes `offer_type` in outreach_events
- Supabase insert includes `lead_source = 'facebook'` and `facebook_page_url` for Facebook leads
- Daily digest updated to show source breakdown including Facebook
- Weekly digest updated to show offer type performance

**Files affected:**
- `scripts/deploy-offer-variants.py` (updates Parse + Store nodes)
- n8n Parse and Store nodes

---

### Step 8: Update email templates reference

Add the new offer variant templates to the reference docs.

**Actions:**
- Add Template 7: "Mates Rates" to `reference/emails/cold-outreach.md`
- Add Template 8: "Portfolio Transparency" to `reference/emails/cold-outreach.md`
- Update A/B Testing Plan section with new offer type dimension
- Add `offer_type` to the tracking dimensions list

**Files affected:**
- `reference/emails/cold-outreach.md`

---

### Step 9: Update WHERE-current-data.md and outstanding actions

**Actions:**
- Update WHERE with: Facebook as 5th source, 5-source allocation, 2 new offer variants
- Update outstanding actions: Apify budget may need bump to $40-45

**Files affected:**
- `context/WHERE-current-data.md`
- `context/outstanding-actions.md`

---

### Step 10: Test

**Actions:**
- Run Manual Trigger in n8n
- Verify Facebook source returns leads with correct scoring
- Verify offer type selection works (check 10 sample emails — should see ~1 mates_rates, ~1 portfolio, ~8 free)
- Verify new fields appear in Supabase (offer_type, facebook_page_url, lead_source='facebook')
- Check daily digest includes Facebook in source breakdown
- Check analytics views include offer_type

**Files affected:**
- n8n workflow (Manual Trigger)

---

## Validation Checklist

- [ ] Facebook source returns qualified leads (score 7+, no website, has phone)
- [ ] Source Allocator distributes ~20 leads to Facebook branch
- [ ] Facebook leads merge into shared pipeline without breaking existing flow
- [ ] Deduplication catches Facebook leads already found via other sources
- [ ] `offer_type` column exists in outreach_events with correct values
- [ ] ~10% of emails use mates_rates offer, ~10% portfolio_build, ~80% free_website
- [ ] Offer type is independent of email variant selection
- [ ] Call scripts adapt to offer type (different objection handlers)
- [ ] Daily digest shows 5-source breakdown
- [ ] Weekly digest includes offer type performance comparison
- [ ] Apify cost per Facebook scrape run is tracked
- [ ] CLAUDE.md updated if structure changed
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. **Facebook delivers 20-30 qualified leads/day** at score 7+ with confirmed no-website status
2. **Offer type A/B data starts accumulating** — after 1 week, can compare free vs mates_rates vs portfolio reply rates
3. **No increase in bounce rate** — Facebook leads have valid contact info
4. **Apify cost stays under $45/mo** total across all 5 sources (approved budget)
5. **Existing pipeline unaffected** — Google Maps, HiPages, ABR, DIY continue working at adjusted volumes

---

## Notes

- **Apify actor selection** — need to confirm the best Facebook business page search actor during implementation. If no good "search" actor exists, fallback is scraping Facebook's public search results.
- **Facebook rate limiting** — Facebook is aggressive with scraping. Apify actors handle this with proxy rotation, but monitor for blocks.
- **Future expansion** — Facebook Groups could be a 6th source (tradies posting in local community groups). Different qualification logic needed — park for later.
- **Offer variant rotation** — "mates rates" references "end of the month" which is time-sensitive. The prompt should auto-calculate days remaining so it sounds natural and urgent, not stale.
- **Eventually: case study variants** — Once Aaron has Google Business verification + reviews, add a "case study" offer variant with real results. Captured in outstanding actions.

---

## Implementation Notes

**Implemented:** 2026-03-24

### Summary
- Supabase migration: `offer_type` column on `outreach_events`, `facebook_page_url` on `leads`, `offer_type_performance` view, updated `weekly_outreach_summary` view
- Facebook source branch: 3 new nodes (Facebook Search, Filter Facebook, Score Facebook) + Merge All Sources A node. Workflow grew from 58 to 63 nodes.
- Source Allocator updated to 5-source split: Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%
- Build Email Prompt A upgraded to v2.1: offer type selection (deterministic), offer-specific system prompt injection, call script objection handlers per offer type
- Parse Email A extracts offer_type. Supabase Store persists it. Instantly tracking syncs it.
- Digest updated: Facebook source labels + offer type A/B comparison section
- Two deployment scripts: `deploy-facebook-source.py` and `deploy-offer-variants.py`

### Deviations from Plan
- Used `apify~facebook-pages-scraper` actor (official). If this doesn't work well in testing, may need to try alternative actors or fallback to public search URL scraping.
- Humour hash uses a different multiplier (x7) than offer type hash to ensure independence between the two deterministic selections.

### Issues Encountered
- Unicode arrow character in Python print statement caused `UnicodeEncodeError` on Windows cp1252 encoding. Fixed by replacing arrows with ASCII `->`. Known Windows gotcha.
