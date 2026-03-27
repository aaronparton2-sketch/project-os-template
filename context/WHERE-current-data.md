# Current Project State

**Last updated:** 2026-03-27

---

## Snapshot (30 seconds)

- **Project:** Smart Automated Lead Generation Pipeline
- **Goal:** Automated daily lead gen — scrape, enrich, score, personalise, email 100+ businesses/day across Australia via 5 sources (Facebook, Google Maps, HiPages, ABR, DIY websites) with auto-region rotation.
- **Current status:** In Progress (pipeline fully built with 76 nodes, testing phase — SMS channel added)

- **What's done:**
  - Lead pipeline scripts built (ABR query, email personaliser, email templates, follow-up templates, table SQL)
  - Zoho Mail configured for outreach domains (myceliumweb.com.au, myceliumsites.com.au)
  - Instantly connected — 3 accounts warming (myceliumai, myceliumweb, myceliumsites)
  - DNS verified (MX, SPF, DKIM, DMARC) for all outreach domains
  - Google Postmaster Tools verified for all 3 domains
  - Dedicated Supabase project created for pipeline (zdaznnifkhdioczrxsae)
  - n8n workflow fully built — 63 nodes, single consolidated workflow
  - Pipeline A working end-to-end: Region Picker → Source Allocator → 5 parallel branches → Merge → Scorer → Social Enrichment → Email Personaliser → Log → Region Status
  - 3-node email personaliser architecture (Build Prompt → HTTP Request → Parse) — avoids Code node 60s timeout
  - Anti-AI-slop framework: em dash ban, no "Mycelium AI", Aussie bloke voice, reviewer name-dropping
  - Auto-region rotation: 135 Australian regions seeded (Perth metro → WA regional → regional AU → outer metro → capital cities)
  - National postcode classifier (all Australian states, not just Perth)
  - Social media enrichment: Facebook post scraping via Apify, feeds recent activity into email prompts
  - 65 business category searches (trades + services + retail + food + professional)
  - OpenAI API key renewed and working
  - **Smart Outreach v2 deployed** (2026-03-23):
    - Trade-specific lingo: 16 trades covered (plumber, sparky, builder, landscaper, painter, roofer, concreter, HVAC, cleaner, tiler, fencer, pest control, carpenter, removalist, mechanic, dog trainer) + generic fallback
    - Social gating: advanced personalisation ONLY for businesses active on socials (recent + relevant posts). Standard outreach for inactive businesses.
    - Humour A/B: ~10% of emails include trade-relevant humour, tracked via `has_humour` flag
    - Call scripts: generated alongside every email with objection handlers
    - Performance tracking: `outreach_events` table + 5 Supabase views (variant, trade, humour, personalisation, weekly)
    - Weekly performance digest: Sunday 6pm AWST email with stats + kill/boost recommendations
    - Social-active email structure: personal opener → saw your content → specific proof → credibility → reason → low-friction ask
  - **Facebook source deployed** (2026-03-24):
    - 5th lead source: Facebook business page scraper via Apify
    - Strict qualification: min score 7, must have phone, no real website, posted in 90 days
    - Source allocation: Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%
    - New Merge All Sources A node chains Facebook into existing pipeline
    - Digest updated with Facebook source labels
  - **Offer variant A/B testing deployed** (2026-03-24):
    - 3 offer types: free_website (80%), mates_rates (10%), portfolio_build (10%)
    - mates_rates: "websites from $299, mates rates til end of month"
    - portfolio_build: "free website... sounds sus I know, but building my portfolio"
    - Deterministic selection (nameHash + dayOfYear), independent of email variant + humour
    - offer_type tracked in outreach_events + new offer_type_performance view
    - Weekly digest shows offer type A/B comparison
    - Call scripts include offer-specific objection handlers
  - **Pattern interrupt email variant deployed** (2026-03-27):
    - New `pattern_interrupt` variant at 15% of standard emails
    - Two self-aware openers: "chances you read this are slim" / "I know you get 10 of these a day"
    - Sharpened free_website offer: "let me build it, if you don't like it, it's yours anyway. All I need is to show you on a 15-min call"
    - Sign-off fixed: dynamic state (no more hardcoded "Perth, WA")
  - **SMS outreach channel deployed** (2026-03-27):
    - Twilio integration: Australian number +61 468 057 217
    - 13 new n8n nodes (8 outbound SMS + 4 inbound reply handler + sticky note). Workflow now 76 nodes.
    - SMS Filter: Australian mobile (04xx) + score >= 7
    - SMS Toggle: ON/OFF switch in n8n UI
    - Build SMS Prompt: same anti-AI-slop framework as email, trade lingo, 5% rogue variant (mild cussing), max 280 chars
    - Every SMS includes "Reply STOP to opt out" (Spam Act compliance)
    - Send via Twilio API, log to Supabase outreach_events (channel='sms')
    - Inbound SMS webhook handler: catches replies, classifies sentiment (positive/negative/stop), updates leads table
    - Pipeline Leads sheet: same tab, channel column distinguishes email/sms
    - $20 Twilio credit loaded for testing (~100-125 SMS)
  - **Client closed via text->call flow** (2026-03-27):
    - Aaron closed a client through SMS -> reply -> phone call -> Google Meet demo
    - Client feedback: "I get these messages every day" — free offer + local Aussie + personal touch stood out

