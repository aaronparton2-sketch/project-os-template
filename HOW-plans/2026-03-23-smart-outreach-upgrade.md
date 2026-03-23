# Plan: Smart Outreach Upgrade — Trade Lingo, Social Gating, Humour A/B, Performance Tracking

**Created:** 2026-03-23
**Status:** Complete (all 9 steps implemented)
**Type:** Full
**Request:** Upgrade cold outreach to use trade-specific lingo, gate advanced personalisation on social activity, add humour A/B testing (~10%), build automated performance tracking for emails + calls, and generate call scripts from enrichment data.

---

## Overview

### What This Accomplishes

Transforms the outreach system from "good personalised emails" to "emails that sound like they come from someone in the trade" — with automated tracking to prove what works. Social personalisation only fires for businesses actively posting relevant content; everyone else gets strong standard outreach. ~10% of emails include light humour, tracked separately so we can measure if it lifts response rates. Call scripts are generated alongside emails so Aaron can pick up the phone with context ready.

### Why This Matters

Every cold outreach agency sends "I noticed your business..." emails. Trade-specific language ("saw that hot water system swap you did in Joondalup" vs "saw your recent project") immediately signals "this person actually gets what I do." Combined with performance tracking, we can iterate based on data instead of gut feel — killing what doesn't work, doubling down on what does. This is the moat.

---

## Current State

### Relevant Existing Structure

| File/Component | What It Does Now |
|----------------|-----------------|
| n8n Build Prompt node | Builds OpenAI prompt with lead context, variant selection, anti-slop rules |
| n8n HTTP Request node | Calls OpenAI API with the prompt |
| n8n Parse node | Extracts subject + body from OpenAI response |
| Supabase `leads` table | Stores leads with `email_variant`, `score`, `social_best_post`, etc. |
| Supabase `regions` table | Region rotation with priority tiers |
| Social enrichment nodes | Find Social → Scrape Facebook → Parse Social Data |
| `reference/emails/cold-outreach.md` | 5 email templates + A/B testing plan |
| `reference/emails/follow-up.md` | Follow-up templates |
| Anti-slop framework | Banned patterns, Aussie tone, em dash ban, reviewer name-dropping |

### Gaps Being Addressed

