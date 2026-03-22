# Plan: Residential Address Detection for Lead Scoring

**Created:** 2026-03-21
**Status:** Implemented
**Type:** Short
**Request:** Add a +2 scoring boost for leads registered at residential/suburban Perth addresses. Not a filter — commercial/industrial leads still flow through, they just don't get the bonus. Credit: Aaron's girlfriend's insight.

---

## Overview

### What This Accomplishes
Adds a new lead scoring signal that gives +2 points to businesses registered at residential/suburban addresses. The logic: a tradie working from home in Baldivis or Ellenbrook is almost certainly owner-operated, has no marketing person, and is exactly the person who needs a free website. Businesses in Welshpool or Malaga industrial estates are more established and more likely to already have agency support.

### Why This Matters
Lead scoring determines who gets emailed first and who Aaron calls. This signal helps surface the highest-conversion leads — small owner-operators who need help the most and are most likely to say yes. It also makes every other scoring signal more powerful by stacking: a newly registered (ABR) tradie with good reviews, active on HiPages, AND operating from a home address will score 8-10 and be an absolute slam dunk.

---

## Current State

### Relevant Existing Structure
- `scripts/lead-pipeline/001-create-tables.sql` — leads table schema, already has `postcode` and `suburb` columns
- `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` — parent plan with scoring functions (lines 877-960 for Pipeline A, 970-1045 for Pipeline B)
- `scripts/lead-pipeline/abr-query.py` — already extracts `postcode` from ABR data (line 179)
- Both scorers cap at `Math.min(score, 10)`

### Gaps Being Addressed
- No address-type classification exists
- Scoring treats all locations equally — a home-based tradie in suburbia scores the same as a business in an industrial park
- No `address_type` column in the leads table

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/lead-pipeline/003-add-address-type.sql` | Migration: adds `address_type` column to leads table |
| `scripts/lead-pipeline/postcode-classifier.js` | Shared postcode → address_type classification function (used by both scorers in n8n Code nodes) |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `scripts/lead-pipeline/abr-query.py` | Add `address_type` field to lead output using postcode classification |
| Parent plan (`HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`) | Add residential signal to both scorer code blocks + update architecture notes |
| `learnings-register.md` | Log this insight |

### Files to Delete

_None._

---

## Scope Check

- **Inside scope?** Yes — this is an enhancement to the lead scoring mechanism within the existing pipeline plan. Scoring is explicitly in scope (parent plan, design decision #4).
- **Decision required:** None.

---

## Integrations & Env Vars

None — this is pure logic using data we already collect (postcode).

---

## Skills to Use

None.

---

## Design Decisions

1. **80/20 postcode classification (not geocoding or Google Places API):** We already have postcode on every lead. Classifying ~26 known commercial/industrial/CBD postcodes and defaulting everything else to residential gives us 80%+ accuracy with zero API calls, zero cost, and zero latency. Geocoding would be more precise but adds complexity, cost, and a dependency we don't need.

2. **+2 boost, not a filter:** Commercial/industrial leads still come through the pipeline and get emailed. They just don't get the +2 bonus. Aaron was clear: don't rule them out, just prioritise residential leads higher.

3. **Three zones, not two:** CBD, commercial/industrial, and residential. CBD gets +0 (saturated market, every agency pitches city businesses). Commercial/industrial gets +0 (established, more likely to have support). Residential gets +2 (owner-operated, high-conversion).

4. **Classification runs at enrichment time, not scoring time:** The `address_type` is set once when the lead is created/enriched and stored in the DB. Scorers just read the field. This means we can query leads by address type later (e.g. "show me all residential leads that didn't respond").

5. **Credit in code comments:** Aaron's girlfriend came up with this insight. A comment in the scoring function gives her credit.

### Alternatives Considered

- **Google Places API type field:** Could detect if an address is a residence vs business. More accurate but adds API cost and complexity. Rejected — postcode classification is good enough.
- **Suburb name matching:** Could match against suburb names instead of postcodes. Rejected — postcodes are more reliable (already structured data), and some suburb names are ambiguous.
- **Negative scoring for commercial/industrial:** Could subtract points. Rejected — Aaron doesn't want to penalise these leads, just prioritise residential ones higher.

### Open Questions

None — approach is confirmed by Aaron.

---

## Perth Postcode Classification Map

### CBD Postcodes (5)

| Postcode | Suburb |
|----------|--------|
| 6000 | Perth CBD |
| 6001 | Perth CBD (PO Boxes) |
| 6003 | Northbridge, Highgate |
| 6004 | East Perth |
| 6005 | West Perth |

### Industrial/Commercial Postcodes (21)

| Postcode | Suburb | Notes |
|----------|--------|-------|
| 6017 | Osborne Park | Light industrial / commercial hub |
| 6021 | Balcatta | Large industrial sector |
| 6053 | Bayswater | Industrial areas along Tonkin Hwy |
| 6054 | Bassendean | Industrial precinct near rail/freight |
| 6055 | Hazelmere | Industrial area near Great Eastern Hwy |
| 6065 | Wangara, Landsdale | Major northern industrial precinct |
| 6090 | Malaga | One of Perth's biggest industrial/trade areas |
| 6100 | Victoria Park | Commercial strip, mixed use |
| 6104 | Belmont | Industrial/commercial along Great Eastern Hwy |
| 6105 | Kewdale | Major freight/logistics hub near airport |
| 6106 | Welshpool | Core heavy industrial precinct |
| 6107 | Cannington, Kenwick | Industrial areas + Carousel commercial |
| 6109 | Maddington | Industrial estates |
| 6112 | Forrestdale (part) | Growing logistics/light industrial |
| 6154 | Myaree | Commercial/trade showroom precinct |
| 6155 | Canning Vale | Large industrial estates |
| 6163 | Bibra Lake, O'Connor, Spearwood | Major southern industrial area |
| 6164 | Jandakot, Yangebup | Industrial + airport precinct |
| 6165 | Naval Base | Heavy industry (Kwinana strip) |
| 6166 | Henderson | Heavy industrial, marine/defence |
| 6168 | Rockingham | Industrial + commercial centre |

### Residential/Suburban (Default)

Everything else in the 6000-6999 range. This covers the vast majority of Perth metro: Baldivis, Ellenbrook, Wanneroo, Mundijong, Byford, Armadale, Mandurah, Joondalup, Karrinyup, Scarborough, Fremantle suburbs, Hills district, etc.

---

## Step-by-Step Tasks

### Step 1: Create database migration

Add `address_type` column to the leads table.

**Actions:**
- Create `scripts/lead-pipeline/003-add-address-type.sql`
- SQL: `ALTER TABLE leads ADD COLUMN address_type TEXT DEFAULT 'unknown';`
- Add a comment explaining the three values: `residential`, `commercial`, `cbd`
- Add index: `CREATE INDEX idx_leads_address_type ON leads(address_type);`

**Files affected:**
- `scripts/lead-pipeline/003-add-address-type.sql` (new)

---

### Step 2: Create shared postcode classifier

A standalone JS function that both n8n Code nodes can use (copy-paste into each, or import via shared module).

**Actions:**
- Create `scripts/lead-pipeline/postcode-classifier.js`
- Define `CBD_POSTCODES` set (5 postcodes)
- Define `COMMERCIAL_INDUSTRIAL_POSTCODES` set (21 postcodes)
- Export `classifyPostcode(postcode)` → returns `'cbd'`, `'commercial'`, or `'residential'`
- Include credit comment for Aaron's girlfriend

```javascript
// Residential Address Detection
// Insight credit: Aaron's girlfriend — businesses registered at home addresses
// are more likely to be owner-operated and need marketing help.

