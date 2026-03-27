# Outstanding Actions

Pending items that need Aaron's input or action. Claude checks this during `/prime` and flags anything stale.

**Rules:**
- Add items as they come up in conversation or during `/implement`
- Remove items when done (this is NOT append-only like learnings-register)
- Keep it short — if an item needs detail, link to a plan or context file

---

| Added | Item | Waiting On | Notes |
|-------|------|-----------|-------|
| 2026-03-12 | Test Tier 1 pricing at $1,500 | Aaron — test in next sales calls | See `context/money-model.md` |
| 2026-03-12 | Purchase PI insurance | Aaron — awaiting quotes | Emailed all 4 brokers on 2026-03-20. Follow up if no response by 2026-03-27. |
| 2026-03-12 | Add `ANTHROPIC_API_KEY` to `.env` | Aaron — low priority | Not blocking current work |
| 2026-03-15 | Chase Form Society (Chloe) failed $50 payment | Aaron — deferred | Already paid via Stripe Link. May need Radar whitelist for next recurring charge. |
| 2026-03-15 | Request feedback from all current clients | Aaron — procrastinating | Combine with payment chasing |
| 2026-03-15 | Fix Stripe Radar rules — whitelist Chloe's card | Aaron | Dashboard > Payments > Radar > Rules > Allow rules > add by email. |
| 2026-03-15 | Awaiting pricing responses from 5 Perth web agencies | Benchmark analysis | Planted Web Design, Slinky, Perth Digital Edge, Samantha Jane, Wolf Web Designs |
| 2026-03-16 | Set up Canva Connect API integration | Aaron — future (not urgent) | OAuth-based. See `reference/uploads/ad-creative-upgrade-guide.md` |
| 2026-03-16 | Build 4 Canva ad templates | Aaron — when ready | See `reference/uploads/ad-creative-upgrade-guide.md` |
| 2026-03-16 | Download Alfie's Google Docs | Aaron — low priority | Cold Calling Scripts + AI Agency Ads 2025. Links in `reference/uploads/alfie-excalidraw-summary.md` |
| 2026-03-16 | Join BNI or District 32 networking group in Perth | Aaron | One referral partner = steady warm leads |
| 2026-03-24 | **Set Apify budget cap to $45/mo** | Aaron | console.apify.com > Settings > Billing > Usage limit > $45. Bumped from $35 for Facebook source addition (5 sources now). |
| 2026-03-20 | Set Google Workspace renewal to Business Starter | Aaron — before 4 Nov 2026 | admin.google.com > Billing > Change renewal settings |
| 2026-03-23 | **Test full pipeline run via Manual Trigger** | Aaron + Claude | Verify ALL 5 sources + pattern interrupt + SMS branch. Review email + SMS drafts before sending. Test SMS to Aaron's phone first. |
| 2026-03-22 | **Revoke old OpenAI API key** | Aaron | platform.openai.com > API Keys. Revoke the key starting with `sk-proj-uI8...TbA` (compromised, was hardcoded in n8n). |
| 2026-03-22 | Monitor email warmup — target first cold sends ~2026-04-17 | Waiting | Day 3 of ~28. 3 accounts warming (myceliumai, myceliumweb, myceliumsites). |
| 2026-03-22 | Test Apify Facebook scraping costs | After first pipeline run | Using `danek~facebook-pages-posts-ppr` ($2.99/1000 results). Need to verify cost per run stays within $30/mo budget. |
| 2026-03-24 | **Get Google Business verification + collect reviews** | Aaron — blocked | Need verified Google Business Profile + 5-10 reviews before adding social proof/case studies to outreach. Required for credibility in future AI solutions campaign. |
| 2026-03-24 | **Future: AI solutions outreach campaign** | Blocked on Google Business + reviews | Alfie's framework: industry lingo → pain point → body → offer → CTA. Lead reactivation, AI appointment booking. Expand beyond websites once credibility is established. |
| 2026-03-24 | ~~Future: Optional Twilio SMS channel~~ | Done | Built 2026-03-27. 13 n8n nodes, Twilio integrated, $20 credit loaded. SMS Filter (mobile + score >= 7), Toggle on/off, inbound reply handler. Test with Aaron's phone first. |
| 2026-03-24 | **Goal: 5 website builds per week** | Ongoing | Current pipeline target. Informs daily volume (100 outreach/day) and qualification thresholds. |
| 2026-03-23 | ~~Connect Instantly tracking~~ | Done | Instantly webhooks need Hypergrowth plan. Deployed API polling every 6 hours instead. |
| 2026-03-23 | ~~Add call outcome column to CRM~~ | Done | Call Outcome + Call Date columns added. Pipeline Leads tab created with 20 columns. |
