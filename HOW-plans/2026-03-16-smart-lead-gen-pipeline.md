# Plan: Smart Automated Lead Generation Pipeline

**Created:** 2026-03-16
**Updated:** 2026-03-19
**Status:** Draft
**Type:** Full
**Request:** Build a smart automated lead gen pipeline that scrapes 8 data sources (including DIY website detection, expired domains, Google Ads Transparency), enriches, scores, AI-personalises cold emails that don't sound like AI slop, auto-sends 20+ targeted emails daily across two pipelines, sends Aaron a daily digest with call scripts, and runs a multi-touch follow-up sequence with spreadsheet tracking.

---

## Overview

### What This Accomplishes
A fully automated system with **two parallel pipelines** and **8 data sources**:

**Pipeline A — "No Website" Leads (businesses without a website)**
1. **6:00am** — Scrapes Google Maps (no website filter), ABR new registrations, HiPages, TrueLocal/Yellow Pages, Facebook-only businesses
2. **6:15am** — Enriches each lead (Google reviews, competitor analysis, email discovery via email verification)
3. **6:20am** — Verifies all discovered emails (email verification verification — removes invalid addresses before sending)
4. **6:30am** — Scores leads 0-10 based on 7+ growth signals
5. **6:45am** — AI generates personalised cold emails for top leads (score 6+) using anti-AI-slop framework
6. **7:00am** — Pushes emails to Instantly for sending via warmed outreach domains (not Aaron's personal/business email)

**Pipeline B — "DIY Website" Leads (businesses with self-made websites that need an upgrade)**
7. **6:00am** — Scrapes Google Maps (HAS website), expired .au domains, Google Ads Transparency
8. **6:10am** — Platform detection: fingerprints Wix, Squarespace, Weebly, WordPress.com, GoDaddy Builder, Jimdo
9. **6:20am** — Quality audit: Google PageSpeed score, mobile responsiveness, SEO signals, SSL check
10. **6:25am** — Email discovery + verification (email verification)
11. **6:30am** — Scores on platform + performance + business signals (reviews, ad spend)
12. **6:45am** — AI generates upgrade-pitch emails with actual speed scores and specific issues found
13. **7:15am** — Pushes emails to Instantly for sending via warmed outreach domains

**Shared Systems**
14. **8:00am** — Daily digest to Aaron: "Here's who I emailed. Here are their phone numbers and what to say when you call."
15. **9:00am** — Auto follow-up sequence for non-responders (Day 3, Day 7, Day 14) — stops automatically if reply detected
16. **Ongoing** — A/B tests email variants and tracks response rates per template
17. **Ongoing** — Google Sheets sync: live spreadsheet view of all outreach with status, last contact, next follow-up date
18. **Ongoing** — Health monitoring: bounce rate, spam complaints, reply rate — auto-pause if thresholds exceeded
19. **Ongoing** — Compliance audit trail: every send, bounce, unsubscribe logged in Supabase with source documentation

**Volume ramp-up (first 8 weeks):**
- Weeks 1-4: Warmup only (0 cold emails — building domain reputation)
- Week 5: 20-30/day across 2 domains
- Week 6-7: 50-75/day across 2-3 domains
- Week 8+: 100-150/day cruise speed (across 3 warmed domains)

By week 8, **100-150 businesses per day receive a personalised email**. At a 2% response rate, that's **40-65 warm conversations/month**. Close 10% = **4-6 new clients/month**. Aaron's only job is to call them and say "Hey, I sent you an email this morning about your website — did you get a chance to look at it?" That's a warm follow-up, not a cold call.

### Why This Matters
Lead gen is Aaron's #1 bottleneck. He works 9-5 and has limited time for manual prospecting. This system reduces Aaron's daily outreach effort from 2+ hours of manual scraping and cold calling to **30-40 minutes of warm follow-up calls**. The pipeline does the research, personalisation, and first touch automatically. Aaron does the human part — the phone call.

### Why Two Pipelines (Not One)
The pitch is fundamentally different:
- **No website leads:** "You don't have a website. Your competitors do. Let me build you a free one."
- **DIY website leads:** "You've got a website but it's scoring 34/100 on Google's speed test. You're losing 40% of visitors. I can fix that."

Different pain point, different angle, different email template. Combining them would water down both messages. Running them in parallel means Aaron walks into every call with specific ammunition.

---

## Current State

### Relevant Existing Structure
- **Apify** — configured in `.env` (`APIFY_API_TOKEN`, `APIFY_USER_ID`). Ready to use.
- **Supabase** — configured in `.env` + MCP server in `.mcp.json`. Ready to use.
- **n8n** — configured in `.env` (MCP + REST API). Ready to use.
- **Gmail** — configured via MCP server. Ready to use.
- **Google Sheets CRM** — configured. Leads could optionally sync here too.
- `context/lead-gen-strategy.md` — strategy doc with data sources, scoring criteria, and weekly cadence.

### Gaps Being Addressed
- No automated lead generation system exists
- No lead database/table in Supabase
- ~~No ABR API integration~~ — ABR GUID now configured (2026-03-19)
- No daily lead digest
- No lead scoring mechanism
- Cold outreach is manual and disorganised
- No auto-email outreach capability
- No follow-up sequence automation
- No A/B testing of email templates
- No lead enrichment (reviews, competitors, email discovery)
- No DIY website detection (Wix/Squarespace/Weebly fingerprinting)
- No website quality auditing (PageSpeed, SEO, mobile)
- No Google Sheets tracking view for outreach status
- No expired domain monitoring
- No Google Ads Transparency monitoring
- No multi-source scraping beyond Google Maps
- Outreach emails sound like AI slop — need anti-pattern framework
- No email deliverability infrastructure (SPF/DKIM/DMARC, warmup, sender rotation)
- No secondary outreach domains (risking primary email reputation)
- No email verification before sending (bounces kill reputation)
- No reply detection to stop follow-up sequences
- No bounce handling automation
- No compliance audit trail (Spam Act 2003 defence)
- No health monitoring (bounce rate, spam complaints, reputation)
- No cross-domain unsubscribe suppression list

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/lead-pipeline/abr-query.py` | Python script to query ABR API for new WA business registrations |
| `scripts/lead-pipeline/lead-scorer-a.js` | Lead scoring logic for Pipeline A (no website) — n8n Code node content |
| `scripts/lead-pipeline/lead-scorer-b.js` | Lead scoring logic for Pipeline B (DIY website) — n8n Code node content |
| `scripts/lead-pipeline/platform-detector.js` | Website platform fingerprinting logic (Wix, Squarespace, etc.) — n8n Code node content |
| `scripts/lead-pipeline/email-personaliser.js` | AI email personalisation with anti-AI-slop framework — generates human-sounding emails per lead |
| `scripts/lead-pipeline/email-templates.json` | A/B test variants for both pipelines — template text + variable slots |
| `scripts/lead-pipeline/follow-up-templates.json` | Follow-up email templates (Day 3, 7, 14) for both pipelines |
| `scripts/lead-pipeline/README.md` | Full setup docs: architecture, all 8 sources, scoring, anti-slop framework, costs, A/B testing |
| `scripts/lead-pipeline/health-check.js` | Health monitoring logic — calculates 7-day rolling metrics, triggers auto-pause |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `reference/integrations-catalog.md` | Add ABR API, Instantly, email verification as new integrations |
| `.env.example` | Add `ABR_GUID`, `INSTANTLY_API_KEY`, `HUNTER_API_KEY`, `OUTREACH_DOMAIN_1`, `OUTREACH_DOMAIN_2` placeholders |
| `context/lead-gen-strategy.md` | Update "Automated Lead Pipeline" section with actual implementation details |
| `context/WHERE-current-data.md` | Update with project status |
| `CLAUDE.md` | Add lead pipeline to workspace structure notes if needed |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** This is a new internal project (not client work). The template workspace doesn't have a defined scope yet — this IS the first project.
- **Decision required:** Update `context/WHAT-scope-of-work.md` with this as the active project scope in Step 1 of implementation.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Apify | `APIFY_API_TOKEN`, `APIFY_USER_ID` | ✓ Present |
| Supabase | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` | ✓ Present |
| Supabase MCP | `SUPABASE_PROJECT_REF`, `SUPABASE_ACCESS_TOKEN` | ✓ Present |
| n8n (REST API) | `N8N_API_URL`, `N8N_API_KEY` | ✓ Present |
| n8n (MCP) | `N8N_MCP_SERVER_URL`, `N8N_MCP_ACCESS_TOKEN` | ✓ Present |
| Gmail MCP | `GMAIL_MCP_CONFIG_DIR` | ✓ Present (for digest + reply monitoring, NOT cold sending) |
| **ABR API** | **`ABR_GUID`** | **✓ Present (added 2026-03-19)** |
| OpenAI | `OPENAI_API_KEY` | ✓ Present (used for email personalisation via gpt-4o-mini) |
| Google Sheets | `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID` | ✓ Present (CRM sync + Lead Outreach tab) |
| **Instantly** | **`INSTANTLY_API_KEY`** | **✗ New — $47/mo, sign up at instantly.ai** |
| **Email Verification** | Built-in (n8n Code node) | ✓ No external service needed — SMTP check + confidence scoring |
| **Outreach Domain 1** | **`OUTREACH_DOMAIN_1`** | **✗ New — register e.g. getmycelium.com.au (~$15/yr)** |
| **Outreach Domain 2** | **`OUTREACH_DOMAIN_2`** | **✗ New — register e.g. myceliumweb.com.au (~$15/yr)** |

---

## Skills to Use

None — this is infrastructure/automation work, not a skill-driven workflow.

---

## Design Decisions

### 1. Supabase as lead database (not Google Sheets)
**Rationale:** Supabase gives us proper deduplication via unique constraints (phone number or place_id), SQL queries for filtering/scoring, and scales to thousands of leads. Google Sheets would hit row limits and can't deduplicate. The CRM Google Sheet is for client management AFTER conversion — Supabase is for the lead pipeline BEFORE outreach.

### 2. Eight data sources across two pipelines
**Rationale:** Everyone scrapes Google Maps. Our edge is combining sources nobody else uses (ABR new registrations, expired .au domains, Google Ads Transparency, DIY website fingerprinting) with smart scoring. Two pipelines — "no website" and "DIY website" — because the pitch is fundamentally different for each. Sources are grouped by pipeline for clean separation.

### 3. n8n as orchestrator (not a custom Python app)
**Rationale:** n8n already configured, visual workflow editing, built-in Apify + Supabase + Gmail nodes, cron scheduling, error handling. Aaron can modify workflows without touching code.

### 4. Lead scoring in an n8n Code node (not Supabase function)
**Rationale:** Scoring logic will evolve rapidly as Aaron learns what signals predict conversion. An n8n Code node is easy to edit, version, and test. Move to a Supabase function later if performance matters.

### 5. Gmail digest (not Slack/SMS)
**Rationale:** Aaron checks email every morning. Gmail MCP is already configured. A well-formatted email with a table of leads, scores, and phone numbers is the simplest daily workflow. Can add SMS alerts for 9/10+ leads later.

### 6. Daily cadence (not real-time)
**Rationale:** Aaron works 9-5. He doesn't need real-time alerts — he needs a morning briefing. Daily batch processing is cheaper (fewer Apify runs) and simpler. ABR data updates daily anyway.

### 7. Instantly for sending (not Gmail MCP)
**Rationale:** Sending cold emails directly from Aaron's Gmail (personal or business) risks destroying his sender reputation. One batch of spam complaints = his real email goes to junk for everyone. Instantly ($47/mo) provides: dedicated outreach domain management, automatic warmup, sender rotation across multiple domains, deliverability monitoring, and built-in reply detection. n8n generates the emails → pushes to Instantly API → Instantly handles the actual sending. Gmail MCP is still used for the daily digest and monitoring replies.

### 8. Secondary outreach domains (not primary domains)
**Rationale:** Never send cold email from `myceliumai.com.au` or `AaronParton2@gmail.com`. Register 2-3 cheap `.com.au` domains (~$15/yr each) that look legitimate and redirect to the main site. If one gets burned by spam complaints, spin up another. Primary domains stay clean for client communication, invoicing, and onboarding.

### 9. Built-in email verification via SMTP check + confidence scoring (not Hunter.io)
**Rationale:** Sending to invalid email addresses causes bounces, which destroy sender reputation. Instead of paying ~$76 AUD/mo for Hunter.io, we build our own verification: (1) confidence scoring based on where the email was found, (2) free SMTP mailbox check in an n8n Code node. Only high/medium confidence verified emails get sent. Target: <1% bounce rate. Saves ~$76/mo.

### 10. Anti-AI-Slop Email Framework (baked into personaliser)
**Rationale:** Everyone's using AI for cold outreach now. Recipients pattern-match AI emails instantly and delete them. Our personaliser must generate emails that break every AI pattern. See "Anti-AI-Slop Framework" section below for the full ruleset baked into the OpenAI system prompt.

### 8. Google Sheets tracking view (not just Supabase)
**Rationale:** Aaron wants a spreadsheet to see outreach status at a glance — who's been contacted, when, what's the next follow-up date. Supabase is the source of truth, but a new "Lead Outreach" tab in the master Google Sheet syncs daily for human-friendly viewing and manual notes.

### 9. Smart website detection (not just "has website or not")
**Rationale:** The old plan only checked "has website = yes/no". That misses the huge opportunity: businesses that HAVE a website but it's a self-made Wix/Squarespace disaster. These are actually better leads — they've proven they care about having a site, they just did it badly. Platform fingerprinting + PageSpeed scoring identifies them automatically.

### Alternatives Considered
- **Real-time webhooks** — unnecessary for daily batch pipeline. Over-engineered.
- **Google Sheets as database** — can't deduplicate, can't score with SQL, hits row limits. But useful as a VIEW.
- **Separate n8n workflows per source** — harder to maintain. One workflow per pipeline with parallel branches is cleaner.
- **Python orchestrator** — more flexible but loses n8n's visual editing and built-in node ecosystem.
- **BuiltWith API for platform detection** — paid ($295/mo+). We can fingerprint platforms ourselves for free using HTML meta tags, script URLs, and DNS checks.
- **Single pipeline for both no-website and DIY-website leads** — rejected because the pitch is fundamentally different and combining them waters down both messages.

### Open Questions

1. ~~**ABR API registration**~~ — Done (2026-03-19). GUID added to `.env`.
2. **Apify budget cap** — should we set a hard monthly limit on Apify spend? Recommend $30/mo cap (increased from $20 due to additional sources).
3. **Lead digest format** — plain text email, HTML table, or link to a Supabase dashboard view? Recommend HTML table in email for now.
4. **CRM sync** — should new high-scoring leads (8+/10) auto-append to the Google Sheet CRM tab? Or keep pipeline and CRM separate until Aaron manually qualifies?
5. **Expired domain volume** — .au domain drop lists can be large. How aggressively should we filter? Recommend: Perth postcodes only + business-sounding names only.
6. **Google Ads Transparency scraping** — no official API. May need Apify actor or custom scraper. Research needed during implementation.

---

## Email Sending Infrastructure

### Domain Strategy

| Domain | Purpose | Cold Email? | Risk Profile |
|--------|---------|-------------|-------------|
| `AaronParton2@gmail.com` | Personal — friends, family, personal use | **NEVER** | Protected |
| `aaron@myceliumai.com.au` | Business — client replies, invoices, onboarding, digest emails | **NEVER** | Protected |
| `aaron@getmycelium.com.au` | **Outreach domain #1** — cold email sending | Yes | Expendable |
| `aaron@myceliumweb.com.au` | **Outreach domain #2** — cold email sending | Yes | Expendable |
| `aaron@myceliumsites.com.au` | **Outreach domain #3** (future) — scale to 150/day | Yes | Expendable |

**Why secondary domains:** If a domain gets flagged for spam, only the expendable domain is affected. Aaron's real email and business domain stay clean. Registering `.com.au` domains costs ~$15/yr each through VentraIP or Crazy Domains.

### DNS Setup Per Outreach Domain (Required)

Each outreach domain needs these DNS records before ANY email is sent:

**1. SPF Record (TXT)**
```
v=spf1 include:_spf.google.com include:sendgrid.net ~all
```
(Adjust includes based on which services send for this domain)

**2. DKIM Record (TXT)**
```
selector._domainkey.getmycelium.com.au → [public key from Google Workspace/Instantly]
```
Generate via Google Workspace admin or Instantly's domain setup wizard.

**3. DMARC Record (TXT)**
```
_dmarc.getmycelium.com.au → v=DMARC1; p=none; rua=mailto:dmarc@getmycelium.com.au; pct=100
```
Start with `p=none` (monitor mode). After 2-4 weeks of clean sending, escalate to `p=quarantine`, then eventually `p=reject`.

**4. Custom Tracking Domain (CNAME)**
Point to Instantly's tracking domain for open/click tracking without triggering spam filters.

**5. Google Postmaster Tools**
Register each outreach domain at `postmaster.google.com`. Monitors:
- Spam complaint rate (keep below 0.1%)
- Authentication pass rate (target 99%+)
- Domain reputation (High/Medium/Low)
- Delivery errors

### Warmup Schedule

| Week | Warmup Emails/Day | Cold Emails/Day | Total/Day | Notes |
|------|-------------------|-----------------|-----------|-------|
| 1 | 10-20 | 0 | 10-20 | Warmup only (Instantly handles this) |
| 2 | 15-25 | 0 | 15-25 | Building reputation |
| 3 | 20-30 | 5-10 | 25-40 | Light cold begins (~day 15) |
| 4 | 30-40 | 15-25 | 45-65 | Ramp up |
| 5 | 30-40 | 30-40 | 60-80 | Per domain. 2 domains = 60-80 cold/day |
| 6+ | 30-40 | 40-50 | 70-90 | Cruise. 2 domains = 80-100 cold/day |
| 8+ | 30-40 | 50 | 80-90 | 3 domains = 150 cold/day max |

**Rules:**
- Never increase volume by more than 20% in a single day
- Maintain warmup emails alongside cold emails indefinitely (1:1 ratio)
- If bounce rate exceeds 2.5%, pause cold sends and investigate
- If spam complaint rate exceeds 0.1%, pause immediately

### Instantly Integration

**How it works:**
1. n8n generates personalised emails (subject + body + recipient) using anti-slop framework
2. n8n pushes emails to Instantly via REST API (`POST /api/v1/campaign/add-leads-to-campaign`)
3. Instantly handles: sending via warmed outreach domains, sender rotation, spacing (60-120s between sends), warmup, deliverability monitoring
4. Instantly detects replies → webhook to n8n → n8n updates Supabase (mark as replied, stop follow-up sequence)
5. Replies arrive in the outreach domain inboxes → Aaron checks or Instantly forwards to main email

**API endpoints used:**
- `POST /api/v1/campaign/create` — create campaigns for Pipeline A and B
- `POST /api/v1/campaign/add-leads-to-campaign` — push daily leads
- `GET /api/v1/analytics/campaign` — pull stats for daily digest
- Webhook: reply detection → n8n

### Email Verification (Pre-Send — Built-In, No External Service)

Every email address discovered by the pipeline is scored and verified before sending. No paid service required.

**Step 1: Confidence Scoring (based on source)**

| Confidence | Source | Action |
|-----------|--------|--------|
| **High** | Email on company website contact page, Google Business profile, ABR listing | Send |
| **Medium** | Standard business pattern (info@, contact@, admin@, hello@) from a verified domain | Send |
| **Low** | Guessed/inferred email, generic Gmail/Hotmail, no public source | Skip — don't send |
| **Blocked** | Previously bounced or in suppressed_emails table | Never send |

**Step 2: Free SMTP Verification (n8n Code node)**

```javascript
// SMTP mailbox check — verifies the email server accepts mail for this address
// WITHOUT actually sending an email. Free, no API key needed.
// Returns: 'valid', 'invalid', 'catch_all', 'unknown'
async function verifyEmail(email) {
  const domain = email.split('@')[1];
  // 1. Check MX records exist for the domain
  // 2. Connect to the mail server
  // 3. Issue RCPT TO:<email> — server responds 250 (exists) or 550 (doesn't)
  // 4. Disconnect without sending
  // Note: Some servers accept all (catch-all) — these get 'catch_all' status
}
```

**Step 3: Decision**
- `valid` + High/Medium confidence → proceed to sending
- `catch_all` + High confidence → proceed (but monitor bounce rate)
- `invalid` or Low confidence → skip, log in Supabase, never send
- Any bounce after sending → add to `suppressed_emails` immediately

**Target: <1% bounce rate.** This protects sender reputation above everything else. If bounce rate creeps above 2%, the health monitor auto-pauses campaigns.

### Legal Compliance (Spam Act 2003)

Every cold email MUST include:

1. **Clear sender identification:**
   ```
   Aaron Parton
   Mycelium AI
   Perth, WA
   ```

2. **Functional unsubscribe mechanism:**
   ```
   If this isn't relevant, just reply "stop" and I won't contact you again.
   ```
   (Simple reply-based opt-out. Instantly can also add a 1-click unsubscribe link.)

3. **Source documentation** — For every lead, record in Supabase:
   - `email_source`: where the email was found ('google_maps', 'company_website', 'linkedin', 'hunter_io', 'abr')
   - `email_source_url`: the specific URL where it was published (for legal defence)
   - `email_found_at`: timestamp when discovered

4. **Unsubscribe within 5 business days** — When someone replies "stop", mark in Supabase immediately. Instantly handles removal from active campaigns. Cross-domain suppression: add to a shared `suppressed_emails` table so they never get contacted from ANY outreach domain.

5. **Inferred consent basis** — Only email addresses that are "conspicuously published" online (company website, LinkedIn, Google Business, ABR). Never scrape personal emails from private sources.

### Suppressed Emails Table (Supabase)

```sql
CREATE TABLE suppressed_emails (
  email TEXT PRIMARY KEY,
  reason TEXT NOT NULL,  -- 'unsubscribed', 'hard_bounce', 'spam_complaint', 'manual'
  source_domain TEXT,    -- which outreach domain triggered the suppression
  suppressed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_suppressed_email ON suppressed_emails(email);
```

Every email send checks this table first. If the recipient is suppressed, skip silently. This list applies across ALL outreach domains.

### Compliance Audit Trail Table (Supabase)

```sql
CREATE TABLE email_audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES leads(id),
  email_to TEXT NOT NULL,
  email_from TEXT NOT NULL,
  email_subject TEXT,
  email_type TEXT NOT NULL,  -- 'cold_outreach', 'follow_up_1', 'follow_up_2', 'follow_up_3'
  pipeline TEXT,  -- 'no_website', 'diy_website'
  email_source TEXT,  -- where recipient's email was found
  email_source_url TEXT,  -- URL where email was published
  sending_domain TEXT,  -- which outreach domain sent it
  instantly_campaign_id TEXT,
  status TEXT DEFAULT 'sent',  -- 'sent', 'delivered', 'opened', 'replied', 'bounced', 'unsubscribed'
  bounce_type TEXT,  -- 'hard', 'soft', NULL
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_lead ON email_audit_log(lead_id);
CREATE INDEX idx_audit_email ON email_audit_log(email_to);
CREATE INDEX idx_audit_status ON email_audit_log(status);
```

### Health Monitoring (Auto-Pause)

n8n workflow runs daily at 7pm — checks pipeline health and auto-pauses if thresholds exceeded:

| Metric | Target | Warning | Auto-Pause |
|--------|--------|---------|------------|
| Bounce rate (7-day rolling) | <1% | >2% | >3% |
| Spam complaint rate (7-day) | <0.05% | >0.1% | >0.3% |
| Reply rate (7-day) | >1% | <0.5% (content issue) | N/A |
| Unsubscribe rate (7-day) | <2% | >3% | >5% |
| Domain reputation (Postmaster) | High | Medium | Low |

If auto-pause triggers:
1. Stop all cold sends from affected domain
2. Send alert email to Aaron
3. Continue warmup emails (to rebuild reputation)
4. Resume cold sends only after Aaron reviews and confirms

---

## Anti-AI-Slop Email Framework

This ruleset is baked into the OpenAI system prompt for the email personaliser. Every generated email MUST follow these rules.

### BANNED Patterns (instant delete signals)

| Pattern | Why It's Banned | What To Do Instead |
|---------|----------------|-------------------|
| "I hope this email finds you well" | Universal AI opener. Recipients delete on sight. | Jump straight into the hook. No greeting preamble. |
| "I was impressed by [Company]'s growth" | Generic flattery with no proof you looked at anything. | Reference ONE specific thing: a Google review quote, a recent job, their suburb. |
| "leverage", "streamline", "optimize", "innovative", "synergy" | Business jargon nobody uses in real conversation. | Use normal words: "fix", "speed up", "sort out", "help with". |
| "I'd love to schedule a call to discuss" | Corporate CTA that sounds like a sales script. | Micro-CTA: "worth a look?" or "interested?" or "want me to show you?" |
| Perfect grammar throughout | Humans make typos and use fragments. Perfection = robot. | Use contractions everywhere. Mix sentence lengths. Allow a casual fragment. |
| Exactly 3 bullet points | AI's default structure. Recipients pattern-match it. | Vary: sometimes 2, sometimes none, sometimes a short paragraph instead. |
| "Please don't hesitate to reach out" | Nobody talks like this. | "Give me a shout if you're keen" or just "Cheers, Aaron". |
| Starting with "I" | Self-focused. The email should be about THEM. | Start with something about their business, their reviews, their situation. |

### REQUIRED Patterns (what makes it sound human)

| Pattern | Example |
|---------|---------|
| **Contractions everywhere** | "I'm", "you're", "don't", "won't", "it's", "that's" |
| **One specific detail proving research** | "Your customer Sarah said 'best plumber in Malaga' — that kind of review sells itself" |
| **Casual aside or parenthetical** | "(not trying to sell you anything — genuinely think this could help)" |
| **Admission of uncertainty** | "Not sure if this is relevant, but..." or "Might be a stretch, but..." |
| **Mixed sentence lengths** | Short. Then a medium one. Then a slightly longer one that flows naturally. Short again. |
| **Sign off as "Cheers, Aaron"** | Never "Best regards", "Sincerely", "Kind regards". Always "Cheers". |
| **Micro-CTA (low commitment)** | "Worth a look?" / "Interested?" / "Want me to show you?" — NOT "Let's schedule a 30-minute call" |
| **Max 5-6 sentences total** | If it scrolls on a phone, it's too long. |
| **No emoji** | Emoji in cold emails = instant spam filter and AI signal. |

### Template Tone Rules (for OpenAI system prompt)

```
You are writing a cold email from Aaron, a web designer in Perth.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with something specific about THEIR business (a review quote, their suburb, a specific issue you found)
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution"
- No emoji
- Vary sentence length — not all the same rhythm
- One sentence can be a fragment. That's fine.
- Sound like a tradie who's good with computers, not a marketing agency
```

### DIY Website Upgrade Email Angle

For Pipeline B (businesses with self-made websites), the email includes their actual audit data:

```
Subject: Your website's costing you customers

Hey [Name],

Found [Business Name] on Google — [X] reviews averaging [Y] stars, clearly you're doing solid work in [suburb].

Ran a quick speed test on your site though — it scored [PageSpeed score]/100. For context, anything under 50 means about 40% of visitors leave before the page even loads. [Specific issue: "the mobile version takes 8 seconds to load" / "your contact page has a broken form" / "Google can't read your services page for SEO"].

I rebuild sites like yours all the time — typically triple the speed and get them ranking properly in Google. Happy to show you what yours could look like, no obligation.

Worth a look?

Cheers,
Aaron
Mycelium AI
[phone]
```

---

## Architecture

### Workflow 1: Pipeline A — "No Website" Leads (Daily 6am)

```
┌──────────────────────────────────────────────────────────────────────────┐
│              n8n Workflow 1: Pipeline A — "No Website" (Daily 6am)        │
│                                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐ │
│  │ Apify:      │ │ ABR API:    │ │ Apify:   │ │ Apify:    │ │ Apify: │ │
│  │ Google Maps │ │ New WA ABNs │ │ HiPages  │ │ TrueLocal │ │ FB Biz │ │
│  │ (no website)│ │ (yesterday) │ │ (Mon)    │ │ + YellowP │ │ Pages  │ │
│  └──────┬──────┘ └──────┬──────┘ └────┬─────┘ └─────┬─────┘ └───┬────┘ │
│         └───────┬───────┴──────┬──────┴──────┬───────┘           │      │
│                 └──────────────┴─────────────┴───────────────────┘      │
│                                ↓                                        │
│                   ┌────────────────┐                                     │
│                   │ Normalise &    │                                     │
│                   │ Merge Results  │                                     │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ ENRICH         │  For each lead:                     │
│                   │ (Code node)    │  - Pull Google review quotes        │
│                   │                │  - Count competitors with websites  │
│                   │                │  - Find email (email verification or regex)  │
│                   │                │  - Check if website = Facebook      │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ Lead Scorer    │  Scores 0-10 based on signals       │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ Supabase:      │  INSERT ON CONFLICT DO NOTHING      │
│                   │ Deduplicate    │  pipeline = 'no_website'            │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ email verification:     │  Verify all discovered emails        │
│                   │ Email Verify   │  Only 'valid'/'accept_all' proceed  │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ AI PERSONALISE │  Anti-slop framework enforced       │
│                   │ Top leads      │  "No website" templates only        │
│                   │ score 6+       │  + call scripts + A/B variant       │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ Check          │  Skip if in suppressed_emails       │
│                   │ Suppression    │  (unsubscribed/bounced/complained)  │
│                   │ List           │                                     │
│                   └───────┬────────┘                                     │
│                           ↓                                             │
│                   ┌────────────────┐                                     │
│                   │ Instantly API: │  Push to Instantly campaign          │
│                   │ Add leads      │  Instantly handles sending,          │
│                   │ to campaign    │  warmup, rotation, spacing           │
│                   │ + Log to       │  + Log to email_audit_log           │
│                   │ Supabase       │  Set follow_up_due = +3 days        │
│                   └────────────────┘                                     │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│            n8n Workflow 2: Pipeline B — "DIY Website" (Daily 6am)        │
│                                                                          │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐               │
│  │ Apify:       │  │ Expired .au   │  │ Google Ads      │               │
│  │ Google Maps  │  │ Domain List   │  │ Transparency    │               │
│  │ (HAS website)│  │ (daily drop)  │  │ (Perth filter)  │               │
│  └──────┬───────┘  └───────┬───────┘  └────────┬────────┘               │
│         └──────────┬───────┴──────────┬─────────┘                        │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ PLATFORM DETECT  │  Fingerprint the website:                   │
│         │ (HTTP Request +  │  - HTML meta generator tag                  │
│         │  Code node)      │  - Script/CSS URLs (wix.com, squarespace)   │
│         │                  │  - DNS CNAME records                         │
│         │                  │  - Cookie names                              │
│         │                  │  Detected: Wix, Squarespace, Weebly,        │
│         │                  │  WordPress.com, GoDaddy Builder, Jimdo      │
│         └──────────┬───────┘                                             │
│                    ↓ (only DIY-platform sites continue)                  │
│         ┌──────────────────┐                                             │
│         │ QUALITY AUDIT    │  For each DIY site:                         │
│         │ (PageSpeed API + │  - Google PageSpeed score (0-100)           │
│         │  Code node)      │  - Mobile responsiveness check              │
│         │                  │  - Core Web Vitals (LCP, FID, CLS)          │
│         │                  │  - SEO basics (meta desc, H1, alt text)     │
│         │                  │  - SSL check (HTTP vs HTTPS)                │
│         │                  │  - Broken contact form detection             │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ DIY SCORER       │  Scores 0-10:                               │
│         │                  │  - PageSpeed < 50 = +3                      │
│         │                  │  - No SSL = +1                              │
│         │                  │  - No meta description = +1                 │
│         │                  │  - Google reviews 10+ = +2                  │
│         │                  │  - Running Google Ads = +2                  │
│         │                  │  - High-value trade = +1                    │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ Supabase:        │  INSERT ON CONFLICT DO NOTHING              │
│         │ Deduplicate      │  pipeline = 'diy_website'                   │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ email verification:       │  Verify discovered emails                    │
│         │ Email Verify     │  Only 'valid'/'accept_all' proceed          │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         │ AI PERSONALISE   │  Anti-slop framework enforced               │
│         │ Top leads        │  "DIY upgrade" templates only               │
│         │ score 6+         │  Includes actual PageSpeed score            │
│         │                  │  + specific issues found in audit           │
│         │                  │  + call scripts                             │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ Check Suppression│  Skip unsubscribed/bounced/complained       │
│         └──────────┬───────┘                                             │
│                    ↓                                                     │
│         ┌──────────────────┐                                             │
│         │ Instantly API:   │  Push to Instantly campaign                  │
│         │ Add leads +      │  Handles sending, warmup, rotation          │
│         │ Log to Supabase  │  + Log to email_audit_log                   │
│         │ + audit trail    │  Set follow_up_due = +3 days                │
│         └──────────────────┘                                             │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│           n8n Workflow 3: Follow-Up Sequence (Daily 9am Mon-Fri)         │
│                                                                          │
│  ┌─────────────────────┐                                                 │
│  │ Supabase: Query     │  WHERE status IN ('emailed','followed_up_1',    │
│  │ leads needing       │  'followed_up_2')                               │
│  │ follow-up           │  AND responded_at IS NULL                       │
│  │                     │  AND follow_up_due <= today                     │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ Code: Determine     │  follow_up_count = 0 → Day 3 follow-up #1      │
│  │ which follow-up     │  follow_up_count = 1 → Day 7 follow-up #2      │
│  │ stage + template    │  follow_up_count = 2 → Day 14 final follow-up  │
│  │                     │  follow_up_count >= 3 → mark 'no_response'     │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ AI: Generate        │  Personalised follow-up (not generic)           │
│  │ follow-up email     │  References original email + any new context    │
│  │ (anti-slop rules)   │  Different angle each time (see templates)      │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ Instantly API:      │  Push follow-up via Instantly                    │
│  │ Send follow-up      │  Update Supabase:                               │
│  │                     │    follow_up_count++                             │
│  │                     │    last_follow_up_at = now                       │
│  │                     │    follow_up_due = +4 or +7 days                │
│  │                     │    status = 'followed_up_N'                      │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ Log stats           │  Track in lead_pipeline_runs                    │
│  └─────────────────────┘                                                 │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│         n8n Workflow 4: Google Sheets Sync (Daily 8:30am)                │
│                                                                          │
│  ┌─────────────────────┐                                                 │
│  │ Supabase: Query     │  All leads with status != 'new'                 │
│  │ outreach leads      │  (i.e. all contacted leads)                     │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ Code: Format for    │  Columns: Business | Phone | Email | Score |    │
│  │ spreadsheet         │  Source | Pipeline | Status | Emailed Date |    │
│  │                     │  Last Contact | Next Follow-Up | Notes          │
│  └──────────┬──────────┘                                                 │
│             ↓                                                            │
│  ┌─────────────────────┐                                                 │
│  │ Google Sheets:      │  Write to "Lead Outreach" tab                   │
│  │ Overwrite tab       │  in Mycelium AI CRM sheet                       │
│  └─────────────────────┘                                                 │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│         n8n Workflow 5: Daily Digest (8:00am)                            │
│                                                                          │
│  Combines results from Pipeline A + Pipeline B into one morning email:   │
│                                                                          │
│  Section 1: "20 Leads Emailed This Morning"                              │
│    - 10 from Pipeline A (no website) + 10 from Pipeline B (DIY website)  │
│    - Per lead: score, phone, suburb, source, call script                 │
│                                                                          │
│  Section 2: "Follow-Ups Due Today"                                       │
│    - Leads emailed 3/7 days ago who haven't responded                    │
│    - Phone + original context for warm call                              │
│                                                                          │
│  Section 3: "Replies Received Yesterday"                                 │
│    - Any leads who replied (manual check reminder)                       │
│                                                                          │
│  Section 4: "Pipeline Stats"                                             │
│    - Leads found, new vs duplicates, emails sent, follow-ups sent        │
│    - A/B variant performance (after 2+ weeks)                            │
│    - Conversion funnel: emailed → responded → call booked → converted    │
└──────────────────────────────────────────────────────────────────────────┘

                         ↕

┌─────────────────────────────────────────────────────────────────────┐
│                     Supabase: leads table                           │
│                                                                     │
│  id | business_name | phone | email | category | address | suburb  │
│  postcode | website | google_reviews | score | source | pipeline   │
│  abn | registration_date | hipages_jobs | status | notes           │
│  diy_platform | pagespeed_score | pagespeed_mobile | seo_issues    │
│  has_ssl | email_sent | email_variant | emailed_at                  │
│  follow_up_count | follow_up_due | last_follow_up_at               │
│  created_at | contacted_at | responded_at | converted_at           │
└─────────────────────────────────────────────────────────────────────┘

                         ↕

┌─────────────────────────────────────────────────────────────────────┐
│             Google Sheets: "Lead Outreach" tab (sync)               │
│                                                                     │
│  Business | Phone | Email | Score | Source | Pipeline | Status      │
│  Emailed Date | Last Contact | Next Follow-Up | Notes               │
│  (Updated daily at 8:30am from Supabase)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Supabase Schema

### Table: `leads`

```sql
CREATE TABLE leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Business info
  business_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  category TEXT,
  address TEXT,
  suburb TEXT,
  postcode TEXT,
  state TEXT DEFAULT 'WA',
  website TEXT,

  -- Pipeline classification
  pipeline TEXT NOT NULL DEFAULT 'no_website',  -- 'no_website' or 'diy_website'
  source TEXT NOT NULL,  -- 'google_maps', 'abr', 'hipages', 'truelocal', 'yellowpages', 'facebook', 'expired_domain', 'google_ads_transparency', 'manual'

  -- Scoring signals (shared)
  google_reviews INTEGER DEFAULT 0,
  google_rating NUMERIC(2,1),
  hipages_jobs INTEGER DEFAULT 0,
  abn TEXT,
  registration_date DATE,
  has_meta_ads BOOLEAN DEFAULT FALSE,
  website_is_facebook BOOLEAN DEFAULT FALSE,

  -- DIY website signals (Pipeline B only)
  diy_platform TEXT,  -- 'wix', 'squarespace', 'weebly', 'wordpress_com', 'godaddy', 'jimdo', NULL if no website
  pagespeed_score INTEGER,  -- 0-100 (Google PageSpeed desktop)
  pagespeed_mobile INTEGER,  -- 0-100 (Google PageSpeed mobile)
  core_web_vitals JSONB,  -- {lcp: 4.2, fid: 0.3, cls: 0.15}
  has_ssl BOOLEAN,
  has_meta_description BOOLEAN,
  has_h1 BOOLEAN,
  mobile_friendly BOOLEAN,
  seo_issues JSONB,  -- ["missing_meta_desc", "no_h1", "no_alt_text", "broken_contact_form"]
  domain_expired BOOLEAN DEFAULT FALSE,
  running_google_ads BOOLEAN DEFAULT FALSE,

  -- Scoring
  score INTEGER DEFAULT 0,
  score_breakdown JSONB,

  -- Pipeline tracking
  status TEXT DEFAULT 'new',
  -- Statuses: 'new', 'emailed', 'followed_up_1', 'followed_up_2', 'followed_up_3',
  --           'responded', 'call_booked', 'converted', 'no_response', 'not_interested', 'dead'
  notes TEXT,

  -- Email discovery + verification
  email_source TEXT,  -- 'google_maps', 'company_website', 'linkedin', 'hunter_io', 'abr', 'facebook'
  email_source_url TEXT,  -- specific URL where email was found (legal defence)
  email_found_at TIMESTAMPTZ,  -- when email was discovered
  email_verified BOOLEAN DEFAULT FALSE,  -- email verification verification passed
  email_verification_status TEXT,  -- 'valid', 'invalid', 'accept_all', 'unknown'

  -- Auto-email tracking
  email_sent BOOLEAN DEFAULT FALSE,
  email_variant TEXT,  -- A/B test variant
  email_subject TEXT,
  email_body TEXT,
  call_script TEXT,  -- AI-generated call script with talking points
  emailed_at TIMESTAMPTZ,
  sending_domain TEXT,  -- which outreach domain sent the email
  instantly_lead_id TEXT,  -- Instantly's internal ID for this lead

  -- Follow-up tracking
  follow_up_count INTEGER DEFAULT 0,
  follow_up_due DATE,
  last_follow_up_at TIMESTAMPTZ,
  last_contact_date DATE,  -- Updated whenever ANY contact happens (email, call, follow-up)
  next_contact_date DATE,  -- Calculated: next follow-up or next call date

  -- Competitor context (enrichment)
  competitors_with_website INTEGER,
  competitors_total INTEGER,
  top_review_quote TEXT,  -- Best Google review quote for personalisation

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  contacted_at TIMESTAMPTZ,  -- When Aaron called
  responded_at TIMESTAMPTZ,  -- When lead replied (email or call)
  converted_at TIMESTAMPTZ,

  -- Deduplication (phone can be NULL for some sources, so also dedupe on business_name + suburb)
  UNIQUE(phone),
  UNIQUE(abn)
);

