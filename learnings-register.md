# Learnings Register

Append-only log of mistakes, pivots, insights, and workflow improvements.

**Rules:**
- Add a row whenever: a mistake, incorrect assumption, pivot, workflow improvement, or tool "gotcha" happens.
- Keep entries short, factual, and action-oriented.
- If a learning changes workflow, also update CLAUDE.md or the relevant command doc.
- Never delete rows — append only.

---

| Date/Time (local) | Type | Issue / Mistake | Learning | Fix / Next time do this | Files / Links |
|-------------------|------|-----------------|----------|------------------------|---------------|
| 2026-03-19 | Gotcha | Google Workspace alias domains can't connect to Instantly | Instantly doesn't support alias domains — it always sends from the primary account. Need secondary domains with their own user accounts. | When setting up outreach domains: always create as secondary domains with real user accounts, never aliases. Costs ~$11 AUD/mo per seat but is the only way that works with cold email tools. | `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` |
| 2026-03-19 | Insight | Email warmup is domain-specific, not account-specific | Warming up one domain does nothing for other domains on the same Workspace. Each domain builds reputation independently. | Always warm each outreach domain separately. Budget 4 weeks per new domain before cold sending. | Instantly docs |
| 2026-03-19 | Workflow | Built-in email verification saves $76 AUD/mo vs Hunter.io | SMTP mailbox check + confidence scoring based on email source can replace paid verification services | Build verification into n8n Code node. Only send to high/medium confidence emails. Suppress bounces immediately. | `HOW-plans/2026-03-16-smart-lead-gen-pipeline.md` |
| 2026-03-20 | Insight | Google Workspace Business Plus is overkill for outreach mailboxes | Aaron's on annual Plus at $30.90/user/mo — can't downgrade mid-contract, and Google hides cheaper plans in the upgrade UI. Outreach mailboxes just need to send/receive. | Use Zoho Mail Lite (A$24/user/year) for outreach domains. Keep Google Workspace for primary business email only. Set Plus renewal to Starter at contract end (4 Nov 2026). | — |
| 2026-03-20 | Gotcha | Zoho Mail requires IMAP/SMTP to be manually enabled per account | IMAP and SMTP access are OFF by default in Zoho Mail. Instantly connection fails with "IMAP not enabled" error until you toggle it on. | After creating any Zoho mailbox: immediately log in at mail.zoho.com.au → Settings → Mail Accounts → toggle IMAP ON and SMTP ON before connecting to any external service. | — |
| 2026-03-20 | Gotcha | Zoho App Passwords require 2FA enabled first | Can't generate app-specific passwords for Instantly until Multi-Factor Authentication is turned on for the Zoho account. | Enable 2FA before attempting to generate app passwords. Each Zoho user account needs its own 2FA + app password. | — |
| 2026-03-20 | Workflow | Separate Supabase projects for different concerns | Created a dedicated Supabase project for the lead pipeline (`zdaznnifkhdioczrxsae`) separate from the original project. Keeps pipeline data isolated from client/general data. | Use `SUPABASE_PIPELINE_*` env vars for pipeline DB. Original `SUPABASE_*` vars for client projects. Update `.env` comments to make this clear. | `.env` |
| 2026-03-20 | Workflow | n8n API creates workflows inactive by default | The `active` field is read-only on workflow creation via n8n REST API — can't set it during POST. Workflows are always created inactive. | Don't include `active` in the POST body. Test with Manual Trigger in the UI, then activate cron manually. | `scripts/lead-pipeline/create-n8n-workflows.py` |
| 2026-03-20 | Insight | One consolidated n8n workflow > multiple separate workflows | Aaron prefers all pipeline sections (A, B, follow-ups, digest, health) in one workflow with sticky notes, not 5 separate workflows. Easier to manage and see the full picture. | Always consolidate related automation into a single n8n workflow with clear section notes. | n8n "Automated Lead Pipeline" workflow |

---

**Types:** `Mistake` · `Pivot` · `Insight` · `Workflow` · `Gotcha`
