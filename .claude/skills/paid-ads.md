---
name: paid-ads
description: Discovery, classification, and budget split for paid ad campaigns (Google + Meta). Entry point — runs before google-ads or meta-ads skills.
---

# Skill: Paid Ads Setup & Optimisation

**Purpose:** Repeatable, client-agnostic workflow for setting up and optimising Google Ads and Meta (Facebook/Instagram) ad campaigns for businesses of any type and size.

**When to use:** New client onboarding for paid ads, launching a new campaign, or optimising an existing one. This is the **entry point** — run this first, then hand off to `google-ads` and/or `meta-ads` skills for platform-specific setup.

---

## How It Works

This skill runs through a structured discovery → setup → launch → optimise flow. It asks key questions, then generates platform-specific campaigns tailored to the client's business.

---

## Phase 1: Client Discovery (5 questions)

Before touching any ad platform, gather these answers:

### Q1. Business Basics
- What does the business do? (1 sentence)
- Business name, website URL, phone number
- Physical address (for local targeting)
- **Business type classification** — Based on the answer, Claude classifies into one of 8 archetypes that drive all downstream ad settings:

| Archetype | Signals | Examples |
|-----------|---------|---------|
| `local-service` | Serves a local area, customers search when they need it, phone calls matter | Plumber, cleaner, pest control, bore driller |
| `local-service-lsa` | Same + eligible for Google Local Services Ads (Google Guaranteed) | Plumber, electrician, locksmith, HVAC |
| `professional-b2b` | Clients are businesses or high-consideration consumers, longer sales cycle | Accountant, lawyer, IT consultant, architect |
| `local-retail` | Physical location, foot traffic, directions/visits are the goal | Cafe, restaurant, salon, boutique |
| `ecommerce` | Sells products online | Online shop, product brand |
| `hospitality-tourism` | Visitors from other locations, booking-based, visuals matter | Hotel, tour operator, holiday rental |
| `health-medical` | Booking-based, restricted ad policies | Dentist, physio, GP, vet |
| `trades-home` | Like local-service but higher ticket, longer decision, portfolio matters | Builder, roofer, painter, pool builder |

> **This classification feeds directly into the google-ads and meta-ads skills.** Every setting (campaign type, keywords, bidding, ad copy, conversion tracking) adapts based on archetype.

### Q2. Service Area & Audience
- Where do they operate? (city, radius, regions)
- Who is the ideal customer? (homeowners, farmers, builders, commercial?)
- Any demographics to exclude?

### Q3. Budget & Goals
- Total weekly/monthly ad budget?
- Split preference: Google vs Meta? (default: 70% Meta / 30% Google for awareness-stage businesses; flip for high-intent services)
- Primary goal: phone calls, form submissions, website visits, or messages?
- What's one job/sale worth? (for ROAS calculation)

### Q4. Competitive Landscape
- Who are the top 2-3 competitors?
- Are competitors running ads? (check Meta Ad Library + Google Ads transparency)
- What makes this business different? (USP / differentiators)

### Q5. Assets & Access
- Do they have photos/videos of their work?
- Do they have a Google Business Profile?
- Do they have a Facebook Business Page + Instagram account?
- Who has admin access? (client, partner, agency?)
- Is there a Meta Pixel or Google conversion tag already installed?

---

## Phase 2: Platform Setup

After discovery, hand off to the platform-specific skills:

- **Google Ads:** Run `.claude/skills/google-ads.md` — full campaign build, keywords, RSA copy, extensions, conversion tracking
- **Meta Ads:** Run `.claude/skills/meta-ads.md` — full campaign build, targeting, creative, lead forms, CRM automation

Both skills read the archetype and discovery answers from Phase 1 above. You don't need to re-ask any questions.

---

## Phase 3: Optimisation (Weekly)

### Week 1-2: Learn

- Don't change anything for the first 3-5 days (let algorithms learn)
- Monitor: impressions, clicks, CTR, cost per click, cost per lead
- Check search terms report (Google) — add negatives for irrelevant searches
- Check Meta ad frequency — if above 3, audience is too small

### Week 3-4: Optimise

- **Google:** Pause keywords with high spend + zero conversions. Add new negatives. Test new ad copy.
- **Meta:** Pause ads with CTR < 1%. Scale ad sets with cost per lead below target. Test new creative.
- Adjust budgets based on which platform is delivering cheaper leads.

### Monthly: Review & Report

- Total spend vs total leads vs cost per lead
- Which platform/campaign/ad is winning?
- Recommendations for next month
- Report to client (simple: spend, leads, cost per lead, next steps)

### Key metrics & benchmarks

**Local service / trades:**
| Metric | Google Ads | Meta Ads |
|--------|-----------|----------|
| CTR | 3-5% (search) | 1-2% (feed) |
| CPC | $3-$12 | $0.50-$3 |
| Cost per lead | $20-$80 | $10-$50 |
| Conversion rate | 5-15% (landing page) | 2-5% (lead form) |

**Professional B2B:**
| Metric | Google Ads | Meta Ads |
|--------|-----------|----------|
| CTR | 2-4% | 0.5-1.5% |
| CPC | $5-$50 | $1-$5 |
| Cost per lead | $30-$200 | $20-$80 |
| Conversion rate | 3-8% | 1-3% |

**E-commerce:**
| Metric | Google Ads (Search) | Google Ads (Shopping) | Meta Ads |
|--------|--------------------|-----------------------|----------|
| CTR | 2-4% | 0.5-2% | 1-2% |
| CPC | $0.50-$5 | $0.30-$3 | $0.50-$3 |
| ROAS target | 400%+ | 400%+ | 300%+ |
| Conversion rate | 2-5% | 1-3% | 1-3% |

**Local retail / hospitality:**
| Metric | Google Ads | Meta Ads |
|--------|-----------|----------|
| CTR | 4-7% | 1-3% |
| CPC | $0.50-$5 | $0.30-$2 |
| Cost per visit/action | $5-$20 | $3-$15 |
| Conversion rate | 3-8% | 2-5% |

> **Full industry CPC benchmarks** are in the google-ads skill (Phase 9). Reference those for budget planning.

---

## Quick Reference: Budget Split Templates

| Scenario | Google Ads | Meta Ads | Rationale |
|----------|-----------|----------|-----------|
| **High-intent service** (plumber, electrician, drilling) | 40-50% | 50-60% | People search when they need it; Meta builds pipeline |
| **Awareness-stage** (new business, new area) | 20-30% | 70-80% | Need to create demand first |
| **Established + reviews** | 50-60% | 40-50% | Capture existing demand |
| **Tight budget (< $200/week)** | 20-30% | 70-80% | Meta's algorithm needs less spend to optimise |
| **E-commerce** | 50-70% (Shopping + Search) | 30-50% | Google Shopping captures purchase intent directly |
| **Local retail / hospitality** | 20-30% | 70-80% | Visual platforms drive foot traffic and bookings better |
| **Professional B2B** | 50-60% | 40-50% | Search captures high-intent research; Meta for brand awareness |
| **Health / medical** | 40-50% | 50-60% | Mix of search intent (emergency) and awareness (check-ups) |

---

## Files This Skill Produces

When run via `/create-plan` or `/implement`, this skill may generate:
- Campaign setup checklist (client-specific)
- Ad copy document (headlines, descriptions, ad text)
- Keyword list with match types and negatives
- Budget allocation spreadsheet
- Weekly/monthly performance report template

---

## Related Skills & Files

- `.claude/skills/google-ads.md` — Google Ads platform-specific setup (run after this skill)
- `.claude/skills/meta-ads.md` — Meta Ads platform-specific setup (run after this skill)