-- Indexes
CREATE INDEX idx_leads_created_status ON leads(created_at, status);
CREATE INDEX idx_leads_score ON leads(score DESC);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_pipeline ON leads(pipeline);
CREATE INDEX idx_leads_follow_up ON leads(follow_up_due) WHERE follow_up_due IS NOT NULL AND status IN ('emailed', 'followed_up_1', 'followed_up_2');
CREATE INDEX idx_leads_email_variant ON leads(email_variant) WHERE email_variant IS NOT NULL;
CREATE INDEX idx_leads_diy_platform ON leads(diy_platform) WHERE diy_platform IS NOT NULL;
CREATE INDEX idx_leads_next_contact ON leads(next_contact_date) WHERE next_contact_date IS NOT NULL;

-- Partial unique index for dedup when phone is NULL (by business name + suburb)
CREATE UNIQUE INDEX idx_leads_name_suburb ON leads(lower(business_name), lower(suburb)) WHERE phone IS NULL AND abn IS NULL;
```

### Table: `lead_pipeline_runs`

```sql
CREATE TABLE lead_pipeline_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  run_date DATE NOT NULL,
  source TEXT NOT NULL,
  leads_found INTEGER DEFAULT 0,
  leads_new INTEGER DEFAULT 0,
  leads_duplicate INTEGER DEFAULT 0,
  errors TEXT,
  run_duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Lead Scoring Logic