1. **No trade-specific language** — emails use generic phrasing regardless of whether the lead is a plumber, sparky, or landscaper
2. **Social personalisation fires even for inactive businesses** — wastes the "saw your content" angle on businesses with stale/irrelevant posts
3. **No humour testing** — all emails are the same tone, no way to test if lighter emails convert better
4. **No automated performance tracking** — email variant tracking exists in schema but no aggregation, no call tracking, no dashboards
5. **No call scripts** — Aaron cold calls from lead digest but has to improvise each time
6. **Outreach structure for social-active leads** doesn't follow Aaron's preferred framework (personal opener → specific proof → credibility → reason → low-friction ask)

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/deploy-trade-lingo.py` | Deploys trade lingo dictionary + updated Build Prompt to n8n |
| `scripts/deploy-performance-tracking.py` | Creates Supabase tables/views for outreach analytics |
| `scripts/deploy-call-scripts.py` | Adds call script generation node to n8n workflow |
| `reference/trade-lingo.md` | Human-readable reference of trade lingo per category (also embedded in prompt) |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| n8n Build Prompt node (via deploy script) | Add trade lingo injection, social gating logic, humour flag, call script generation |
| n8n Parse node (via deploy script) | Extract call script alongside email subject/body |
| Supabase `leads` table (via migration) | Add columns: `personalisation_type`, `has_humour`, `call_script`, `call_outcome`, `call_notes`, `call_date` |
| Supabase new table `outreach_events` | Track every outreach touchpoint (email sent, opened, replied, bounced, call made, call outcome) |
| Supabase new view `outreach_performance` | Aggregated stats by variant, trade, personalisation type, humour flag |
| `reference/emails/cold-outreach.md` | Add social-active outreach structure + trade lingo notes |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — this is an enhancement to the existing lead pipeline (in-scope deliverable). Improves personalisation quality, adds tracking, generates call scripts. All within the "automated daily lead gen" project.
- **Scope delta:** None — no new WHAT, just better HOW.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Supabase (pipeline DB) | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Present |
| n8n REST API | `N8N_API_URL`, `N8N_API_KEY` | Present |
| OpenAI | `OPENAI_API_KEY` | Present |
| Instantly | `INSTANTLY_API_KEY` | Present |

---

## Skills to Use

None — this is n8n workflow modification + Supabase schema work, no new skills needed.

---

## Design Decisions

### 1. Trade Lingo: Embedded in Prompt vs Supabase Lookup Table

**Decision:** Embed a condensed trade lingo dictionary directly in the OpenAI system prompt, keyed by the lead's `category` field.

**Rationale:** The lingo dictionary is small (~20 trades × 5-8 terms each). Putting it in the prompt means OpenAI naturally weaves terms in without an extra lookup step. A Supabase table adds latency and complexity for minimal benefit. If the dictionary grows beyond 50 trades, we can move it to Supabase later.

### 2. Social Gating: How to Determine "Active on Socials"

**Decision:** A business qualifies for advanced social personalisation ONLY if:
- Has a Facebook URL (from enrichment)
- Has at least 1 post scraped
- Most recent post is within 60 days
- Post content matches relevance filter (completed jobs, tips, reviews, before/after — NOT generic ads, holiday greetings, share-if-you-agree posts)

If ANY of these fail → standard outreach (no social reference). The personalisation_type is logged as either `social_active`, `standard`, or `new_business` (ABR leads).

**Rationale:** Aaron's exact requirement — "only when the business is active on social media, posting content about recent events, jobs, tips, reviews." 60 days is generous enough to catch monthly posters but filters out dead pages.

### 3. Humour: Random Selection vs Deterministic

**Decision:** Deterministic — every 10th email gets humour (based on lead row ID or daily counter). Not truly random.

**Rationale:** Ensures exactly ~10% humour rate for clean A/B comparison. Random selection could cluster humour emails on certain days, skewing results. Deterministic also means we can reproduce which emails had humour.

### 4. Humour Style: What Kind

**Decision:** Light, trade-relevant, self-deprecating or observational. Never at the lead's expense. One line max — either in the opener or the CTA.

Examples:
- Plumber: "I promise I won't tell you about my SEO pipeline — you've probably heard enough about pipes."
- Electrician: "I won't shock you with the price — it's free."
- Builder: "I build websites, not houses — but I reckon yours would look pretty good online."
- Landscaper: "Your garden game is strong — your Google game could use some work though."
- Generic: "Fair warning — I'm better at building websites than small talk."

**Rationale:** Aaron said "tiny bit of humour" and "don't overdo it." One line that shows personality without being cringe. Trade-relevant humour signals insider knowledge.

### 5. Call Script: Full Script vs Bullet Points

**Decision:** Bullet-point call script with a natural opener + 3-4 talking points. NOT a word-for-word script.

**Rationale:** Aaron isn't a telemarketer — he needs context and talking points, not a script to read verbatim. The structure follows his preferred framework: personal opener → specific proof → credibility → reason → low-friction ask.

### 6. Performance Tracking: Supabase Views vs External Dashboard

**Decision:** Supabase views + weekly digest email. No external dashboard tool.

**Rationale:** Aaron already gets a daily lead digest via Gmail. Adding a weekly performance summary (best variant, best trade, humour vs non-humour, call conversion rate) keeps everything in the existing flow. A Grafana/Metabase dashboard is overkill at this stage — add later if needed.

### 7. Call Outcome Tracking: How Aaron Logs Calls

**Decision:** n8n webhook endpoint — Aaron texts/messages a simple format or uses a quick Google Form that writes to Supabase. Format: `[lead_id] [outcome] [notes]`. Outcomes: `answered`, `voicemail`, `no_answer`, `callback`, `interested`, `not_interested`, `wrong_number`.

**Rationale:** Needs to be frictionless. If Aaron has to open Supabase or a CRM to log a call, he won't do it. A simple text format or Google Form → n8n webhook → Supabase is the lowest-friction option.

### Alternatives Considered

1. **ChatGPT custom GPT for call scripts** — Rejected. Adds another tool. Better to generate scripts in the same pipeline and store in Supabase.
2. **Separate n8n workflow for tracking** — Rejected. Aaron prefers one consolidated workflow (per learnings register).
3. **Instantly webhooks for email events** — Considered and included. Instantly can POST to n8n when emails are opened/replied/bounced.
4. **Trade lingo in a separate Supabase table** — Rejected for now. Too much complexity for ~20 entries. Revisit if we hit 50+ trades.

### Open Questions

1. **Instantly webhook support** — Need to verify Instantly's plan supports webhooks for open/reply/bounce events. If not, we poll the API on a schedule instead.
2. **Call logging preference** — Aaron: would you prefer (a) a Google Form on your phone, (b) texting a specific format to a number, or (c) a simple web form? All route to Supabase via n8n.
3. **Humour tone check** — The examples above feel right? Too much? Too little? Want to review a few before we bake them in.

---

## The Trade Lingo Dictionary

This is the core of the upgrade. Each trade gets authentic language that signals "this person gets my industry." The rule: **use 1-2 trade terms naturally, never more. Sound like a mate who knows the trade, not a marketer who Googled it.**

### Plumbing
- **Jobs:** hot water system swap, blocked drain, burst pipe, tapware replacement, rough-in, fit-off, gas compliance
- **Tools/terms:** copper pipe, PEX, backflow preventer, tempering valve, S-trap/P-trap, DWV (drain-waste-vent)
- **Lingo:** "called out to a burst main", "HWS changeover", "emergency callout", "compliance cert"
- **Email flavour:** "Saw you just did that hot water changeover in [suburb] — those Rheem units are solid."

### Electrical
- **Jobs:** switchboard upgrade, safety switch install, LED downlight swap, ceiling fan install, RCD testing, smoke alarm compliance
- **Tools/terms:** RCD, MCB, switchboard, safety switch, conduit, cable tray, AS/NZS 3000 (Wiring Rules)
- **Lingo:** "sparky", "board upgrade", "fault finding", "test and tag"
- **Email flavour:** "Saw you did that switchboard upgrade in [suburb] — old boards are a nightmare to work with."

### Building / Construction
- **Jobs:** renovation, extension, knock-down rebuild, granny flat, retaining wall, concrete slab, frame and truss
- **Tools/terms:** DA (development approval), BA (building approval), NCC (National Construction Code), formwork, reo (reinforcement), Hebel
- **Lingo:** "knocked out a reno", "slab down", "frame up", "lock-up stage"
- **Email flavour:** "That reno you just finished in [suburb] looks mint — the before and after is chalk and cheese."

### Landscaping
- **Jobs:** garden design, reticulation install, turf laying, paving, retaining wall, pool landscaping, native garden
- **Tools/terms:** retic (reticulation/irrigation), bore, mulch, limestone, exposed aggregate, sleepers
- **Lingo:** "put in the retic", "laid the turf", "limestone walls", "pulled up the old paving"
- **Email flavour:** "Saw that retic job you did in [suburb] — WA summers are brutal without a decent system."

### Painting
- **Jobs:** interior repaint, exterior repaint, commercial paint job, roof restoration, texture coating, wallpaper
- **Tools/terms:** Dulux, Taubmans, prep work, sugar soap, cutting in, roller marks, 2-coat system
- **Lingo:** "cut in the edges", "two-pack job", "prep took longer than the paint", "roller and brush"
- **Email flavour:** "That exterior job in [suburb] came up mint — the colour choice is spot on."

### Roofing
- **Jobs:** re-roof, ridge cap repointing, gutter replacement, roof restoration, leak repair, whirlybird install
- **Tools/terms:** Colorbond, Zincalume, valley gutter, flashing, fascia, soffit, sarking
- **Lingo:** "repoint the ridge caps", "Colorbond changeover", "gutter and downpipe", "roof report"
- **Email flavour:** "Saw that Colorbond re-roof in [suburb] — those old tile roofs are everywhere around here."

### Concreting
- **Jobs:** driveway, shed slab, patio, exposed aggregate, honed concrete, liquid limestone
- **Tools/terms:** aggregate, liquid limestone, formwork, reo mesh, control joint, power float
- **Lingo:** "poured the slab", "exposed agg", "liquid lime", "power floated"
- **Email flavour:** "That exposed agg driveway in [suburb] looks unreal — the aggregate mix is bang on."

### Air Conditioning / HVAC
- **Jobs:** split system install, ducted system, AC service, refrigerant top-up, evaporative cooler
- **Tools/terms:** split system, ducted, inverter, reverse cycle, refrigerant, compressor, zones
- **Lingo:** "threw in a split", "ducted is the go", "topped up the gas", "zoned system"
- **Email flavour:** "Saw you just put a split system in over in [suburb] — this heat's been keeping you busy."

### Cleaning (Commercial/Residential)
- **Jobs:** end-of-lease clean, commercial office clean, carpet steam clean, window cleaning, pressure washing
- **Tools/terms:** bond clean, steam extraction, HEPA filter, commercial-grade, high-pressure
- **Lingo:** "bond clean", "deep clean", "steam and extract", "pressure blast"
- **Email flavour:** "Saw you smashed out that bond clean in [suburb] — agents love a sparkling handover."

### Tiling
- **Jobs:** bathroom reno tile, floor tiling, splashback, waterproofing, re-grout
- **Tools/terms:** porcelain, ceramic, subway tile, waterproofing membrane, grout, spacers, wet saw
- **Lingo:** "laid the tiles", "waterproofed the wet area", "re-grouted", "subway splashback"
- **Email flavour:** "That bathroom tile job in [suburb] is clean as — the herringbone pattern looks sharp."

### Fencing
- **Jobs:** Colorbond fence, pool fence compliance, gate automation, timber fence, slat screening
- **Tools/terms:** Colorbond, pool-compliant, post-and-rail, slats, retaining, dividing fence
- **Lingo:** "Colorbond install", "pool fence compliance", "dividing fence", "automated gate"
- **Email flavour:** "Saw that Colorbond job you did in [suburb] — neighbours must be stoked with how it turned out."

### Pest Control
- **Jobs:** termite inspection, general pest spray, possum removal, rodent baiting, pre-purchase inspection
- **Tools/terms:** termite barrier, bait station, thermal imaging, treated zone, WDI (wood-destroying insects)
- **Lingo:** "termite scare", "barrier treatment", "bait and monitor", "all clear report"
- **Email flavour:** "Saw you did a termite job in [suburb] — those older suburbs are always keeping you busy."

### Carpentry / Joinery
- **Jobs:** decking, pergola, built-in wardrobe, kitchen install, custom shelving, door hanging
- **Tools/terms:** merbau, jarrah, treated pine, dado rail, mitre joint, tongue-and-groove
- **Lingo:** "built the deck", "hung the doors", "custom fit-out", "merbau decking"
- **Email flavour:** "That merbau deck in [suburb] looks unreal — jarrah or merbau is always the go in Perth."

### Removalist / Moving
- **Jobs:** house move, office relocation, furniture delivery, piano moving, interstate move
- **Tools/terms:** packing materials, blanket wrap, trolley, tailgate loader
- **Lingo:** "smashed out a move", "packed and wrapped", "three-tonner", "door to door"
- **Email flavour:** "Saw you did that big move in [suburb] — moving day is chaos but your reviews say you make it easy."

### Auto Mechanic / Mobile Mechanic
- **Jobs:** service, brake replacement, timing belt, roadside assist, pre-purchase inspection
- **Tools/terms:** logbook service, OBD scan, timing chain, brake pads, diff service
- **Lingo:** "ran a scan", "logbook service", "pads and rotors", "rego check"
- **Email flavour:** "Saw you did that logbook service in [suburb] — people love a mobile mechanic who comes to them."

### Dog Training / Pet Services
- **Jobs:** puppy school, obedience training, aggression rehabilitation, dog walking, grooming
- **Tools/terms:** positive reinforcement, recall training, leash reactivity, socialisation, marker training
- **Lingo:** "recall work", "loose leash walking", "socialisation sessions", "behaviour consult"
- **Email flavour:** "Saw that recall training video you posted — the before and after is impressive."

### General Fallback (Trades Not Listed)
- **Lingo:** "smashed it", "came up mint", "the before and after speaks for itself", "your reviews say it all"
- **Email flavour:** "Saw that job you did in [suburb] — your customers clearly rate you."

---

## The Social Gating Logic (Detailed)

### Decision Tree

```
Lead enters Build Prompt
    │
    ├─ Has facebook_url? ──── NO ──→ personalisation_type = "standard"
    │                                  Use standard outreach template
    │
    ├─ YES
    │   ├─ Has social_best_post? ── NO ──→ personalisation_type = "standard"
    │   │
    │   ├─ YES
    │   │   ├─ social_post_date within 60 days? ── NO ──→ personalisation_type = "standard"
    │   │   │
    │   │   ├─ YES
    │   │   │   ├─ Post matches relevance filter? ── NO ──→ personalisation_type = "standard"
    │   │   │   │   (completed job, tip, review, before/after, install, project showcase)
    │   │   │   │
    │   │   │   ├─ YES ──→ personalisation_type = "social_active"
    │   │   │   │          Use social-active outreach structure:
    │   │   │   │          1. Personal opener (trade lingo)
    │   │   │   │          2. "Saw your content..." (specific post reference)
    │   │   │   │          3. Specific proof (detail from post)
    │   │   │   │          4. Credibility + relevance (why reaching out)
    │   │   │   │          5. Reason for email (value prop)
    │   │   │   │          6. Low-friction ask
    │   │   │   │
    │   │   │   └─ OVERRIDE: If lead is ABR-sourced ──→ personalisation_type = "new_business"