const CBD_POSTCODES = new Set([
  '6000', '6001', '6003', '6004', '6005'
]);

const COMMERCIAL_INDUSTRIAL_POSTCODES = new Set([
  '6017', '6021', '6053', '6054', '6055', '6065', '6090',
  '6100', '6104', '6105', '6106', '6107', '6109', '6112',
  '6154', '6155', '6163', '6164', '6165', '6166', '6168'
]);

function classifyPostcode(postcode) {
  if (!postcode) return 'unknown';
  const pc = String(postcode).trim();
  if (CBD_POSTCODES.has(pc)) return 'cbd';
  if (COMMERCIAL_INDUSTRIAL_POSTCODES.has(pc)) return 'commercial';
  return 'residential';
}
```

**Files affected:**
- `scripts/lead-pipeline/postcode-classifier.js` (new)

---

### Step 3: Update ABR query script

Add `address_type` to the lead output dict so it's classified at source.

**Actions:**
- Import or inline the postcode classification logic (Python version of the same map)
- After setting `postcode` in the lead dict, add: `'address_type': classify_postcode(postcode)`
- Add Python equivalent of the classifier:

```python
CBD_POSTCODES = {'6000', '6001', '6003', '6004', '6005'}
COMMERCIAL_INDUSTRIAL_POSTCODES = {
    '6017', '6021', '6053', '6054', '6055', '6065', '6090',
    '6100', '6104', '6105', '6106', '6107', '6109', '6112',
    '6154', '6155', '6163', '6164', '6165', '6166', '6168',
}

def classify_postcode(postcode):
    if not postcode:
        return 'unknown'
    pc = str(postcode).strip()
    if pc in CBD_POSTCODES:
        return 'cbd'
    if pc in COMMERCIAL_INDUSTRIAL_POSTCODES:
        return 'commercial'
    return 'residential'
```

**Files affected:**
- `scripts/lead-pipeline/abr-query.py`

---

### Step 4: Update Pipeline A scorer (no website leads)

Add residential address as Signal 8 in `scoreNoWebsiteLead`.

**Actions:**
- Add after Signal 7 (multi-source confirmation):

```javascript
  // Signal 8: Residential address (credit: Aaron's girlfriend)
  // Home-based businesses are owner-operated, no marketing support = ideal lead
  if (lead.address_type === 'residential') {
    score += 2;
    breakdown.residential = '+2 (residential address — likely owner-operated)';
  }
