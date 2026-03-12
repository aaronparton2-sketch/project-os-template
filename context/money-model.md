# Money Model

> Core revenue model for Mycelium AI. Claude reads this to understand pricing, margins, upsell ladder, and unit economics. Update as pricing evolves.

**Last updated:** 2026-03-10

---

## How This Connects

- **business-info.md** — org overview and market position
- **strategy.md** — what we're optimising toward
- **WHERE-current-data.md** — tracks actual revenue and pipeline

---

## Revenue Goal

- **Target:** $10,000/month from website builds + growing monthly recurring revenue (MRR)
- **Stretch:** Scale to hire contractors (sales + AI devs) once MRR covers base costs
- **Lifestyle:** Flexible enough to work remotely (Bali, travel) while scaling

---

## Service Ladder (Upsell Sequence)

Clients enter at Tier 1. After delivery, offer Tier 2 upward until they say no.

### Tier 1 — Landing Page + Email Automation (Entry Product)

| Item | Current Price | Recommended Price | Notes |
|------|--------------|-------------------|-------|
| Upfront build fee | $770 | $1,800–$2,500 | Vibe-coded landing page + n8n webhook + contact form email. 3-4 hours of work. Australian market rate for custom-coded site + automation is $2,000–$4,000. |
| Monthly hosting + maintenance | $30/mo | $59–$79/mo | Hosting on Netlify/Vercel + basic maintenance. Industry standard $49–$99/mo. |
| Domain management | Included | $0 (baked into monthly) | Domain purchased on Aaron's GoDaddy. Transfers to client on request/termination. Cost ~$20-30/yr absorbed into monthly fee. |

**Effective hourly rate at current pricing:** $770 / 4hrs = ~$192/hr
**Effective hourly rate at recommended pricing:** $2,000 / 4hrs = $500/hr (but client perceives project value, not hourly)

**Sales approach:** Free website demo (basic/ugly version) shown in meeting → then show premium version (built in Lovable). Contrast drives conversion.

### Tier 2 — Google Sheet CRM + n8n Automation (First Upsell)

| Item | Current Price | Recommended Price | Notes |
|------|--------------|-------------------|-------|
| Setup fee | Not yet priced | $500–$800 | Google Sheet CRM + n8n workflow. 1-2 hours work. Price against what CRM software costs them ($50-100/mo for HubSpot/Zoho). |
| Monthly maintenance | Not yet priced | $30–$50/mo | Ongoing support, tweaks, monitoring |

### Tier 3 — SEO Improvements (Second Upsell)

| Item | Current Price | Recommended Price | Notes |
|------|--------------|-------------------|-------|
| Initial SEO audit + setup | Not yet priced | $800–$1,500 | On-page SEO, Google Business Profile, meta tags, sitemap, analytics setup |
| Monthly SEO management | Not yet priced | $300–$500/mo | Content updates, keyword monitoring, monthly report. Aus market: $500–$2,000/mo for agencies. Price low to win, increase as results show. |

### Tier 4 — Paid Ad Management (Third Upsell)

| Item | Current Price | Recommended Price | Notes |
|------|--------------|-------------------|-------|
| Ad setup fee | Not yet priced | $500–$1,000 | Google Ads or Meta Ads account setup, initial campaign build |
| Monthly management | Not yet priced | $300–$500/mo OR 15-20% of ad spend | Whichever is greater. Industry standard is % of spend with a minimum floor. |
| Minimum ad spend recommendation | — | $500–$1,000/mo | Below this, results are too thin to justify management fees |

### Tier 5 — Custom Web Apps & Large Automations (Big Ticket)

| Item | Current Price | Recommended Price | Notes |
|------|--------------|-------------------|-------|
| Discovery + scoping | — | $500 (credited to build) | Paid discovery session. Credits toward build if they proceed. |
| Build fee | Project-based | $3,000–$15,000+ | Depends on scope. Always quoted after discovery. Contract required. |
| Monthly support | — | $100–$300/mo | Ongoing hosting, maintenance, support |

---

## Monthly Recurring Revenue (MRR) Stack

Every client who stays generates recurring revenue. This compounds:

| Service | Monthly per client |
|---------|-------------------|
| Hosting + maintenance | $59–$79 |
| CRM maintenance | $30–$50 |
| SEO management | $300–$500 |
| Ad management | $300–$500 |
| **Max MRR per client** | **$690–$1,130** |

**10 clients on full stack = $6,900–$11,300/mo recurring**
**20 clients on hosting only = $1,180–$1,580/mo recurring**

---

## Path to $10k/month

| Scenario | Websites/mo | Avg upfront | Monthly clients | Avg MRR/client | Total |
|----------|------------|-------------|-----------------|----------------|-------|
| Current pricing | 13 | $770 | 10 | $30 | $10,310 |
| Recommended pricing (conservative) | 4 | $2,000 | 15 | $79 | $9,185 |
| Recommended + upsells | 3 | $2,000 | 15 | $200 | $9,000 |
| Mature (6-12 months) | 2 | $2,500 | 25 | $250 | $11,250 |

**Key insight:** At recommended pricing, you need 3-4 websites per month (vs 13 at current pricing) to hit $10k. The MRR compounds — after 6 months of clients, recurring alone could cover $3,000-5,000/mo.

---

## Costs & Margins

| Cost | Monthly | Notes |
|------|---------|-------|
| Netlify/Vercel hosting | ~$0–$20 | Free tier covers most simple sites |
| GoDaddy domains | ~$3–$5/domain/mo amortised | ~$20-30/yr per domain |
| n8n | $20–$50 | Depending on plan/self-hosted |
| Stripe fees | 1.75% + $0.30 per transaction | Australian Stripe pricing |
| Tools (Lovable, etc.) | $20–$50/mo | Design/prototyping tools |
| PI Insurance (recommended) | ~$50–$80/mo | See risk analysis |
| **Total overhead** | **~$100–$250/mo** | Extremely lean |

**Gross margin:** ~85-95% on service revenue. Almost all profit at this stage.

---

## Pricing Principles

1. **Price on value, not hours.** Client pays for a working website + automation, not "4 hours of vibe coding."
2. **Always charge setup + monthly.** Setup covers your build time. Monthly creates the recurring flywheel.
3. **Never discount the monthly.** Discount the upfront if needed to close, but protect MRR.
4. **Upsell until they say no.** Every client interaction is a chance to offer the next tier.
5. **Review pricing quarterly.** As demand grows and you're closing >80% of leads, prices are too low.

---

## Process Flow

```
Lead Generation (YouTube, cold outreach, referrals)
    ↓
Discovery Call (15-30 min)
    ↓
Demo Meeting — show free (ugly) version, then premium version
    ↓
Client says yes → receives Stripe payment link
    ↓
Client ticks Terms of Service checkbox + pays upfront fee via Stripe
    ↓
Aaron buys domain on GoDaddy → deploys to Netlify/Vercel → sets up n8n webhook
    ↓
Aaron shares GitHub repo with client (full code access)
    ↓
Website live → client on monthly Stripe subscription
    ↓
Upsell sequence: CRM → SEO → Ads → Custom work
    ↓
Each upsell: new Stripe payment link + subscription updated
```

---

## Outstanding Pricing Decisions

- [ ] Finalise Tier 1 price point (test $1,800 vs $2,500 — could A/B test in sales calls)
- [ ] Set hourly rate for ad-hoc rework (recommended: $150–$200/hr AUD)
- [ ] Define "what's included" boundary for monthly hosting (e.g., "2 text/image changes per month included, additional at hourly rate")

---

_Update this file as pricing is tested and refined. Track actual close rates to calibrate._