```

### Relevance Filter (Post Content)

**INCLUDE (job-related):**
- Completed projects: "finished", "completed", "done", "handed over", "before and after"
- Installations: "installed", "fitted", "put in", "set up", "wired up"
- Tips/advice: "tip", "trick", "how to", "did you know", "pro tip"
- Reviews/testimonials: "review", "feedback", "happy customer", "client", "thank you"
- Showcases: photos of work, "check out", "latest project", "proud of"

**EXCLUDE (not relevant):**
- Generic ads: "call us", "book now", "special offer", "discount"
- Holiday posts: "Merry Christmas", "Happy Easter", "public holiday"
- Share bait: "share if you agree", "tag someone", "giveaway"
- Political/opinion: anything not about their trade
- Reposts/shares: content from other pages (not original)
- Posts older than 60 days

---

## The Social-Active Email Structure

When `personalisation_type = "social_active"`, the email follows Aaron's preferred structure:

```
1. PERSONAL OPENER (trade lingo, casual)
   "Hey [Name],"

2. SAW YOUR CONTENT (reference the specific post naturally)
   "I came across your [post about X] the other day."
   — Never say "I saw on your Facebook page"
   — Reference as if you naturally encountered it
   — Use trade lingo when describing what the post was about

3. SPECIFIC PROOF (show you actually engaged with it)
   "That [specific detail from post] looked [genuine reaction]."
   — Reference a specific detail (suburb, technique, material, result)
   — React genuinely (not over the top)