### Pipeline A Scorer — "No Website" Leads

```javascript
// n8n Code Node: Lead Scorer (Pipeline A)
// Input: normalised lead object (no website)
// Output: lead object with score + score_breakdown

function scoreNoWebsiteLead(lead) {
  let score = 0;
  const breakdown = {};

  // Signal 1: New business registration (ABR source) — timing advantage
  if (lead.registration_date) {
    const daysSinceReg = Math.floor(
      (Date.now() - new Date(lead.registration_date)) / (1000 * 60 * 60 * 24)
    );
    if (daysSinceReg <= 14) {
      score += 3;
      breakdown.new_business = '+3 (registered < 14 days ago)';
    } else if (daysSinceReg <= 30) {
      score += 2;
      breakdown.new_business = '+2 (registered < 30 days ago)';
    } else if (daysSinceReg <= 90) {
      score += 1;
      breakdown.new_business = '+1 (registered < 90 days ago)';
    }
  }

  // Signal 2: Google reviews (established + growing = budget to spend)
  if (lead.google_reviews >= 20) {
    score += 3;
    breakdown.reviews = '+3 (20+ reviews — established, ready to invest)';
  } else if (lead.google_reviews >= 10) {
    score += 2;
    breakdown.reviews = '+2 (10+ reviews — growing)';
  } else if (lead.google_reviews >= 5) {
    score += 1;
    breakdown.reviews = '+1 (5+ reviews)';
  }

  // Signal 3: HiPages activity (proves they're actively seeking work)
  if (lead.hipages_jobs >= 20) {
    score += 2;
    breakdown.hipages = '+2 (20+ HiPages jobs — very active)';
  } else if (lead.hipages_jobs >= 10) {
    score += 1;
    breakdown.hipages = '+1 (10+ HiPages jobs)';
  }

  // Signal 4: Website is just a Facebook page (knows they need web presence)
  if (lead.website_is_facebook) {
    score += 1;
    breakdown.facebook_only = '+1 (website is Facebook page — knows they need one)';
  }

  // Signal 5: High-value trade category
  const highValue = [
    'plumber', 'electrician', 'builder', 'roofer', 'concreter',
    'landscaper', 'pool', 'painter', 'fencer', 'carpenter',
    'pest control', 'cleaner', 'air conditioning', 'solar',
    'bore', 'drilling', 'excavation', 'demolition'
  ];
  const catLower = (lead.category || '').toLowerCase();
  if (highValue.some(hv => catLower.includes(hv))) {
    score += 1;
    breakdown.high_value_category = '+1 (high-value trade)';
  }

  // Signal 6: Seasonal timing bonus
  const month = new Date().getMonth() + 1;
  const seasonalBoost = {
    'landscap': [8, 9, 10, 11], 'pool': [8, 9, 10, 11],
    'air con': [9, 10, 11, 12], 'solar': [1, 2, 3, 9, 10, 11],
    'pest': [9, 10, 11, 12, 1, 2], 'clean': [1, 2, 11, 12],
  };
  for (const [keyword, months] of Object.entries(seasonalBoost)) {
    if (catLower.includes(keyword) && months.includes(month)) {
      score += 1;
      breakdown.seasonal = '+1 (seasonal timing match)';
      break;
    }
  }

  // Signal 7: Multi-source confirmation (found on multiple platforms = real business)
  if (lead.found_on_sources && lead.found_on_sources.length > 1) {
    score += 1;
    breakdown.multi_source = '+1 (found on multiple platforms)';
  }

  // Signal 8: Residential address (credit: Aaron's girlfriend)
  // Home-based businesses are owner-operated, no marketing support = ideal lead
  if (lead.address_type === 'residential') {
    score += 2;
    breakdown.residential = '+2 (residential address — likely owner-operated)';
  }

  return { ...lead, score: Math.min(score, 10), score_breakdown: breakdown };
}
```