```

- Update in parent plan (`HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`, lines 877-960)

**Files affected:**
- `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`

---

### Step 5: Update Pipeline B scorer (DIY website leads)

Add residential address as Signal 9 in `scoreDiyWebsiteLead`.

**Actions:**
- Add after Signal 8 (expired domain):

```javascript
  // Signal 9: Residential address (credit: Aaron's girlfriend)
  // Home-based businesses are owner-operated, no marketing support = ideal lead
  if (lead.address_type === 'residential') {
    score += 2;
    breakdown.residential = '+2 (residential address — likely owner-operated)';
  }
```

- Update in parent plan (`HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`, lines 970-1045)

**Files affected:**
- `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`

---

### Step 6: Update n8n workflow enrichment

When leads come in from Google Maps (Apify), they also have postcodes. The n8n Code node that processes scraped leads needs to classify the postcode into `address_type` before storing in Supabase.

**Actions:**
- In the n8n enrichment Code node (for both Pipeline A and B), add the `classifyPostcode` function
- Set `lead.address_type = classifyPostcode(lead.postcode)` before the Supabase insert

**Files affected:**
- n8n workflow (manual update in n8n UI — document in README)

---

### Step 7: Log the learning + give credit

**Actions:**
- Append row to `learnings-register.md`:
  - Type: `Insight`
  - Issue: "Residential address as lead scoring signal"
  - Learning: "Businesses registered at residential/suburban postcodes are more likely to be owner-operated, have no marketing support, and convert better. Credit: Aaron's girlfriend's observation."
  - Fix: "Added +2 score boost for residential postcodes in both Pipeline A and B scorers."
- Update `WHERE-current-data.md` if Aaron confirms

**Files affected:**
- `learnings-register.md`

---

## Validation Checklist

- [ ] `003-add-address-type.sql` runs cleanly in Supabase SQL Editor
- [ ] `classifyPostcode('6050')` returns `'residential'` (Mount Hawthorn — suburban)
- [ ] `classifyPostcode('6106')` returns `'commercial'` (Welshpool — industrial)
- [ ] `classifyPostcode('6000')` returns `'cbd'` (Perth CBD)
- [ ] `classifyPostcode(null)` returns `'unknown'`
- [ ] ABR script output includes `address_type` field for each lead
- [ ] Pipeline A scorer awards +2 for residential leads
- [ ] Pipeline B scorer awards +2 for residential leads
- [ ] Commercial/industrial leads still flow through (score +0, not filtered)
- [ ] Score still caps at 10
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated

---

## Success Criteria

1. Every lead in Supabase has an `address_type` value (`residential`, `commercial`, `cbd`, or `unknown`)
2. Residential leads score +2 higher than identical leads at commercial addresses
3. Zero leads are filtered out — commercial/industrial leads still enter the pipeline and get emailed
4. Aaron's girlfriend gets credit in the code comments

---

## Scoring Impact Analysis

### Pipeline A (No Website) — Max possible score after this change: 12 (capped to 10)

| Signal | Max Points |
|--------|-----------|
| New registration (ABR) | +3 |
| Google reviews | +3 |
| HiPages activity | +2 |
| Facebook-only website | +1 |
| High-value trade | +1 |
| Seasonal timing | +1 |
| Multi-source | +1 |
| **Residential address (NEW)** | **+2** |
| **Total possible** | **14 → capped to 10** |

A newly registered plumber in Ellenbrook with 25 Google reviews and 15 HiPages jobs operating from home: 3 + 3 + 2 + 1 + 2 = **11 → 10**. That's a perfect score. That's someone Aaron should be calling at 7:01am.

### Pipeline B (DIY Website) — Max possible score after this change: 17 (capped to 10)

| Signal | Max Points |
|--------|-----------|
| PageSpeed score | +3 |
| Not mobile-friendly | +2 |
| No SSL | +1 |
| SEO issues | +2 |
| Google reviews | +2 |
| Running Google Ads | +2 |
| High-value trade | +1 |
| Expired domain | +2 |
| **Residential address (NEW)** | **+2** |
| **Total possible** | **17 → capped to 10** |

---

## Notes

- The postcode lists should be reviewed after 3-6 months of data. Some mixed-use postcodes (e.g. 6100 Victoria Park, 6168 Rockingham) could be reclassified if conversion data shows they behave more like residential.
- Future enhancement: if Google Maps returns a `place_type` or `business_status` field, this could supplement postcode classification with actual business-vs-residence detection.
- This classification is Perth-specific. If the pipeline ever expands to other cities, the postcode maps would need per-city versions.

---

## Implementation Notes

**Implemented:** 2026-03-21

### Summary
All 7 steps completed. Created DB migration SQL, shared JS postcode classifier, updated ABR Python script with inline classifier + `address_type` output field, added Signal 8 (+2 residential) to Pipeline A scorer and Signal 9 (+2 residential) to Pipeline B scorer in the parent plan, logged the learning with credit.

### Deviations from Plan
- Step 6 (n8n workflow enrichment) is a manual UI step — documented the function to copy into n8n Code nodes in `postcode-classifier.js`. Will be done when Aaron connects the n8n workflow to the Supabase DB.
- Added a backfill UPDATE statement to the migration SQL so any existing leads get classified retroactively.

### Issues Encountered
None.
