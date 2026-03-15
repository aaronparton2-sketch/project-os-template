# Business Info

> This file provides background on the organization or business you operate within. It sets the stage for understanding your role (personal-info.md) and strategic priorities (strategy.md).

---

## How This Connects

- **This file** establishes organizational context
- **personal-info.md** defines your role within this org
- **strategy.md** captures the goals you're driving toward
- **WHERE-current-data.md** tracks progress and informs decisions

---

## Organization Overview

**Mycelium AI** is an AI Automation Agency founded by Aaron Parton (mid-2025). Mycelium AI specialises in helping small to medium-sized businesses take full advantage of AI — beyond "rephrasing emails in ChatGPT." Services include automation workflows (n8n), custom software, AI education, and AI audits. Mission: help businesses automate tedious admin so they can focus on what they're great at. Revenue goal: $100k in 2026 (stretch, but achievable).

## Products / Services / Focus Areas

Core revenue model documented in detail: `context/money-model.md`

| Service | Type | Revenue Model |
|---------|------|---------------|
| Landing pages + email automation | Entry product | Upfront + monthly hosting |
| Google Sheet CRM + n8n workflows | Upsell | Setup fee + monthly |
| SEO improvements | Upsell | Audit fee + monthly management |
| Paid ad management | Upsell | Setup fee + monthly (or % of spend) |
| Custom web apps & large automations | Big ticket | Scoped project + monthly support |
| AI Education | Future/supplementary | TBD |
| AI Audits | Future/supplementary | TBD |

## Sales Process

1. Lead gen via YouTube, cold outreach, referrals
2. Discovery call (15-30 min)
3. Demo meeting — show free (ugly) website → then show premium version (built in Lovable). Contrast drives conversion.
4. Client receives Stripe payment link with embedded Terms of Service checkbox
5. Client ticks ToS box + pays upfront fee via Stripe
6. Aaron buys domain (GoDaddy) → deploys to Netlify/Vercel → sets up n8n webhook
7. Aaron shares GitHub repo with client (full code access — client owns their code)
8. Website live → client on monthly Stripe subscription for hosting/maintenance
9. Upsell ladder: CRM → SEO → Ads → Custom work (offer until they say no)

## Tech Stack

- **Frontend:** Vibe-coded sites (Lovable for prototyping/demos, deployed to Netlify/Vercel)
- **Backend automations:** n8n (webhooks, email, CRM workflows)
- **Domains:** GoDaddy (managed on Aaron's account, transferred to client on request)
- **Payments:** Stripe (payment links with embedded ToS checkbox — no separate contract signing). Stripe API integrated (read-only restricted key) for MRR tracking, payment status checks, and failed payment alerts. See `reference/integrations-catalog.md` for setup.
- **Contracts/Legal:** Terms of Service + Privacy Policy embedded in Stripe checkout. No separate contract template.
- **Code delivery:** GitHub repos shared with client (full access to their code)
- **CRM for clients:** Google Sheets + n8n
- **AI tools:** Claude Code, OpenAI API, Apify

## Stripe Data (Live — Read-Only API)

| Metric | Value | As of |
|--------|-------|-------|
| **Total customers** | 6 | 2026-03-15 |
| **Active subscriptions** | 5 | 2026-03-15 |
| **MRR** | $170.00 AUD | 2026-03-15 |
| **Failed payments (30 days)** | 1 (Form Society — $50, card blocked by Stripe fraud filter) | 2026-03-15 |

**Active subscribers:**
- Arturo Toalisa Acuna — $30/mo
- Andrew Bozier — $30/mo
- Grundy Drilling Company — $30/mo
- Euro System Carpet Cleaning — $30/mo
- Form Society — $50/mo (last payment failed — see outstanding actions)

*Update this section by asking Claude to re-run the Stripe check.*

## Current Active Project

_No active project. Use `/create-plan` to start one._

## Key Context

- Still early stages — 1-man band (Aaron)
- Currently working full-time in corporate (Perth, WA) — planning to exit and go all-in on Mycelium AI
- Market position: early/unknown; no significant inbound yet
- Leads come via cold outreach and referrals
- YouTube channel launched — posting ~fortnightly, goal is weekly then 2-3x/week post-corporate exit
- Target clients: small to medium businesses that aren't digitally technical
- Location: Perth, Western Australia

---

_Keep this high-level — enough to orient Claude, not a comprehensive company wiki._