### Pipeline B Scorer — "DIY Website" Leads

```javascript
// n8n Code Node: Lead Scorer (Pipeline B)
// Input: lead with DIY website + audit data
// Output: lead with score + score_breakdown

function scoreDiyWebsiteLead(lead) {
  let score = 0;
  const breakdown = {};

  // Signal 1: PageSpeed score (worse = more opportunity)
  if (lead.pagespeed_score !== null) {
    if (lead.pagespeed_score < 30) {
      score += 3;
      breakdown.pagespeed = `+3 (PageSpeed ${lead.pagespeed_score}/100 — terrible)`;
    } else if (lead.pagespeed_score < 50) {
      score += 2;
      breakdown.pagespeed = `+2 (PageSpeed ${lead.pagespeed_score}/100 — poor)`;
    } else if (lead.pagespeed_score < 70) {
      score += 1;
      breakdown.pagespeed = `+1 (PageSpeed ${lead.pagespeed_score}/100 — mediocre)`;
    }
  }

  // Signal 2: Mobile responsiveness (huge for tradies — customers search on phone)
  if (lead.mobile_friendly === false) {
    score += 2;
    breakdown.mobile = '+2 (not mobile-friendly — losing phone searchers)';
  }

  // Signal 3: No SSL (HTTP not HTTPS)
  if (lead.has_ssl === false) {
    score += 1;
    breakdown.ssl = '+1 (no SSL — browser shows "Not Secure" warning)';
  }

  // Signal 4: SEO issues
  const seoIssues = lead.seo_issues || [];
  if (seoIssues.length >= 3) {
    score += 2;
    breakdown.seo = `+2 (${seoIssues.length} SEO issues found)`;
  } else if (seoIssues.length >= 1) {
    score += 1;
    breakdown.seo = `+1 (${seoIssues.length} SEO issue(s) found)`;
  }

  // Signal 5: Google reviews (established business = budget)
  if (lead.google_reviews >= 20) {
    score += 2;
    breakdown.reviews = '+2 (20+ reviews — established, can afford upgrade)';
  } else if (lead.google_reviews >= 10) {
    score += 1;
    breakdown.reviews = '+1 (10+ reviews)';
  }

  // Signal 6: Running Google Ads (already spending on marketing = has budget + mindset)
  if (lead.running_google_ads) {
    score += 2;
    breakdown.ads = '+2 (running Google Ads — marketing-minded, has budget)';
  }

  // Signal 7: High-value trade category
  const highValue = [
    'plumber', 'electrician', 'builder', 'roofer', 'concreter',
    'landscaper', 'pool', 'painter', 'fencer', 'carpenter',
    'pest control', 'cleaner', 'air conditioning', 'solar',
    'bore', 'drilling', 'excavation', 'demolition'
  ];
  const catLower = (lead.category || '').toLowerCase();
  if (highValue.some(hv => catLower.includes(hv))) {
    score += 1;
    breakdown.high_value_category = '+1 (high-value trade)';
  }

  // Signal 8: Expired domain (had a site, lost it — proven intent)
  if (lead.domain_expired) {
    score += 2;
    breakdown.expired = '+2 (domain expired — had website before, needs new one)';
  }

  // Signal 9: Residential address (credit: Aaron's girlfriend)
  // Home-based businesses are owner-operated, no marketing support = ideal lead
  if (lead.address_type === 'residential') {
    score += 2;
    breakdown.residential = '+2 (residential address — likely owner-operated)';
  }

  return { ...lead, score: Math.min(score, 10), score_breakdown: breakdown };
}
```

