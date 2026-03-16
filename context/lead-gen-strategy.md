# Lead Generation Strategy

> How Mycelium AI generates leads. Based on Alex Hormozi's $100M Leads framework, adapted for a solo AI/web agency targeting local service businesses in Perth, Western Australia.

**Last updated:** 2026-03-16

---

## How This Connects

- **strategy.md** — overall business priorities
- **money-model.md** — what we sell once leads convert
- **business-info.md** — sales process and tech stack
- **reference/uploads/alfie-excalidraw-summary.md** — Alfie's lead gen approach (Google Maps + cold calling)
- **reference/uploads/ben-excalidraw-summary.md** — Ben's validation approach (cold walk-ins)

---

## The Problem (As of March 2026)

- Aaron works 9-5 in corporate. Limited time for lead gen.
- Lead sources so far: Google Maps cold calls (okay), driving past vans without websites (okay), warm network (exhausted).
- Need WAY more leads to build revenue to quit corporate.
- Perth service businesses are bombarded by web agencies — differentiation is critical.

---

## Hormozi's Core Framework ($100M Leads)

Every form of advertising falls into a 2x2 matrix:

|  | **1-to-1 (Private)** | **1-to-Many (Public)** |
|--|--|--|
| **Warm (Know You)** | 1. Warm Outreach | 2. Free Content |
| **Cold (Don't Know You)** | 3. Cold Outreach | 4. Paid Ads |

### Key Principles

1. **The Rule of 100:** Do 100 outreaches/day, OR 100 minutes of content/day, OR $100/day on ads. Every day. For 100 days. No excuses.
2. **The Value Equation:** Value = (Dream Outcome x Perceived Likelihood) / (Time Delay x Effort). Maximise the top, minimise the bottom.
3. **Make offers so good people feel stupid saying no.** A free website IS that offer.
4. **Give:Ask Ratio = 3.5:1.** Give value 3.5 times for every 1 time you ask. Deposits into an emotional trust bank.
5. **Write at a third-grade reading level.** Hormozi saw 50% more responses. Simple = better.
6. **Speed is king.** When someone responds, get them on a call immediately.
7. **More, Better, New.** Scale in this order: do MORE of what works → make it BETTER → only then try something NEW.

---

## Aaron's Core Four Plan

### 1. Warm Outreach (NOW — Exhausted but Rebuild-able)

**Status:** Warm network largely exhausted. Need to expand it.

**How to rebuild:**
- Join Perth business networking groups (see Networking section below)
- Every new person met = warm contact. Add to CRM.
- Don't pitch. Ask: "Do you know any tradies/small businesses who need help getting more customers online?"
- Use the **ACA Framework:**
  - **Acknowledge** — restate what they said
  - **Compliment** — tie it to a positive trait ("you clearly know everyone in the trade")
  - **Ask** — "who else do you know who might need this?"

**Target:** 10-20 warm outreaches per week (realistic with 9-5 job).

### 2. Free Content (POST-EXIT — Not Now)

**Status:** Posting ~fortnightly on YouTube. Will scale to daily after corporate exit.
**For now:** Don't force this. Focus on warm + cold outreach. Content is a long game.

**When ready (post-exit):**
- Post daily on LinkedIn + YouTube
- Content topics: before/after builds, website teardowns, quick tips, myth-busting
- Hook-Retain-Reward framework for every piece
- Give:Ask ratio of 3.5:1

### 3. Cold Outreach (NOW — Primary Lead Gen Channel)

**Status:** Manual Google Maps scraping + driving past vans. Disorganised.

**The system to build:**
- Automated daily lead pipeline (see Systems section)
- Target: 20-30 cold outreaches per day (evenings/weekends — realistic with 9-5)
- Channels: phone calls, SMS, email, Instagram DMs, Facebook messages
- Use personalised messages (not mass-blast)
- Lead with the free website offer — it's irresistible

**Cold Outreach Message Templates:**

**Phone script (30 seconds):**
> "Hey [Name], my name's Aaron from Mycelium AI. I found your business on Google Maps and noticed you don't have a website yet. I'm building free websites for local businesses this month — no strings, no catch. Would you be open to a quick 10-minute chat about it?"

**SMS/DM (short):**
> "Hey [Name], found your business on Google — looks like you're doing great work. I noticed you don't have a website. I build free ones for local businesses. Interested?"

**Email (slightly longer):**
> See `reference/emails/cold-outreach.md` for full templates.

**Key differentiator:** You're not selling. You're GIVING. "I'll build you a free website" is so different from every other agency cold-calling them that it cuts through the noise.

### 4. Paid Ads (LATER — After Proving the Offer)

**Status:** Not running ads for own lead gen yet. Running ads for clients.

**When to start:** After closing 5-10 clients via cold outreach and having case studies.

**What to run:**
- Meta Ads targeting Perth small business owners
- Lead magnet: Free Website Audit or Free Website offer
- Budget: $100/day (Hormozi's Rule of 100)
- Use the ad copy formula from `reference/uploads/alfie-ad-copy-formula.md`

---

## How to Differentiate in Perth

Perth trades businesses are bombarded by agencies. Here's how to stand out:

| What Others Do | What We Do | Why It's Different |
|----------------|-----------|-------------------|
| "We'll build you a website for $3,000" | "I'll build you a free website — no strings" | Zero risk. They've heard sales pitches. They haven't heard free. |
| Send a proposal PDF | Build the website FIRST, show it on a call | Proof of concept. They can see and touch it. |
| "We're a full-service agency" | "I'm Aaron. I build websites for tradies." | Personal. One person they can text. Not an agency. |
| Generic pitch to everyone | "I noticed your plumbing business in [suburb] has great Google reviews but no website" | Personalised. Shows you actually looked at their business. |
| Sell the website | Give the website, sell the monthly services | Hormozi: money is in the backend, not the frontend. |
| Chase the sale | Ask for a referral + testimonial instead | Builds social proof and compounds over time. |
| Charge upfront | Proof of concept: "If you don't like it, full refund" | Risk reversal. They have nothing to lose. |

**The ultimate differentiator:** You're the only one offering something for FREE that everyone else charges $2,000+ for. That alone is enough.

---

## Lead Magnets (Future — When Running Paid Ads)

| Lead Magnet | Type | Format | Reveals |
|-------------|------|--------|---------|
| Free Website (current offer) | Service | Done-for-you | "You need more than a basic site — you need automation" |
| Free Google Business Profile Audit | Problem revealer | Loom video (5 min) | "You're invisible in Google — here's why" |
| "5 Things Every Tradie's Website Needs" | Information | PDF guide | "Your site is missing these — I can add them" |
| Free Website Scorecard | Software | Automated tool | "Your site scores 3/10 — here's how to fix it" |
| Free Loom Teardown of Their Online Presence | Service | Video | "Here are 3 things losing you customers right now" |

---

## Automated Lead Pipeline (Build This)

### Architecture: n8n + Apify + Supabase + Gmail

```
Daily 6am Cron
    ↓
Apify: Scrape Google Maps → Perth businesses without websites
    ↓
Filter: Remove businesses WITH websites (or with only Facebook as "website")
    ↓
Supabase: Check against existing leads (deduplicate by place_id or phone)
    ↓
Insert NEW leads only
    ↓
Gmail: Daily digest → "X new leads found today" with names, phones, categories
```

### Data Sources to Monitor

| Source | Tool | Frequency | Cost | Unique Value |
|--------|------|-----------|------|-------------|
| **Google Maps** (no website filter) | Apify "Businesses Without Websites" actor or Outscraper | Daily | ~$5-20/mo | Highest volume. Primary source. |
| **ABR (new ABN registrations in WA)** | ABR public API (free) | Daily | **Free** | New businesses = perfect timing. Nobody else is doing this. |
| **HiPages** | Apify HiPages scraper | Weekly | ~$5/mo | Trades-specific. Filter for high jobs + no website. |
| **Yellow Pages AU** | Apify Yellow Pages AU actor | Weekly | ~$5/mo | Supplementary. Cross-reference with Google Maps. |
| **Facebook Pages** (no website) | Apify Facebook Pages scraper | Weekly | ~$5/mo | Risk: ToS grey area. Use carefully. |

### The ABR API (Secret Weapon)

The Australian Business Register has a **free public API** that lets you search by registration date and state. Nobody is monitoring this for lead gen.

**The play:**
1. Daily: Query ABR API for new WA business registrations (yesterday's date)
2. Filter by Perth postcodes (6000-6999)
3. Cross-reference against Google Maps — do they have a website?
4. If no website → add to daily lead digest
5. You're reaching out to a brand-new business within days of them registering

**Why this is gold:** New businesses are in setup mode. They're actively making decisions about websites, branding, online presence. You're arriving at exactly the right moment — not 2 years after they've already been pitched by 50 agencies.

### Tools & Costs

| Tool | Purpose | Cost |
|------|---------|------|
| Apify (already in .env) | Google Maps, HiPages, Yellow Pages scraping | $5-20/mo (set maxItems limits) |
| Outscraper | Alternative Google Maps scraper with "no website" filter | Free first 500, then $3/1K |
| Webleadr | Pre-built "businesses without websites" leads | $12/100 leads |
| ABR API | New business registrations | **Free** |
| n8n (already set up) | Workflow orchestration | Already paying |
| Supabase (already set up) | Lead storage + deduplication | Free tier |

**Total estimated cost: $15-30/mo for an automated daily lead pipeline.**

---

## Lead Purchasing Options (Australia)

| Platform | Model | Cost | Notes |
|----------|-------|------|-------|
| Webleadr | Pre-scraped "no website" leads | $0.12/lead | Quick wins while building automation |
| Bark | Inbound job requests, pay per lead | $2-25/lead | Businesses post requests, you respond |
| Oneflare | Dynamic pricing per lead | $6-25/lead | Trades-focused |
| ServiceSeeking | Monthly membership, unlimited quoting | From $66/mo | Good for supplementary leads |

---

## Physical / Offline Lead Gen (Perth)

### Corflute Signs

**Message A (Free Website):**
> DOES YOUR BUSINESS NEED A WEBSITE?
> I'll build one for FREE.
> No catch. You keep the code.
> Text Aaron: [phone] or scan QR →

**Message B (AI/Automation):**
> WHAT IF YOUR BUSINESS RAN ITSELF OVERNIGHT?
> Free AI automation demo for Perth businesses.
> Text Aaron: [phone] or scan QR →

**Where to place:**
- Light industrial areas: Malaga, Osborne Park, Balcatta, Welshpool
- Near building sites (tradies everywhere)
- Shopping centre car parks (foot traffic)
- Near Bunnings stores (tradies + small business owners)

**Cost:** $5-15 per sign from Perth printers (Ladybird Design, JL Signs, Docuprint WA).

### Perth Business Networking Groups

| Group | Meeting | Notes |
|-------|---------|-------|
| **BNI Western Australia** | Weekly, various locations | One member per profession. Strong referral culture. |
| **District 32 Business Co-op** | Various | Good for Perth SMB networking |
| **Nifnex** | Various | Casual networking |
| **Chamber of Commerce & Industry WA** | Events-based | Broader business community |
| **Fremantle Chamber of Commerce** | Events-based | Freo-specific |
| **Malaga & Districts Business Association** | Events-based | Industrial area — lots of trades |

**Priority:** Join BNI or District 32 first. One referral partner (accountant, business coach) can generate a steady flow of warm leads.

### Complementary Partners (Referral Sources)

| Partner Type | Why They're Gold | How to Approach |
|-------------|-----------------|-----------------|
| Accountants / Bookkeepers | See new ABN registrations firsthand. Advise new businesses on setup. | "I build free websites for your new business clients — makes you look good, costs you nothing." |
| Business Coaches | Clients are growing businesses needing professional web presence. | Same approach — offer value to their clients for free. |
| Graphic Designers / Print Shops | Already doing branding — natural upsell to website. | Reciprocal referral arrangement. |
| Commercial Real Estate Agents | Know when new businesses are opening premises. | "When your tenant opens, I'll build them a free website. Makes your space look more attractive." |
| Insurance Brokers | New business insurance = new business needing a website. | Same as accountants. |

**Hormozi's affiliate principle:** "If you can show them that their audience wins by them associating with you, you'll unlock the doors to as much promotion as you want."

---

## The Referral Loop (Compound Growth)

After every successful project:
1. Ask for a Google review (see `reference/emails/referrals-testimonials.md`)
2. Ask for a video testimonial
3. Ask: "Do you know any other tradies who'd want more jobs coming in?"
4. Compliment them as a "connector" (raises their status, makes them want to help)
5. Offer incentive: free month of hosting for every referral that converts

**Why this compounds:** Each client brings 1-2 referrals → those clients bring 1-2 more → exponential growth. Referral clients also close faster and stay longer because they arrive with trust pre-built.

---

## Weekly Lead Gen Cadence (While Working 9-5)

| Day | Morning (Before Work) | Evening (After Work) | Time |
|-----|----------------------|---------------------|------|
| Mon | Check daily lead digest email | 10 cold calls/texts from lead list | 30 min |
| Tue | Reply to any responses | 10 cold DMs (Instagram/Facebook) | 30 min |
| Wed | Check daily lead digest | 10 cold calls/texts | 30 min |
| Thu | Reply to responses | Discovery calls (if any booked) | 30-60 min |
| Fri | Check lead digest | Build free websites for warm leads | 1-2 hrs |
| Sat | Networking event (BNI/D32) OR build free sites | Cold outreach batch (20 calls/texts) | 2-3 hrs |
| Sun | Plan week, review CRM, update lead list | Build websites / client work | 2-4 hrs |

**Weekly total: ~10-15 hours. 60-80 outreaches per week.**

This isn't 100/day (Hormozi's ideal), but it's realistic with a 9-5. The automated pipeline supplements this by delivering fresh leads to your inbox every morning.

---

## Priority Actions (Do This Week)

1. **Set up Apify Google Maps scraper** — Perth businesses without websites. Categories: plumber, electrician, builder, cleaner, landscaper, pest control. Already have Apify in .env. Schedule daily.
2. **Register for ABR API** — free, takes 5 minutes. Start monitoring new WA businesses daily.
3. **Build n8n pipeline** — connect Apify + ABR → Supabase (dedup) → daily Gmail digest.
4. **Order 10 corflute signs** — "Free website" message. Place in Malaga, Osborne Park, near Bunnings.
5. **Join one networking group** — BNI or District 32. One meeting = 10+ warm contacts.
6. **Set up Webleadr** — $12 for 100 instant leads while automation is being built.

---

## Metrics to Track

| Metric | Target | Track In |
|--------|--------|----------|
| Outreaches per week | 60-80 | CRM |
| Response rate | >10% | CRM |
| Discovery calls per week | 2-3 | CRM |
| Free websites delivered per month | 4-6 | CRM |
| Tier 1 conversions per month | 2-3 (50% of free) | CRM |
| Referrals per client | 1-2 | CRM |
| Daily automated leads (pipeline) | 5-20 | Daily digest email |

---

_This is a living document. Update as lead gen systems are built and refined._