- **Known remaining items:**
  - Set Apify budget cap to $45/mo (approved, up from $35)
  - Test full pipeline run end-to-end with real data
  - Wait for email warmup to complete (~4 weeks from 2026-03-20, target ~2026-04-17)
  - Test social media scraping costs (budget impact)
  - ~~Connect Instantly webhook to n8n~~ — Done: API polling every 6 hours (webhooks need Hypergrowth plan, Growth plan has API access)
  - ~~Add call outcome column to CRM Google Sheet~~ — Done: Call Outcome + Call Date columns added to CRM, dropdown values in CRM Lists

- **Blockers / Risks:**
  - Email warmup in progress — can't cold send until ~mid-April (day 7 of ~28)
  - Apify Facebook scraper cost per run needs testing (budget $45/mo across 5 sources)
  - SMS ready to test NOW — need to run pipeline, review drafts, then send test SMS

---

## Next Steps (think 1 step ahead)

1. **Test SMS channel** — run pipeline via Manual Trigger, review SMS drafts, send test to Aaron's phone first
2. **Test full pipeline** — verify all 5 sources + pattern interrupt variant + SMS branch
3. **Review email drafts** — Aaron reads generated emails before enabling auto-send next week
4. Set Apify budget cap to $45/mo (Aaron action)
5. Monitor email warmup — target first cold sends ~2026-04-17
6. When emails are ready: activate the Daily 6am AWST cron trigger
7. After 2 weeks of data: review source + offer type + pattern interrupt performance

---

## What Claude Should Do Next

- Help Aaron test SMS outreach via Manual Trigger (review drafts first, then send test SMS)
- Debug any issues with SMS Filter, Twilio send, or inbound reply handler
- Help Aaron review email drafts and refine before enabling auto-send
- Monitor Twilio credit spend (~$20 budget, ~100-125 SMS)
- When warmup is done (~Apr 17): connect Instantly email sending
- After 2 weeks: compare pattern_interrupt vs other variants, SMS vs email reply rates

---

## Pointers

- **Scope:** `context/WHAT-scope-of-work.md`
- **Main plan:** `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`
- **Region rotation plan:** `HOW-plans/2026-03-22-auto-region-rotation.md`
- **Social media plan:** `HOW-plans/2026-03-22-social-media-personalisation.md`
- **Smart outreach plan:** `HOW-plans/2026-03-23-smart-outreach-upgrade.md`
- **Multi-source plan:** `HOW-plans/2026-03-23-multi-source-pipeline.md`
- **Facebook + offer variants plan:** `HOW-plans/2026-03-24-facebook-source-and-offer-variants.md`
- **Pattern interrupt + SMS plan:** `HOW-plans/2026-03-27-pattern-interrupt-emails-and-sms-outreach.md`
- **Learnings:** `learnings-register.md`

---

## Progress Log (append-only)