---

## Data Source Details

### PIPELINE A SOURCES (No Website)

### Source 1: Google Maps — No Website Filter (Apify)

**Actor:** `apify/google-maps-scraper` (or `xmiso_scrapers/businesses-without-websites-leads-scraper`)

**Input config:**
```json
{
  "searchStringsArray": [
    "plumber Perth", "electrician Perth", "builder Perth",
    "landscaper Perth", "cleaner Perth", "painter Perth",
    "roofer Perth", "pest control Perth", "air conditioning Perth",
    "fencer Perth", "concreter Perth", "carpenter Perth"
  ],
  "maxCrawledPlacesPerSearch": 50,
  "language": "en",
  "deeperCityScrape": false,
  "onePerQuery": false
}
```

**Post-processing:**
- Filter: `website` is empty OR contains `facebook.com`
- Flag `website_is_facebook = true` if website contains `facebook.com`
- Normalise phone to Australian format (`0X XXXX XXXX`)
- **Website Existence Checker (3-layer verification):** Runs after normalisation, before scoring. See `HOW-plans/2026-03-21-website-existence-checker.md` and `scripts/lead-pipeline/website-checker.js`. Layer 1: URL pattern check (free). Layer 2: Google search via Apify (batched, ~$0.001/search). Layer 3: ABN→domain check (free). If website found → reclassify to Pipeline B. If professional site → suppress. Eliminates ~20-30% false positive rate from Google Maps "no website" data.

**Cadence:** Daily Mon-Fri, rotating 3-4 categories per day to control costs.
**Cost estimate:** ~$15-25/mo (Apify).

### Source 2: ABR API — New WA Registrations (Free)

**Endpoint:** `https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx`
**Method:** `SearchByRegistrationEvent` (SOAP API)
**ABR GUID:** Configured in `.env` (added 2026-03-19)

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `registrationYear` | Current year |
| `registrationMonth` | Current month |
| `registrationDay` | Yesterday |
| `state` | WA |
| `postcode` | 6000-6999 (Perth metro + surrounds) |
| `authenticationGuid` | `ABR_GUID` from `.env` |

