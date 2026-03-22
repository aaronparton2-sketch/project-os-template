# Current Project State

**Last updated:** 2026-03-22

---

## Snapshot (30 seconds)

- **Project:** Smart Automated Lead Generation Pipeline
- **Goal:** Automated daily lead gen — scrape, enrich, score, personalise, email 100+ businesses/day across Australia via two pipelines (no website + DIY website) with auto-region rotation.
- **Current status:** In Progress (pipeline fully built, testing phase)

- **What's done:**
  - Lead pipeline scripts built (ABR query, email personaliser, email templates, follow-up templates, table SQL)
  - Zoho Mail configured for outreach domains (myceliumweb.com.au, myceliumsites.com.au)
  - Instantly connected — 3 accounts warming (myceliumai, myceliumweb, myceliumsites)
  - DNS verified (MX, SPF, DKIM, DMARC) for all outreach domains
  - Google Postmaster Tools verified for all 3 domains
  - Dedicated Supabase project created for pipeline (zdaznnifkhdioczrxsae)
  - n8n workflow fully built — 43 nodes, single consolidated workflow
  - Pipeline A working end-to-end: Region Picker → Apify → Filter → Website Checker → Scorer → Social Enrichment → Email Personaliser → Log → Region Status
  - 3-node email personaliser architecture (Build Prompt → HTTP Request → Parse) — avoids Code node 60s timeout
  - Anti-AI-slop framework: em dash ban, no "Mycelium AI", Aussie bloke voice, reviewer name-dropping
  - Auto-region rotation: 135 Australian regions seeded (Perth metro → WA regional → regional AU → outer metro → capital cities)
  - National postcode classifier (all Australian states, not just Perth)
  - Social media enrichment: Facebook post scraping via Apify, feeds recent activity into email prompts
  - 65 business category searches (trades + services + retail + food + professional)
  - OpenAI API key renewed and working

- **Known remaining items:**
  - Set Apify budget cap to $30/mo
  - Test full pipeline run end-to-end with real data
  - Wait for email warmup to complete (~4 weeks from 2026-03-20, target ~2026-04-17)
  - Test social media scraping costs (budget impact)

- **Blockers / Risks:**
  - Email warmup in progress — can't cold send until ~mid-April (day 3 of ~28)
  - Apify Facebook scraper cost per run needs testing (budget $30/mo shared with Google Maps)

---

## Next Steps (think 1 step ahead)

1. Run full pipeline test (Manual Trigger) and verify region picker works
2. Check Apify costs per run — ensure $30/mo budget is sustainable
3. Test social media scraping on real leads — check Facebook posts are being pulled
4. Set Apify budget cap to $30/mo (Aaron action)
5. Monitor email warmup — target first cold sends ~2026-04-17
6. When emails are ready: activate the Daily 6am AWST cron trigger

---

## What Claude Should Do Next

- Help Aaron test the full pipeline via Manual Trigger in n8n
- Debug any issues with the region picker, social scraper, or email personaliser
- Monitor Apify spend and adjust scrape limits if needed
- When warmup is done (~Apr 17): connect Instantly sending to the pipeline

---

## Pointers

- **Scope:** `context/WHAT-scope-of-work.md`
- **Main plan:** `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md`
- **Region rotation plan:** `HOW-plans/2026-03-22-auto-region-rotation.md`
- **Social media plan:** `HOW-plans/2026-03-22-social-media-personalisation.md`
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