- 2026-03-16 — Pipeline plan created. Scripts built: ABR query, email personaliser, templates, table SQL.
- 2026-03-19 — Learned Instantly needs real domains (not aliases). Switched to Zoho Mail for outreach.
- 2026-03-20 — Zoho Mail configured, DNS verified, Instantly connected with 3 accounts warming. New Supabase project created. n8n workflow scaffolded via API. Email verification built in-house (no Hunter.io needed).
- 2026-03-21 — Residential address scoring implemented: postcode classifier (JS + Python), DB migration (003), both Pipeline A and B scorers updated with +2 residential boost. Credit: Aaron's girlfriend's insight.
- 2026-03-21 — Website existence checker plan created. 3-layer verification (URL patterns → Google search → ABN domain) to eliminate 20-30% false positive rate from Google Maps "no website" data. Plan ready for implementation next session.
- 2026-03-22 — Supabase pipeline DB connected (all 4 migrations run, 65 columns). n8n Postgres credential working via pooler (`aws-1-ap-southeast-2.pooler.supabase.com:6543`). Website existence checker implemented and tested (`website-checker.js`). Major blockers cleared.
- 2026-03-22 — Massive pipeline build session. Fixed OpenAI integration ($credentials not available in Code nodes, switched to injected key). Fixed 60-second timeout by splitting personaliser into 3 nodes (Build Prompt → HTTP Request → Parse). Expanded Apify search from 12 trades to 65 business categories. Improved anti-slop framework: em dash ban, no "Mycelium AI", reviewer name-dropping.
- 2026-03-22 — Auto-region rotation implemented: `regions` table in Supabase with 135 Australian regions across 5 priority tiers. Region Picker node queries for next region, Apify searches dynamically, regions marked exhausted after <5 new leads (90-day cooldown). National postcode classifier for all states.
- 2026-03-22 — Social media enrichment implemented: Find Social Profile → Scrape Facebook Posts (Apify danek~facebook-pages-posts-ppr, $2.99/1000 results) → Parse Social Data. Only references job-related posts (completed projects, installations). Generic posts ignored.
- 2026-03-22 — Outreach tone refined: professional but human (not too casual). Value prop changed from "digital presence" to "book more jobs, look the part online". 5 email variants including recent_job, reviewer_namedrop, missing_out, look_the_part, dead_simple. Pipeline A fully wired: 15 nodes from trigger to region status update.
- 2026-03-23 — Smart Outreach v2 deployed. Trade-specific lingo (16 trades), social gating (only personalise active businesses), humour A/B (~10%), call script generation, performance tracking (outreach_events table + 5 views + weekly digest).
- 2026-03-23 — Multi-source pipeline deployed. 4 sources: Google Maps (no website 30%), HiPages (20%), ABR (20%), DIY websites (30%). Source Allocator distributes daily volume. ABR queries match region (national, not WA-only). Pipeline B now has data source. Daily digest upgraded to command centre (source splits, phone numbers, reply analytics, spreadsheet links). Pipeline Leads tab created in Google Sheet. Workflow now 58 nodes.
- 2026-03-24 — Facebook business scraper deployed as 5th lead source. Source allocation: Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%. Strict qualification (min score 7). New Merge All Sources A node chains Facebook into pipeline. Workflow now 63 nodes. Supabase migration: offer_type column + facebook_page_url + offer_type_performance view.
- 2026-03-24 — Offer variant A/B testing deployed. 3 offer types: free_website (80%), mates_rates at $299 (10%), portfolio_build (10%). Deterministic selection independent of email variant + humour. Tracked in outreach_events.offer_type. Call scripts include offer-specific objection handlers. Weekly digest shows offer type comparison. Future items captured: AI solutions outreach (blocked on Google Business), optional Twilio SMS, goal of 5 website builds/week.
- 2026-03-27 — Pattern interrupt email variant deployed (15% of standard emails). Two self-aware openers. Free_website offer pitch sharpened to proven close language. Sign-off fixed from hardcoded "Perth, WA" to dynamic state.
- 2026-03-27 — SMS outreach channel deployed via Twilio. 13 new n8n nodes (8 outbound + 4 inbound handler + sticky note). Workflow now 76 nodes. SMS Filter (mobile + score >= 7), Toggle (on/off), Build SMS Prompt (trade lingo, anti-slop, 5% rogue, STOP opt-out), Twilio send, Supabase logging. Inbound SMS webhook catches replies, classifies sentiment, updates leads. $20 credit for testing. Aaron closed a client via text->call->Meet flow — informed the design.