**Post-processing:**
- Parse XML response → extract ABN, business name, entity type, postcode, registration date
- Filter by Perth metro postcodes (6000-6999)
- Cross-reference ABN against existing Supabase leads
- New registrations = Pipeline A (they definitely don't have a website yet)

**Cadence:** Daily Mon-Fri.
**Cost:** Free. No rate limits for reasonable usage.
**Fallback:** ABR bulk extract (weekly XML from data.gov.au) if SOAP is cumbersome.

### Source 3: HiPages (Apify)

**Actor:** `abotapi/hipages-business-scraper` (or `parsedom/hipages-lead-scraper`)

**Post-processing:**
- Filter: `website` is empty AND `jobsCompleted >= 10`
- Businesses with 10+ HiPages jobs but no website = actively getting work, ready to grow

**Cadence:** Weekly (Monday only — data changes slowly).
**Cost estimate:** ~$8-20/mo.

### Source 4: TrueLocal + Yellow Pages (Apify)

**Actors:**
- TrueLocal: `ecomscrape/truelocal-business-search-scraper`
- Yellow Pages AU: `lead.gen.labs/yellow-pages-australia-business-lead-generator`

**Why these matter:** Most competitors only scrape Google Maps. These directories capture traditional businesses that may not have optimised their Google listing — or may not be on Google Maps at all. Yellow Pages especially captures older businesses that grew up pre-internet.

**Post-processing:**
- Filter: no website listed, OR website is just Facebook
- Cross-reference against existing Supabase leads (dedupe by phone)
- Normalise to lead schema

**Cadence:** Weekly (Tuesday — stagger with HiPages Monday).
**Cost estimate:** ~$5-15/mo (Apify).

### Source 5: Facebook Business Pages — No Website (Apify)

**Actor:** `apify/facebook-pages-scraper`

**Search strategy:**
- Search: "[category] Perth" on Facebook Pages
- Filter: business pages with 50+ followers (real businesses, not abandoned pages)
- Filter: no website in page info, OR website field = facebook.com URL
- Extract: business name, phone, address, category, follower count

**Why this matters:** Heaps of small businesses — especially newer ones — run entirely through Facebook. They post regularly, reply to comments, but have zero web presence. These are businesses that KNOW they need to be online but haven't taken the website step yet.

**Cadence:** Weekly (Wednesday).
**Cost estimate:** ~$5-10/mo (Apify).

---

### PIPELINE B SOURCES (DIY Website)

### Source 6: Google Maps — HAS Website Filter + Platform Detection

**Same Apify actor as Source 1**, but with opposite filter:
- Filter: `website` IS NOT empty AND does NOT contain `facebook.com`
- Then: HTTP request to each website URL to fingerprint the platform

**Platform Detection Logic (n8n Code node):**
```javascript
// Fingerprint a website's platform by checking HTML, scripts, and DNS
async function detectPlatform(url) {
  const response = await fetch(url, { redirect: 'follow', timeout: 10000 });
  const html = await response.text();
  const headers = response.headers;

  // Check meta generator tag
  const generator = html.match(/<meta[^>]*name=["']generator["'][^>]*content=["']([^"']+)["']/i);

  // Platform signatures
  const signatures = {
    wix: [
      /wix\.com/i.test(html),
      /X-Wix-/i.test(JSON.stringify(Object.fromEntries(headers))),
      /_wix_browser_sess/i.test(html),
    ],
    squarespace: [
      /squarespace\.com/i.test(html),
      /Squarespace/i.test(generator?.[1] || ''),
      /sqsp/i.test(html),
    ],
    weebly: [
      /weebly\.com/i.test(html),
      /Weebly/i.test(generator?.[1] || ''),
    ],
    wordpress_com: [
      // wordpress.COM (hosted) not wordpress.ORG (self-hosted)
      /s[0-9]\.wp\.com/i.test(html),
      /wordpress\.com/i.test(html),
      // Self-hosted WordPress with default theme = also a DIY signal
      /flavor=flavor_flavor/i.test(html) && /flavors\/starter/i.test(html),
    ],
    godaddy: [
      /godaddy\.com/i.test(html),
      /GoDaddy/i.test(generator?.[1] || ''),
      /img1\.wsimg\.com/i.test(html),
    ],
    jimdo: [
      /jimdo\.com/i.test(html),
      /Jimdo/i.test(generator?.[1] || ''),
    ],
  };

  for (const [platform, checks] of Object.entries(signatures)) {
    if (checks.some(Boolean)) return platform;
  }
  return null; // Not a DIY platform (professionally built or unknown)
}
```

**Post-processing:**
- Only keep leads where `diy_platform` is NOT null (confirmed DIY site)
- For each: run Google PageSpeed API audit (see below)

**Cadence:** Daily Mon-Fri (same Apify run as Source 1 — just split the results).
**Cost:** No additional Apify cost (same scrape, different filter).

### Source 7: Expired .au Domains

**Data source:** `expireddomains.net` filtered for `.com.au` and `.au` TLDs

**How it works:**
1. Scrape or download the daily .au domain drop list
2. Filter by business-sounding names (exclude personal blogs, generic domains)
3. Check Wayback Machine for the last cached version — was it a real business?
4. Cross-reference with ABR (if domain contained a business name, the ABN might still be active)
5. If the ABN is active but the domain expired → they need a new website

**Why this matters:** These businesses HAD a website and lost it. They've already proven they care about web presence. The pitch: "Your old website at [domain] went offline — I can get you back up and running this week."

**Cadence:** Daily.
**Cost:** Free (expireddomains.net is free to browse; scraping may need Apify actor).

### Source 8: Google Ads Transparency Center

**URL:** `adstransparency.google.com`

**How it works:**
1. Search for businesses running Google Ads in Perth service categories
2. For each: check their landing page URL
3. Run platform detection (Source 6 logic) on the landing page
4. If DIY platform detected → they're spending money on ads but sending traffic to a rubbish site

**Why this matters:** These businesses are ALREADY spending money on marketing. They have budget and they have the mindset. But they're wasting their ad spend by sending clicks to a slow Wix site. The pitch: "You're spending $X/month on Google Ads but your landing page scores 28/100 on speed. That means most of your ad clicks bounce before they see your page. I can fix that."

**Cadence:** Weekly (Thursday — data doesn't change daily).
**Cost:** Free (public data). May need Apify actor for automated scraping.
**Note:** No official API — implementation may require custom scraper or manual process initially.

---

### Google PageSpeed Insights API (Used by Pipeline B)

**API:** `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
**Free tier:** 25,000 queries/day (more than enough)
**No API key required** for basic usage (rate-limited but generous)

**Fields extracted per website:**
```json
{
  "pagespeed_score": 34,
  "pagespeed_mobile": 22,
  "core_web_vitals": {
    "lcp": 4.2,
    "fid": 0.3,
    "cls": 0.15
  },
  "has_ssl": true,
  "has_meta_description": false,
  "has_h1": true,
  "mobile_friendly": false,
  "seo_issues": ["missing_meta_desc", "no_alt_text", "slow_lcp"]
}
```

**Implementation:** n8n HTTP Request node → Google PageSpeed API → Code node to extract scores

---

## n8n Workflow Structure

### Workflow 1: Pipeline A — "No Website" Leads

```
Nodes (in order):

1. [Cron Trigger] — 6:00am AWST Mon-Fri
     ↓
2. [Branch] — 5 parallel branches:
     ├─ Branch A: Google Maps (no website filter)
     │    [Apify: Run Actor] → [Wait] → [Code: Filter no-website] → [Code: Normalise]
     │
     ├─ Branch B: ABR API (daily)
     │    [HTTP Request: ABR SOAP] → [XML Parse] → [Code: Filter Perth postcodes] → [Code: Normalise]
     │
     ├─ Branch C: HiPages (Monday only)
     │    [IF: Monday] → [Apify: Run Actor] → [Wait] → [Code: Filter] → [Code: Normalise]
     │
     ├─ Branch D: TrueLocal + Yellow Pages (Tuesday only)
     │    [IF: Tuesday] → [Apify: Run Actors] → [Wait] → [Code: Filter no-website] → [Code: Normalise]
     │
     └─ Branch E: Facebook Business Pages (Wednesday only)
          [IF: Wednesday] → [Apify: Run Actor] → [Wait] → [Code: Filter] → [Code: Normalise]
     ↓
3. [Merge] → [Code: Lead Scorer A] → [Supabase: Upsert (pipeline='no_website')]
     ↓
4. [Code: Top 10 new leads score 6+ with email] → [AI Personalise (anti-slop)] → [Gmail: Send 10 at 7:00am]
     ↓
5. [Supabase: Log pipeline run]
```

### Workflow 2: Pipeline B — "DIY Website" Leads

```
Nodes (in order):

1. [Cron Trigger] — 6:00am AWST Mon-Fri
     ↓
2. [Branch] — 3 parallel branches:
     ├─ Branch A: Google Maps (HAS website)
     │    [Apify: Same run as Pipeline A] → [Code: Filter HAS website] → [Code: Normalise]
     │
     ├─ Branch B: Expired .au Domains (daily)
     │    [HTTP/Apify: Fetch drop list] → [Code: Filter .com.au business names] → [Code: Normalise]
     │
     └─ Branch C: Google Ads Transparency (Thursday only)
          [IF: Thursday] → [Apify/Scraper] → [Code: Extract landing pages] → [Code: Normalise]
     ↓
3. [Code: Platform Detection] — Fingerprint each website (Wix, Squarespace, etc.)
     ↓ (only DIY-platform sites continue)
4. [HTTP: Google PageSpeed API] — Audit each site (score, mobile, CWV, SEO)
     ↓
5. [Code: Lead Scorer B] → [Supabase: Upsert (pipeline='diy_website')]
     ↓
6. [Code: Top 10 new leads score 6+ with email] → [AI Personalise (anti-slop, upgrade templates)] → [Gmail: Send 10 at 7:15am]
     ↓
7. [Supabase: Log pipeline run]
```

### Workflow 3: Follow-Up Sequence (9am daily)

See architecture diagram above.

### Workflow 4: Google Sheets Sync (8:30am daily)

See architecture diagram above.

### Workflow 5: Daily Digest (8:00am)

See architecture diagram above.

### Email Digest Format

**Subject:** `[X] Leads Emailed Today — Top Score: [Y]/10`

**Body (HTML table):**

```
Morning! Here's what the pipeline did while you slept:

═══ NO-WEBSITE LEADS (10 emailed) ═══

| Score | Business | Category | Phone | Suburb | Source | Why |
|-------|----------|----------|-------|--------|--------|-----|
| 9/10  | Smith Plumbing | Plumber | 0412 345 678 | Malaga | ABR | New ABN (3 days ago), 12 reviews, no website |
| 7/10  | Coastal Electrical | Electrician | 0439 876 543 | Joondalup | Google Maps | 15 reviews, FB as website |

Call script for Smith Plumbing: "Hey Dave, Aaron here from Mycelium — I sent you an email
this morning about getting a website set up for Smith Plumbing. Your reviews are excellent,
especially that one about the emergency callout in Malaga. Figured a proper website would
help you turn those reviews into more bookings. Got 10 minutes?"

═══ DIY-WEBSITE LEADS (10 emailed) ═══

| Score | Business | Platform | PageSpeed | Phone | Suburb | Issues Found |
|-------|----------|----------|-----------|-------|--------|-------------|
| 8/10  | Pete's Pools | Wix | 28/100 | 0498 765 432 | Balcatta | No SSL, 8s mobile load, no meta desc |
| 7/10  | AllClear Pest | Squarespace | 41/100 | 0411 222 333 | Wanneroo | Broken contact form, not mobile-friendly |

Call script for Pete's Pools: "Hey Pete, Aaron here — I sent you a quick email this morning.
I ran a speed test on your website and it's scoring 28 out of 100. For context, that means
about half your visitors are leaving before the page loads. I rebuild sites like yours all
the time — usually triple the speed. Worth a quick chat?"

═══ FOLLOW-UPS DUE TODAY ═══
- Smith Electrical (emailed Day 3 ago) — follow-up #1 due
- Clean Co (emailed Day 7 ago) — follow-up #2 due

═══ PIPELINE STATS ═══
Found: 47 leads | New: 23 | Duplicates: 24 | Emails sent: 20 | Follow-ups sent: 5
A/B performance: Variant C (review quote) = 18% response rate vs Variant A (standard) = 9%
```

---

## Step-by-Step Tasks

### Step 0: Email Infrastructure Setup (Aaron — before implementation starts)
Register outreach domains, set up Instantly + email verification, configure DNS. This is the foundation — nothing works without it.

**Actions:**
1. **Register 2 outreach domains** (~$15/yr each via VentraIP or Crazy Domains):
   - `getmycelium.com.au` (or similar — looks legit, redirects to main site)
   - `myceliumweb.com.au` (or similar)
2. **Set up Google Workspace** on each outreach domain ($7/mo each):
   - Create `aaron@getmycelium.com.au` and `aaron@myceliumweb.com.au`
3. **Configure DNS for each domain:**
   - SPF record (TXT): `v=spf1 include:_spf.google.com ~all`
   - DKIM record (TXT) — generate via Google Workspace admin
   - DMARC record (TXT): `v=DMARC1; p=none; rua=mailto:dmarc@[domain]`
   - Verify all 3 pass at `mxtoolbox.com/emailhealth`
4. **Sign up for Instantly** ($47/mo at instantly.ai):
   - Connect both outreach domain inboxes
   - Start warmup immediately (Instantly handles this automatically)
   - Warmup runs 4 weeks before cold sends begin
5. **Sign up for email verification** ($49/mo at hunter.io):
   - Get API key, add `HUNTER_API_KEY` to `.env`
6. **Register at Google Postmaster Tools** (free, postmaster.google.com):
   - Add both outreach domains, verify ownership
7. **Set up domain redirects:**
   - Each outreach domain → redirect to `myceliumai.com.au`
8. **Add to `.env`:** `INSTANTLY_API_KEY`, `HUNTER_API_KEY`, `OUTREACH_DOMAIN_1`, `OUTREACH_DOMAIN_2`

**Timeline:** Do this NOW. Warmup takes 4 weeks. Start today = cold emails by mid-April.
**Cost:** ~$130/mo (Instantly $47 + Hunter $49 + 2× Workspace $14 + 2× domain ~$2.50/mo)
**Files affected:** `.env`, `.env.example`, DNS registrar

---

### Step 1: Create Supabase Tables
Create all 4 tables: `leads`, `lead_pipeline_runs`, `suppressed_emails`, `email_audit_log`.

**Actions:**
- Run the SQL via Supabase MCP or dashboard (schemas from sections above)
- Verify tables, columns, constraints, and indexes
- Test unique constraints with duplicate inserts

**Files affected:** Supabase database (remote)

---

### Step 2: ABR GUID Setup ✅ DONE
~~Aaron registers at abr.business.gov.au/Tools/WebServices to get a GUID.~~

**Completed 2026-03-19.** GUID added to `.env`. Still need to add `ABR_GUID` placeholder to `.env.example`.

---

### Step 3: Create ABR Query Script
Build a Python script that queries the ABR API for new WA registrations.

**Actions:**
- Create `scripts/lead-pipeline/abr-query.py`
- Script takes a date parameter (default: yesterday)
- Queries ABR SOAP API for registrations on that date in WA
- Filters by Perth postcodes (6000-6999)
- Outputs JSON: business name, ABN, postcode, entity type, registration date
- n8n calls this via Execute Command node

**Files affected:** `scripts/lead-pipeline/abr-query.py` (new)

---

### Step 4: Configure Apify Actors
Set up all Apify actors with correct inputs and cost controls.

**Actions:**
- Google Maps scraper: Perth trade categories, `maxCrawledPlacesPerSearch: 50`
- HiPages scraper: Perth location, 6 categories
- TrueLocal scraper: Perth trades, no-website filter
- Yellow Pages AU scraper: Perth trades
- Facebook Pages scraper: Perth business pages, 50+ followers
- Set `maxItems` limits on ALL actors
- Set Apify monthly budget cap to **$30** (increased from $20 for additional sources)
- Note all actor IDs for n8n configuration

**Files affected:** Apify console (remote)

---

### Step 5: Build Pipeline A — "No Website" n8n Workflow
Main scrape → enrich → score → email workflow for businesses without websites.

**Actions:**
- Create n8n workflow "Pipeline A — No Website Leads"
- Cron trigger: 6am AWST Mon-Fri
- 5 parallel branches: Google Maps, ABR, HiPages (Mon), TrueLocal+YP (Tue), Facebook (Wed)
- Normalisation Code nodes per branch
- Merge → Lead Scorer A → Supabase upsert (pipeline='no_website')
- Filter top 10 new leads score 6+ with email
- AI personalise (anti-slop framework, no-website templates)
- Gmail send 10 at 7:00am (30-60s spacing)
- Update Supabase: status, emailed_at, follow_up_due, last_contact_date, next_contact_date
- Log pipeline run
- Test with manual trigger first

**Files affected:** n8n (remote workflow)

---

### Step 6: Build Platform Detection + PageSpeed Audit Logic
The core of Pipeline B — fingerprint DIY websites and audit their quality.

**Actions:**
- Create platform detection Code node (see detection logic in Data Sources section)
- Create Google PageSpeed API integration (HTTP Request node)
- Extract: pagespeed_score, pagespeed_mobile, core_web_vitals, has_ssl, has_meta_description, mobile_friendly, seo_issues
- Test against 20 known Wix/Squarespace sites to validate detection accuracy
- Test against 20 professionally-built sites to confirm they're correctly filtered OUT

**Files affected:** n8n workflow (Code nodes + HTTP Request node)

---

### Step 7: Build Pipeline B — "DIY Website" n8n Workflow
Scrape → detect platform → audit → score → email workflow for businesses with bad DIY websites.

**Actions:**
- Create n8n workflow "Pipeline B — DIY Website Leads"
- Cron trigger: 6am AWST Mon-Fri
- 3 branches: Google Maps (has website), expired .au domains (daily), Google Ads Transparency (Thu)
- Platform detection → filter only DIY platforms
- PageSpeed audit for each
- Lead Scorer B → Supabase upsert (pipeline='diy_website')
- Filter top 10 new leads score 6+ with email
- AI personalise (anti-slop framework, upgrade-pitch templates with actual PageSpeed data)
- Gmail send 10 at 7:15am (30-60s spacing)
- Update Supabase
- Log pipeline run

**Files affected:** n8n (remote workflow)

---

### Step 8: Build Anti-AI-Slop Email Personaliser
The AI engine that generates cold emails that sound human.

**Actions:**
- Create `scripts/lead-pipeline/email-personaliser.js` (n8n Code node content)
- **Two prompt variants** — one for Pipeline A (no website), one for Pipeline B (DIY website upgrade)
- System prompt includes the FULL anti-slop framework (banned patterns + required patterns)
- For each lead, inject: business name, category, suburb, Google review quote, competitor count, score breakdown, (Pipeline B: PageSpeed score, specific issues found, platform name)
- Output: email_subject, email_body, call_script, email_variant per lead
- A/B variant assignment (random from template pool)
- Use `gpt-4o-mini` for cost efficiency (~$0.01 per 10 leads)
- **Test 10 sample outputs** and manually check: do they sound like Aaron? Would you delete this email or read it?

**Files affected:**
- `scripts/lead-pipeline/email-personaliser.js` (new)
- `scripts/lead-pipeline/email-templates.json` (new — includes Pipeline A and B templates)

---

### Step 9: Build Instantly Integration + Auto-Email Send
Push personalised emails to Instantly for sending via warmed outreach domains.

**Actions:**
- Create Instantly campaigns: "Pipeline A — No Website" and "Pipeline B — DIY Website"
- In both Pipeline n8n workflows, after AI personalisation:
  1. Check `suppressed_emails` table — skip any suppressed recipients
  2. Push leads to Instantly campaign via API (`POST /api/v1/campaign/add-leads-to-campaign`)
  3. Log to `email_audit_log` table (email_to, email_from, subject, type, pipeline, source, source_url, sending_domain)
  4. Update `leads` table: `email_sent`, `emailed_at`, `email_variant`, `email_subject`, `email_body`, `call_script`, `status='emailed'`, `follow_up_due=today+3`, `last_contact_date=today`, `next_contact_date=today+3`, `sending_domain`
- Instantly handles: sending from rotated outreach domains, spacing (60-120s), warmup alongside cold sends
- Spam Act 2003 compliance baked into every email footer: "If this isn't relevant, just reply 'stop' and I won't contact you again. | Aaron Parton, Mycelium AI, Perth WA"
- Set up Instantly webhook → n8n for reply detection (see Step 10a)
- Volume ramp per warmup schedule (see Email Infrastructure section)

**Files affected:** n8n workflows (HTTP Request to Instantly API), Supabase (status updates + audit log)

**Important — Gmail is NOT used for cold sending:**
- Gmail MCP = daily digest to Aaron + monitoring replies
- Instantly = all cold outreach + follow-ups via outreach domains
- Replies to outreach domains are forwarded to Aaron's main inbox by Instantly

---

### Step 10: Build Reply Detection + Bounce Handling
Detect when leads reply or bounce, and take immediate action.

**Actions:**
- **Reply detection:**
  - Set up Instantly webhook → n8n endpoint
  - When reply detected: update `leads` table (`responded_at = now()`, `status = 'responded'`), remove from follow-up queue, log in `email_audit_log`
  - If reply contains "stop"/"unsubscribe"/"remove": add to `suppressed_emails` table, update status to 'not_interested'
  - Send Aaron a notification email for positive replies (interested leads)
- **Bounce handling:**
  - Instantly webhook fires on bounce
  - Hard bounce: add email to `suppressed_emails` (reason='hard_bounce'), update lead status, NEVER retry
  - Soft bounce: retry up to 3x (Instantly handles this), then suppress
  - Log all bounces in `email_audit_log`
- **Out-of-office detection:**
  - If auto-reply detected, delay follow-up by 7 days past their stated return date
  - Parse return date from OOO message if possible

**Files affected:** n8n (new webhook workflow), Supabase (suppressed_emails, leads, email_audit_log)

---

### Step 10a: Build Health Monitoring Workflow
Auto-pause campaigns if deliverability metrics go red.

**Actions:**
- Create n8n workflow "Pipeline Health Check" (daily 7pm AWST)
- Query `email_audit_log` for 7-day rolling metrics:
  - Bounce rate = bounced / sent
  - Spam complaint rate (from Instantly API analytics)
  - Reply rate = replied / sent
  - Unsubscribe rate = unsubscribed / sent
- Compare against thresholds (see Health Monitoring table in Email Infrastructure section)
- If any metric exceeds auto-pause threshold:
  - Pause Instantly campaigns via API
  - Send alert email to Aaron: "Pipeline auto-paused: [metric] exceeded threshold ([value]). Review and restart manually."
- Include health summary in daily digest email (Section 4: Pipeline Stats)

**Files affected:** n8n (new workflow), Instantly API

---

### Step 11: Build Follow-Up Workflow
Multi-touch follow-up sequence for non-responders. Uses Instantly for sending (same warmed domains).

**Actions:**
- Create n8n workflow "Lead Pipeline — Follow-Up Sequence"
- Cron trigger: 9am daily Mon-Fri
- Query Supabase: leads where `follow_up_due <= today` AND `responded_at IS NULL` AND status IN ('emailed', 'followed_up_1', 'followed_up_2')
- **Check suppression list first** — skip any suppressed emails
- For each lead, determine follow-up stage:

| Follow-Up | When | Template | Angle |
|-----------|------|----------|-------|
| **#1** | Day 3 | Short check-in | "Did you get a chance to see my email?" |
| **#2** | Day 7 | Add value | "I ran a quick audit on your site — here's what I found" (Pipeline B) or "I mocked up what your site could look like" (Pipeline A) |
| **#3** | Day 14 | Soft close | "No worries if now's not the right time. I'll leave it with you." |
| **Stop** | Day 14+ | Mark `no_response` | No more emails. Lead stays in DB for future re-engagement. |

- AI generates each follow-up using anti-slop framework (different angle each time, references original email)
- Push follow-ups to Instantly via API (same warmed domains, same sender rotation)
- Log each follow-up in `email_audit_log`
- Update Supabase: `follow_up_count++`, `last_follow_up_at`, `follow_up_due` (next interval), `last_contact_date`, `next_contact_date`, `status`

**Files affected:** n8n (new workflow), Instantly API, Supabase (follow-up updates + audit log)

---

### Step 12: Build Google Sheets Sync
Live spreadsheet view of all outreach for Aaron's manual tracking.

**Actions:**
- Create n8n workflow "Lead Outreach — Sheets Sync"
- Cron trigger: 8:30am daily Mon-Fri
- Query Supabase: all leads with `status != 'new'` (all contacted leads)
- Format for spreadsheet:

| Column | Source |
|--------|--------|
| Business | business_name |
| Phone | phone |
| Email | email |
| Score | score |
| Source | source |
| Pipeline | pipeline ('No Website' / 'DIY Website') |
| Platform | diy_platform (Pipeline B only) |
| PageSpeed | pagespeed_score (Pipeline B only) |
| Status | status (human-readable) |
| Emailed Date | emailed_at |
| Last Contact | last_contact_date |
| Next Follow-Up | next_contact_date |
| Follow-Up # | follow_up_count |
| Notes | notes (Aaron can edit this column manually) |

- Write to new "Lead Outreach" tab in Mycelium AI CRM sheet
- **Important:** Preserve Aaron's manual Notes column — read existing notes before overwriting
- Add "Lead Outreach" and "Lead Outreach Lists" to the CRM Lists tab for dropdown validation

**Files affected:** n8n (new workflow), Google Sheets (new tab)

---

### Step 13: Build Daily Digest Email
Combined digest for both pipelines + follow-ups + stats.

**Actions:**
- Build HTML email template in n8n Code node
- Section 1: "No-Website Leads Emailed" (10 rows + call scripts)
- Section 2: "DIY-Website Leads Emailed" (10 rows + call scripts + PageSpeed data)
- Section 3: "Follow-Ups Due Today" (leads needing follow-up + phone + context)
- Section 4: "Pipeline Stats" (found, new, dupes, emails sent, follow-ups, A/B performance)
- Send to Aaron's Gmail at 8am

**Files affected:** n8n workflow (Code node + Gmail send)

---

### Step 14: Create Pipeline README
Document everything for maintainability.

**Actions:**
- Create `scripts/lead-pipeline/README.md`
- Document: architecture (both pipelines), all 8 data sources, scoring weights, anti-slop framework, how to modify categories, how to adjust scoring, cost monitoring, A/B testing, follow-up sequence, Google Sheets sync

**Files affected:** `scripts/lead-pipeline/README.md` (new)

---

### Step 15: Update Integration Catalog + .env.example
Add ABR API as an integration and update env placeholders.

**Actions:**
- Add ABR API section to `reference/integrations-catalog.md`
- Add `ABR_GUID` placeholder to `.env.example`
- Add Google PageSpeed API note to integrations catalog (free, no key needed)

**Files affected:** `reference/integrations-catalog.md`, `.env.example`

---

### Step 16: Update Context Files
Bring all project docs up to date.

**Actions:**
- Update `context/WHERE-current-data.md` with pipeline project status
- Update `context/lead-gen-strategy.md` with actual implementation details
- Update `context/outstanding-actions.md` — mark completed items
- Update `CLAUDE.md` if needed (Active Projects section)

**Files affected:** `context/WHERE-current-data.md`, `context/lead-gen-strategy.md`, `context/outstanding-actions.md`, possibly `CLAUDE.md`

---

### Step 17: Test & Tune
Run both pipelines manually, verify end-to-end.

**Actions:**
- Trigger Pipeline A manually → verify leads in Supabase with scores
- Trigger Pipeline B manually → verify platform detection + PageSpeed scores
- Check AI-generated emails: do they sound human? Would Aaron send this?
- Send test emails to Aaron's own email first (not real leads)
- Verify daily digest format and content
- Verify Google Sheets sync (Lead Outreach tab populates correctly)
- Trigger follow-up workflow → verify correct stage determination
- Check deduplication across all sources
- Review scoring — do high scores correlate with good prospects?
- Once confident: activate all workflows on cron
- **Week 1:** Monitor daily, check for errors, tune scoring
- **Week 2:** Review A/B variant performance, kill worst performers
- **Week 3:** Analyse conversion funnel (emailed → responded → called → converted)

---

## Validation Checklist

### Email Infrastructure (Step 0)
- [ ] Outreach domain 1 registered (e.g. `getmycelium.com.au`)
- [ ] Outreach domain 2 registered (e.g. `myceliumweb.com.au`)
- [ ] Google Workspace set up on both outreach domains
- [ ] SPF records configured and passing (verify at mxtoolbox.com)
- [ ] DKIM records configured and passing
- [ ] DMARC records configured (p=none initially)
- [ ] Instantly account created and both inboxes connected
- [ ] Instantly warmup running for 4+ weeks before cold sends
- [ ] email verification account created, API key in `.env`
- [ ] Google Postmaster Tools set up for both outreach domains
- [ ] Domain redirects: outreach domains → myceliumai.com.au
- [ ] `INSTANTLY_API_KEY`, `HUNTER_API_KEY` added to `.env`
- [ ] Outreach domain env vars added to `.env`

### Database Infrastructure
- [ ] Supabase `leads` table created with updated schema (includes DIY fields, pipeline, email source, verification)
- [ ] Supabase `lead_pipeline_runs` table created
- [ ] Supabase `suppressed_emails` table created
- [ ] Supabase `email_audit_log` table created
- [x] ABR GUID obtained and added to `.env` (2026-03-19)
- [ ] `ABR_GUID` placeholder added to `.env.example`
- [ ] All Apify actors configured with `maxItems` limits
- [ ] Apify monthly budget cap set to $30

### Pipeline A (No Website)
- [ ] ABR query script returns valid results for yesterday's WA registrations
- [ ] Apify Google Maps actor returns Perth businesses without websites
- [ ] Apify HiPages actor returns Perth trades with job counts
- [ ] Apify TrueLocal + Yellow Pages actors return Perth businesses
- [ ] Apify Facebook Pages actor returns Perth business pages
- [ ] Pipeline A n8n workflow runs end-to-end without errors
- [ ] Lead Scorer A scores correctly (manual check 10 leads)
- [ ] Top 10 leads selected and AI-personalised emails generated

### Pipeline B (DIY Website)
- [ ] Platform detection correctly identifies Wix, Squarespace, Weebly, WordPress.com, GoDaddy, Jimdo
- [ ] Platform detection correctly EXCLUDES professionally-built sites
- [ ] Google PageSpeed API returns scores for each detected DIY site
- [ ] SEO issues correctly extracted (meta desc, H1, alt text, SSL)
- [ ] Expired .au domain source returns business domains
- [ ] Google Ads Transparency source returns Perth businesses with ads
- [ ] Pipeline B n8n workflow runs end-to-end without errors
- [ ] Lead Scorer B scores correctly (manual check 10 leads)
- [ ] Upgrade-pitch emails include actual PageSpeed scores and specific issues

### Email Quality (Anti-AI-Slop)
- [ ] Generated emails use contractions (I'm, you're, don't)
- [ ] No emails start with "I hope this email finds you well" or similar
- [ ] No jargon (leverage, streamline, optimize, innovative)
- [ ] Each email contains one specific detail proving research (review quote, PageSpeed score, competitor count)
- [ ] All emails end with "Cheers, Aaron" (not "Best regards")
- [ ] Max 5-6 sentences per email
- [ ] CTA is low-commitment ("worth a look?" not "schedule a call")
- [ ] Call scripts contain specific talking points per lead
- [ ] Aaron reads 10 sample emails and confirms they sound like him

### Deliverability & Compliance
- [ ] Emails sent via Instantly (NOT Gmail MCP) through warmed outreach domains
- [ ] email verification verification runs on every email before sending (only 'valid'/'accept_all' proceed)
- [ ] Bounce rate stays below 1% after first week
- [ ] Spam complaint rate stays below 0.1% (check Google Postmaster Tools)
- [ ] Reply detection webhook fires correctly → stops follow-up sequence
- [ ] "Stop" replies trigger suppression across ALL outreach domains
- [ ] `suppressed_emails` table checked before every send
- [ ] `email_audit_log` captures every send with source documentation
- [ ] Health monitoring workflow auto-pauses campaigns when thresholds exceeded
- [ ] Every email includes Spam Act 2003 compliant footer (name, business, unsubscribe)

### Follow-Up & Tracking
- [ ] Follow-up workflow correctly identifies Day 3, 7, 14 leads
- [ ] Follow-ups also sent via Instantly (same warmed domains)
- [ ] Each follow-up uses a different angle (not same email again)
- [ ] Follow-ups stop after 3 attempts (Day 14 = mark no_response)
- [ ] Follow-ups stop immediately if reply detected
- [ ] `last_contact_date` and `next_contact_date` update correctly
- [ ] Google Sheets "Lead Outreach" tab populates with all contacted leads
- [ ] Spreadsheet preserves Aaron's manual Notes column
- [ ] Duplicates correctly skipped across all sources (run twice, second run = 0 new)

### Shared Systems
- [ ] Daily digest email arrives by 8am with both pipelines + follow-ups + health stats
- [ ] A/B variant assigned and logged per lead in Supabase
- [ ] Pipeline runs logged in `lead_pipeline_runs`
- [ ] All crons fire correctly: 6am (Pipelines A+B), 8am (Digest), 8:30am (Sheets sync), 9am (Follow-ups), 7pm (Health check)
- [ ] `reference/integrations-catalog.md` updated with ABR API + Instantly + email verification
- [ ] `context/WHERE-current-data.md` updated
- [ ] No secrets in tracked files

---

## Success Criteria

1. **Both pipelines run daily at 6am without manual intervention**
2. **Produces 30-60 new scored leads per day** across both pipelines (after deduplication)
3. **Scales from 20/day (week 5) to 100-150/day (week 8+)** via warmed outreach domains
4. **Daily digest with call scripts arrives by 8am** — both pipelines + follow-ups + health stats
5. **Follow-up emails sent automatically on Day 3, 7, 14 for non-responders** — stop on reply
6. **Google Sheets "Lead Outreach" tab updated daily** with status, last contact, next follow-up
7. **Emails pass the "would Aaron delete this?" test** — anti-slop framework produces genuinely human-sounding outreach
8. **Bounce rate stays below 1%** thanks to email verification verification
9. **Spam complaint rate stays below 0.1%** — auto-pause triggers if exceeded
10. **Reply detection stops follow-ups immediately** when someone responds
11. **Cross-domain suppression works** — unsubscribe from one domain = suppressed on all
12. **Full compliance audit trail** in `email_audit_log` — every send, bounce, unsubscribe documented
13. **A/B test data accumulates** — response rate queryable per variant after 2 weeks of sending
14. **Lead scores correlate with conversion potential** (validate after 2 weeks of outreach data)
15. **At cruise speed (100/day): 2% response rate = 40+ warm conversations/month → 4-6 new clients/month**
16. **Aaron's daily effort reduced to 30-40 minutes** of warm follow-up calls based on the morning digest

---

## Estimated Implementation Time

| Step | Time | Dependency |
|------|------|------------|
| Step 0: Email infrastructure (Aaron) | 2-3 hrs setup + 4 weeks warmup | None — **DO THIS FIRST** |
| Step 1: Supabase tables (all 4) | 30 min | None |
| Step 2: ABR GUID | ✅ Done | None |
| Step 3: ABR query script | 1-2 hrs | Step 2 |
| Step 4: Configure Apify actors (all 5+) | 1 hr | None |
| Step 5: Pipeline A n8n workflow | 2-3 hrs | Steps 1, 3, 4 |
| Step 6: Platform detection + PageSpeed audit | 2-3 hrs | None |
| Step 7: Pipeline B n8n workflow | 2-3 hrs | Steps 1, 4, 6 |
| Step 8: Anti-slop email personaliser | 2-3 hrs | None |
| Step 9: Instantly integration + auto-send | 1-2 hrs | Steps 0, 5, 7, 8 |
| Step 10: Reply detection + bounce handling | 1-2 hrs | Step 9 |
| Step 10a: Health monitoring | 1 hr | Step 10 |
| Step 11: Follow-up workflow | 1-2 hrs | Steps 9, 10 |
| Step 12: Google Sheets sync | 1 hr | Step 9 |
| Step 13: Daily digest email | 1-2 hrs | Steps 5, 7, 11 |
| Step 14: README | 30 min | All above |
| Step 15: Integration catalog + .env.example | 15 min | Step 0 |
| Step 16: Context updates | 15 min | All above |
| Step 17: Test & tune | 2-3 hrs | All above |
| **Total** | **~20-28 hours build** + **4 weeks warmup** | |

**Critical path:** Step 0 (email infrastructure) has a 4-week warmup. Start this immediately. Steps 1-8 can be built in parallel during the warmup period. By the time warmup completes, the pipeline is ready to send.

### Monthly Running Costs

| Service | Monthly Cost (AUD) | What It Does |
|---------|-------------------|-------------|
| Instantly | ~$73 | Warmup network (4M+ accounts), sender rotation, reply detection |
| Apify | ~$30 | Web scraping (Google Maps, HiPages, TrueLocal, YP, Facebook) |
| OpenAI | Already paying | Email personalisation via gpt-4o-mini |
| Google Workspace (×2) | ~$22 | Outreach domain inboxes |
| Outreach domains (×2) | ~$3.50 | myceliumweb.com.au + myceliumsites.com.au |
| Email verification | Free | Built-in SMTP check + confidence scoring (n8n Code node) |
| Supabase | Free | Database (free tier) |
| n8n | Existing | Workflow orchestration |
| Google PageSpeed API | Free | Website auditing |
| ABR API | Free | New business registrations |
| **Total** | **~$130 AUD/mo** | |

**ROI:** At cruise speed (100 emails/day × 22 days × 2% response = 44 conversations/month × 10% close = 4 clients). At $1,500/client average = **$6,000 revenue from $130 AUD spend = 46× ROI**.

---

## Follow-Up Email Templates

### Follow-Up #1 (Day 3) — Quick Check-In
```
Subject: Re: [original subject]

Hey [Name],

Sent you a note a few days ago about [Business Name]'s website — figured I'd follow up in case it got buried.

Happy to show you what I had in mind. No pressure either way.

Cheers,
Aaron
```

### Follow-Up #2 (Day 7) — Add Value

**Pipeline A version (no website):**
```
Subject: Re: [original subject]

Hey [Name],

Last follow-up from me — I actually mocked up a rough idea of what a site for [Business Name] could look like. Based on your [suburb] area and the kind of work you do.

If you're curious I'll send it through. If not, no worries at all.

Cheers,
Aaron
```

**Pipeline B version (DIY website):**
```
Subject: Re: [original subject]

Hey [Name],

Quick update — I ran a full audit on your site since I last emailed. Found a few things that are probably costing you enquiries:

[1-2 specific issues from audit, e.g. "Your contact form returns a 404 on mobile" or "Google's indexing 3 of your 8 pages"]

Happy to walk you through it if you're interested. 10 minutes max.

Cheers,
Aaron
```

### Follow-Up #3 (Day 14) — Soft Close
```
Subject: Re: [original subject]

Hey [Name],

Last one from me — don't want to be a pest. If a website isn't on your radar right now, totally get it.

If it ever is, my number's below. Happy to help whenever the timing's right.

Cheers,
Aaron
[phone]
```

---

## Future Enhancements (Not in This Plan)

- **Auto-SMS for 9+/10 leads** — instant text alert to Aaron for the hottest leads
- **CRM auto-sync** — push 8+/10 leads to Google Sheets CRM tab automatically (currently separate)
- **Weekly performance report** — conversion funnel by score band, source, pipeline, and A/B variant
- **LinkedIn enrichment** — find business owner's LinkedIn for DM outreach
- **Seek/Indeed monitoring** — businesses hiring = growth signal = +2 to score
- **Review response monitoring** — detect when a lead replies to an email (Gmail API search for thread)
- **Automatic re-engagement** — leads marked `no_response` 90+ days ago get a "checking back in" email
- **Multi-city expansion** — same pipeline for other Australian metros (Melbourne, Sydney, Brisbane)
- **Referral tracking** — when a converted client refers someone, auto-create a warm lead
- **Response framework** — when leads REPLY, Claude drafts a response in Aaron's tone (never auto-sends — Aaron reviews and sends manually)

---

## Notes

- **8 sources, 2 pipelines** is the key differentiator. Everyone scrapes Google Maps. Nobody combines ABR + expired domains + platform fingerprinting + PageSpeed auditing + anti-AI-slop email generation.
- The ABR API is the secret weapon. Reaching out within days of ABN registration is almost warm outreach — they're actively in setup mode.
- DIY website detection is the second secret weapon. Business owners who built their own Wix site have PROVEN they care about having a website. They just did it badly. That's a much warmer lead than "no website at all."
- The anti-slop framework is non-negotiable. If emails sound like AI, they get deleted. Strategic imperfection, specific details, and casual tone are what separate this from every other automated outreach system.
- **Follow-ups are where the money is.** "You don't have a lead problem. You have a follow-up problem." Three touches (Day 3, 7, 14) before giving up.
- Keep Apify costs controlled by rotating categories and staggering sources across weekdays.
- The scoring weights are starting values. After 2-3 weeks of outreach, analyse which scores actually convert and tune accordingly.
- **Corflute signs** (now ordered) will drive inbound leads that bypass the pipeline entirely — these go straight to CRM as warm leads.
- Google Sheets "Lead Outreach" tab gives Aaron a manual view he can check on his phone during lunch break. Supabase is the real database; the sheet is just a window.