4. CREDIBILITY + RELEVANCE (why you're reaching out)
   "The reason I'm reaching out is I build websites for [trade]s —
   and after seeing your work, I thought you'd be a good fit."
   — Connect the quality of their work to why they deserve a website
   — Don't sell yet

5. REASON / VALUE PROP (what's in it for them)
   "Most [trade]s I work with see 2-3x more enquiries once they've got a
   proper site showing up in Google. Yours would basically sell itself with
   the work you're already posting."
   — Trade-specific benefit
   — Compliment embedded

6. LOW-FRICTION ASK
   "Worth a quick chat? No pitch, just wanted to show you what I had in mind."
   — Keep it casual
   — "Quick chat", "no pressure", "no pitch"
```

**Example — Plumber who posted about a hot water system swap:**

> Hey Dave,
>
> I came across that hot water changeover you did in Joondalup the other day. Rheem to Rinnai continuous flow — smart move, those things pay for themselves.
>
> The reason I'm reaching out is I build websites for plumbers, and after seeing your work I reckon you'd be a solid fit. Most plumbers I talk to are getting calls from Google but don't have a website — so they're leaving jobs on the table for the blokes who do.
>
> Your reviews already sell you. A website would just make it easier for people to find you and get in touch.
>
> Worth a quick chat?
>
> Cheers,
> Aaron

---

## The Humour System

### Rules

1. **Frequency:** Exactly 1 in 10 emails includes humour (deterministic, not random)
2. **Placement:** One humorous line — either in the opener OR the CTA, never both
3. **Style:** Self-deprecating, observational, or trade-relevant. Never at the lead's expense.
4. **Tracking:** `has_humour = true` stored in Supabase for A/B analysis
5. **Trade-relevant:** Humour should reference the trade when possible

### Humour Examples by Placement

**Opener humour (replaces standard opener):**
- Plumber: "Fair warning — I promise this email isn't about pipes. Well... sort of."
- Electrician: "I won't shock you with the price — it's free."
- Builder: "I build websites, not houses — but yours would look pretty good online."
- Landscaper: "Your garden game is strong — your Google game could use some work though."
- Painter: "I've got to be honest — I Googled '[suburb] painter' and you didn't show up. But your reviews are five-star, so something's not adding up."
- Cleaner: "I clean up online presences — not as satisfying as a bond clean, but close."
- Generic: "I'll keep this short — I know you've got better things to do than read emails from strangers."

**CTA humour (replaces standard CTA):**
- "Worth a 10-minute chat? I promise I'm more interesting than this email makes me sound."
- "Keen for a quick yarn? Worst case you get 10 minutes of mediocre banter and a free website idea."
- "Open to a chat? I'll bring the ideas, you bring the scepticism."

### What NOT to Do
- No puns that make you cringe reading them out loud
- No humour that requires explanation
- No jokes about the lead's lack of website (insulting)
- No memes, emojis, or GIFs
- No humour in follow-up emails (follow-ups stay professional)

---

## Performance Tracking System

### New Supabase Table: `outreach_events`

```sql
CREATE TABLE outreach_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    event_type TEXT NOT NULL,  -- 'email_sent', 'email_opened', 'email_replied', 'email_bounced', 'email_unsubscribed', 'call_made', 'call_answered', 'call_voicemail', 'call_no_answer', 'call_callback', 'call_interested', 'call_not_interested', 'call_wrong_number'
    channel TEXT NOT NULL,  -- 'email' or 'call'
    variant TEXT,  -- email variant name (e.g., 'social_activity', 'competitor_angle')
    personalisation_type TEXT,  -- 'social_active', 'standard', 'new_business'
    has_humour BOOLEAN DEFAULT false,
    trade_category TEXT,  -- plumber, electrician, etc.
    notes TEXT,  -- free-text notes (especially for calls)
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_outreach_events_lead ON outreach_events(lead_id);
CREATE INDEX idx_outreach_events_type ON outreach_events(event_type);
CREATE INDEX idx_outreach_events_created ON outreach_events(created_at);
```

### New Columns on `leads` Table

```sql
ALTER TABLE leads ADD COLUMN IF NOT EXISTS personalisation_type TEXT;  -- 'social_active', 'standard', 'new_business'
ALTER TABLE leads ADD COLUMN IF NOT EXISTS has_humour BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS call_script TEXT;  -- generated call script (bullet points)
ALTER TABLE leads ADD COLUMN IF NOT EXISTS trade_lingo_used TEXT[];  -- which trade terms were injected
```

### Performance Views

```sql
-- Email performance by variant
CREATE VIEW email_variant_performance AS
SELECT
    e_sent.variant,
    COUNT(DISTINCT e_sent.lead_id) as sent,
    COUNT(DISTINCT e_open.lead_id) as opened,
    COUNT(DISTINCT e_reply.lead_id) as replied,
    COUNT(DISTINCT e_bounce.lead_id) as bounced,
    ROUND(COUNT(DISTINCT e_open.lead_id)::numeric / NULLIF(COUNT(DISTINCT e_sent.lead_id), 0) * 100, 1) as open_rate,
    ROUND(COUNT(DISTINCT e_reply.lead_id)::numeric / NULLIF(COUNT(DISTINCT e_sent.lead_id), 0) * 100, 1) as reply_rate
FROM outreach_events e_sent
LEFT JOIN outreach_events e_open ON e_sent.lead_id = e_open.lead_id AND e_open.event_type = 'email_opened'
LEFT JOIN outreach_events e_reply ON e_sent.lead_id = e_reply.lead_id AND e_reply.event_type = 'email_replied'
LEFT JOIN outreach_events e_bounce ON e_sent.lead_id = e_bounce.lead_id AND e_bounce.event_type = 'email_bounced'
WHERE e_sent.event_type = 'email_sent'
GROUP BY e_sent.variant;

-- Performance by trade category
CREATE VIEW trade_performance AS
SELECT
    trade_category,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as emails_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as email_replies,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as call_interested,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as email_reply_rate
FROM outreach_events
GROUP BY trade_category;

-- Humour A/B comparison
CREATE VIEW humour_ab_test AS
SELECT
    has_humour,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as reply_rate
FROM outreach_events
WHERE channel = 'email'
GROUP BY has_humour;

-- Personalisation type comparison
CREATE VIEW personalisation_performance AS
SELECT
    personalisation_type,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as call_conversions,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as reply_rate
FROM outreach_events
GROUP BY personalisation_type;

-- Weekly digest query
-- (run by n8n weekly to generate performance summary email)
CREATE VIEW weekly_outreach_summary AS
SELECT
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as emails_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as emails_opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as emails_replied,
    COUNT(*) FILTER (WHERE event_type = 'email_bounced') as emails_bounced,
    COUNT(*) FILTER (WHERE event_type IN ('call_made', 'call_answered', 'call_voicemail', 'call_no_answer')) as calls_made,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as calls_interested,
    COUNT(*) FILTER (WHERE event_type = 'call_not_interested') as calls_not_interested
FROM outreach_events
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC;
```

### Instantly Webhook → n8n → Supabase

Email events flow automatically:

```
Instantly (email sent/opened/replied/bounced)
    ↓ webhook POST
n8n webhook node (new trigger in consolidated workflow)
    ↓ parse event
Supabase INSERT into outreach_events
    ↓
Views auto-update
```

### Call Logging (Aaron's Manual Input)

**Option A: Google Form (recommended — lowest friction)**
- Simple form: Lead Name (autocomplete from recent leads), Outcome (dropdown), Notes (free text)
- Google Form → Google Sheet → n8n watches sheet → writes to `outreach_events` in Supabase
- Aaron bookmarks the form on his phone

**Option B: n8n webhook via URL**
- Aaron texts format: `CALL [lead_name] [outcome] [notes]`
- Parsed by n8n, matched to lead_id, inserted into outreach_events

### Weekly Performance Digest

New section added to the existing daily digest workflow (runs once per week, Sunday evening):

```
Subject: Weekly Outreach Report — [date range]

EMAILS
- Sent: X | Opened: X (Y%) | Replied: X (Y%) | Bounced: X (Y%)

TOP PERFORMING VARIANT
- [variant_name]: Y% reply rate (X sent)

TOP PERFORMING TRADE
- [trade]: Y% reply rate (X sent)

HUMOUR A/B
- With humour: Y% reply rate (X sent)
- Without humour: Y% reply rate (X sent)

SOCIAL vs STANDARD
- Social-active: Y% reply rate
- Standard: Y% reply rate

CALLS (if any logged)
- Made: X | Interested: X | Not interested: X

ACTION ITEMS
- [Kill variant X — 0% reply rate after 50 sends]
- [Double down on variant Y — 15% reply rate]
- [Trade Z converting well — increase search volume]
```

---

## Call Script Generation

### Structure (Follows Aaron's Framework)

The n8n Build Prompt node generates a call script alongside the email. The script is bullet points, not verbatim:

```
CALL SCRIPT — [Business Name] ([Trade]) — [Suburb]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPENER:
"Hey, is this [Name]? It's Aaron."

HOOK (pick one based on available data):
□ Social: "I saw your [specific post about X] — [genuine reaction with trade lingo]."
□ Review: "I saw [reviewer name]'s review — '[short quote]'. That's the kind of thing that sells itself."
□ Standard: "I found your business on Google — looks like you do solid work in [suburb]."

BRIDGE:
"The reason I'm calling is I build websites for [trade]s."

VALUE:
"Most [trade]s I talk to are getting calls from Google but don't have a
website — so they're losing jobs to the blokes who do."

YOUR EDGE:
"Your reviews are already great — a website would just make it easier for
people to find you and actually get in touch."

ASK:
"Would you be open to a quick chat about it? No pressure, just wanted to
see if it's something you'd be interested in."

IF OBJECTION — "I already get enough work":
"That's awesome — means you're doing something right. Most blokes in that
position want a website so they can be choosier about which jobs they take."

IF OBJECTION — "I've been burnt by web agencies before":
"Totally get it — that's actually why I do it differently. I build the
site first, you see it, and if you don't like it, no charge. Zero risk."

NOTES:
- Score: [X]/10 | Tier: [priority_call/email_only]
- Competitors with websites: [X] of [Y] in [suburb]
- Google reviews: [X] stars ([Y] reviews)
- [Any social media context]
```

### Storage

The call script is stored as plain text in `leads.call_script`. Aaron accesses it from:
1. The daily lead digest email (priority_call leads include their call script)
2. Supabase directly (if needed)

---

## Step-by-Step Tasks

### Step 1: Supabase Schema Migration

Create migration 004 — add new columns to `leads` table and create `outreach_events` table + performance views.

**Actions:**
- Write migration SQL (new table, new columns, views, indexes)
- Run via Supabase MCP or deploy script
- Verify tables and views exist

**Files affected:**
- Supabase pipeline DB (migration 004)
- `scripts/deploy-performance-tracking.py` (new)

---

### Step 2: Update Build Prompt Node — Trade Lingo + Social Gating

Modify the n8n Build Prompt Code node to:
- Look up trade lingo based on `category` field
- Apply social gating decision tree (active → social_active template, inactive → standard template)
- Set `personalisation_type` and `has_humour` flags
- Inject trade lingo into the OpenAI prompt
- Add the social-active email structure as a prompt template
- Add humour instruction for every 10th email

**Actions:**
- Write `scripts/deploy-trade-lingo.py` that updates the Build Prompt node via n8n API
- Include the trade lingo dictionary as a JS object in the Code node
- Include the social gating logic
- Include humour selection logic
- Update variant list to include new personalisation types

**Files affected:**
- n8n Build Prompt node (via API)
- `scripts/deploy-trade-lingo.py` (new)

---

### Step 3: Update Parse Node — Extract Call Script + New Fields

Modify the Parse Code node to extract:
- Email subject + body (existing)
- Call script (new)
- `personalisation_type` (new)
- `has_humour` (new)
- `trade_lingo_used` (new)

**Actions:**
- Update Parse node via n8n API to handle new OpenAI response fields
- Ensure all new fields flow through to the Supabase insert

**Files affected:**
- n8n Parse node (via API)
- n8n Supabase insert node (may need new field mappings)

---

### Step 4: Update OpenAI Prompt — Call Script Generation

Add instruction to the OpenAI system prompt to generate a call script alongside the email, following Aaron's framework.

**Actions:**
- Extend the OpenAI prompt to request both email AND call script in structured format
- Call script uses the same personalisation data but in spoken format
- Include objection handlers

**Files affected:**
- n8n Build Prompt node (prompt content, via deploy script from Step 2)

---

### Step 5: Instantly Webhook Integration

Set up webhook from Instantly → n8n to capture email events (sent, opened, replied, bounced).

**Actions:**
- Add a Webhook trigger node to the n8n workflow (separate trigger, same workflow)
- Parse Instantly webhook payload
- Match to lead_id (by email address)
- Insert into `outreach_events` table

**Files affected:**
- n8n workflow (new webhook trigger + processing nodes)
- Instantly campaign settings (webhook URL configuration)

---

### Step 6: Call Logging System

Set up a frictionless way for Aaron to log call outcomes.

**Actions:**
- Create a Google Form (Lead Name, Outcome dropdown, Notes)
- Connect Google Form responses → Google Sheet
- n8n watches the sheet → writes to `outreach_events`
- OR: simple n8n webhook URL that Aaron can hit from a bookmarked mobile page

**Files affected:**
- n8n workflow (new nodes for call logging)
- Google Sheets (new tab or form response sheet)

---

### Step 7: Weekly Performance Digest

Add a weekly summary email to the existing n8n workflow.

**Actions:**
- Add a weekly Cron trigger (Sunday 6pm AWST)
- Query Supabase performance views
- Format into a readable email
- Send via Gmail MCP or n8n email node
- Include action items (kill/boost recommendations based on data)

**Files affected:**
- n8n workflow (new weekly trigger + query + email nodes)

---

### Step 8: Update Reference Docs

Update `reference/emails/cold-outreach.md` with:
- Social-active outreach structure
- Trade lingo reference
- Humour guidelines
- New variant tracking info

**Actions:**
- Edit cold-outreach.md
- Create `reference/trade-lingo.md` as human-readable reference

**Files affected:**
- `reference/emails/cold-outreach.md`
- `reference/trade-lingo.md` (new)

---

### Step 9: Test & Validate

- Run pipeline with Manual Trigger
- Verify trade lingo appears in emails for different categories
- Verify social gating: active businesses get social template, inactive get standard
- Verify humour appears in ~10% of emails
- Verify call scripts are generated and stored
- Verify outreach_events table receives data
- Test Instantly webhook (if available)
- Check weekly digest query returns sensible data

---

## Validation Checklist

- [ ] Trade lingo dictionary covers top 15 trades + generic fallback
- [ ] Social gating correctly classifies leads (social_active vs standard vs new_business)
- [ ] Social personalisation ONLY fires for recent (60 days) + relevant posts
- [ ] Humour appears in exactly ~10% of emails, flagged with `has_humour = true`
- [ ] Humour is trade-relevant and not cringe
- [ ] Call scripts generated for all priority_call leads
- [ ] Call scripts follow Aaron's framework (opener → proof → credibility → reason → ask)
- [ ] `outreach_events` table captures email + call events
- [ ] Performance views return correct aggregations
- [ ] Weekly digest email sends with meaningful stats
- [ ] Anti-slop framework still enforced (em dash ban, no "Mycelium AI", Aussie tone)
- [ ] Trade lingo is subtle (1-2 terms per email, not forced)
- [ ] No secrets in tracked files
- [ ] CLAUDE.md updated if structure changed
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. **Emails sound trade-specific** — a plumber reading the email thinks "this bloke knows what a HWS changeover is"
2. **Social personalisation only fires when appropriate** — no awkward references to 6-month-old holiday posts
3. **Humour A/B data is clean** — can compare reply rates with/without humour after 100+ emails
4. **Performance tracking is automatic** — email events flow without manual work, call logging takes <30 seconds
5. **Call scripts are useful** — Aaron can glance at bullet points before dialling and sound prepared
6. **Weekly digest drives action** — clear signal on what to kill/boost/test next

---

## Implementation Order & Dependencies

```
Step 1 (Schema) ──→ Step 2 (Build Prompt) ──→ Step 3 (Parse Node) ──→ Step 4 (OpenAI Prompt)
                                                                              │
                                                                              ↓
                                                              Step 9 (Test & Validate)
                                                                              ↑
Step 5 (Instantly Webhook) ─────────────────────────────────────────────────┘
Step 6 (Call Logging) ──────────────────────────────────────────────────────┘
Step 7 (Weekly Digest) ─────────────────────────────────────────────────────┘
Step 8 (Reference Docs) — can happen anytime
```

Steps 1-4 are sequential (each depends on the previous).
Steps 5, 6, 7 are independent of each other but depend on Step 1 (schema).
Step 8 can happen anytime.

---

## Notes

- **Trade lingo will need tuning.** The initial dictionary is based on common Australian trade language. Aaron should review emails for the first week and flag any terms that feel forced or wrong. We can adjust the prompt weighting.
- **Humour needs 100+ sends minimum** before drawing conclusions. Don't kill it early.
- **Instantly webhook availability** needs to be confirmed on Aaron's plan. If webhooks aren't available, we fall back to polling the Instantly API every 6 hours.
- **Call logging friction is the #1 risk.** If it takes more than 30 seconds, Aaron won't do it. The Google Form approach is the lowest friction — he can fill it out while the phone is still ringing on the next call.
- **Future enhancement:** Once we have enough data (500+ emails), we could train a simple model to predict which variant + trade + personalisation type combo has the highest reply rate, and auto-select the optimal approach per lead. That's Phase 2.
