---
name: google-ads
description: Full Google Ads campaign setup — account creation, verification, conversion tracking, keywords, RSA copy, extensions, budget, and post-launch management. Branched by business archetype.
---

# Skill: Google Ads Campaign Setup — Multi-Business-Type

**Purpose:** Complete, repeatable workflow for setting up Google Ads campaigns for ANY business type. Uses decision-tree logic: classify the business → every downstream setting adapts automatically.

**When to use:** New client needs Google Ads, or existing client needs a new campaign.

**Prerequisites skill:** Run `paid-ads` discovery questions first (Q1–Q5) before starting this skill. The archetype classification from `paid-ads` Phase 1 drives every setting in this skill.

**Version:** 2.0 — Upgraded from local-service-only (v1.0) to multi-business-type branching.

---

## How This Skill Works

Every phase reads the **business archetype** (set in Phase 0) and adjusts its advice. Look for conditional blocks like:

```
IF archetype = ecommerce → do X
IF archetype = local-service → do Y
```

Claude should auto-classify the business from discovery answers. Aaron should never need to pick an archetype manually.

---

## Phase 0: Business Classification

**This phase determines everything downstream.** Get it right.

### Step 1 — Classify the business archetype

Read the paid-ads discovery answers (Q1–Q5) and classify into ONE primary archetype:

| Archetype | Examples | Key Signal |
|-----------|----------|------------|
| `local-service` | Plumber, electrician, cleaner, bore driller, landscaper, pest control | Serves a local area, customers search when they need it, phone calls matter |
| `local-service-lsa` | Same as above BUT in a [Google LSA-eligible category](https://ads.google.com/local-services-ads/) | Eligible for Google Guaranteed badge + pay-per-lead |
| `professional-b2b` | Accountant, lawyer, IT consultant, marketing agency, architect | Clients are businesses or high-consideration consumers, longer sales cycle |
| `local-retail` | Cafe, restaurant, bakery, boutique, salon, barber | Physical location, foot traffic matters, directions/visits are conversions |
| `ecommerce` | Online shop, dropship store, product brand selling online | Sells products online, needs Shopping campaigns + purchase tracking |
| `hospitality-tourism` | Hotel, motel, tour operator, holiday rental, attraction | Visitors searching FROM other locations, visuals matter, booking-based |
| `health-medical` | Dentist, physio, chiropractor, GP, psychologist, vet | Booking-based, restricted ad policies, patient-focused language |
| `trades-home` | Builder, roofer, painter, concreter, fencer, pool builder | Like local-service but higher ticket, longer decision cycle, visual portfolio matters |

### Step 2 — Set archetype variables

Once classified, these variables apply to all downstream phases:

| Variable | `local-service` / `local-service-lsa` | `professional-b2b` | `local-retail` | `ecommerce` | `hospitality-tourism` | `health-medical` | `trades-home` |
|----------|---------------------------------------|--------------------:|---------------:|-------------:|----------------------:|------------------:|--------------:|
| **Primary campaign** | Search (+ LSA if eligible) | Search | Search + Local | Shopping + Search | Search + PMax | Search | Search |
| **Location targeting** | Presence only | Presence only | Tight radius, Presence only | State/National, Presence only | Presence OR interest | Presence only | Presence only |
| **Primary conversion** | Phone call + form | Form + offline import | Directions + calls | Purchase + revenue | Booking + calls | Booking + calls | Form + phone |
| **Ad schedule** | Business hours | Business hours | Opening hours | 24/7 | 24/7 | Practice hours | Business hours |
| **Keyword intent** | High-intent service | Mixed intent + brand | Location + experience | Product + brand + buy | Experience + location | Treatment + location | Service + location |
| **Avg CPC range (AUD)** | $3–$12 | $5–$50 | $1–$5 | $0.50–$5 | $1–$8 | $3–$15 | $3–$15 |
| **Avg job/sale value** | $200–$15,000 | $1,000–$50,000+ | $15–$100 | $30–$500 | $100–$2,000 | $50–$500 | $5,000–$100,000+ |
| **Decision cycle** | Same day – 2 weeks | 2 weeks – 6 months | Immediate | Minutes – days | Days – weeks | Days – 2 weeks | 2 weeks – 3 months |
| **Visual importance** | Low | Low | Medium | High | High | Medium | High |
| **Restricted category?** | No | Maybe (finance, legal) | No (usually) | No (usually) | No (usually) | YES | No |

### Step 3 — Check for Google Local Services Ads eligibility

**Only for `local-service-lsa` archetype.** If the business is in an eligible category:

Google Local Services Ads (LSAs) are **pay-per-lead** (not per-click) and show a "Google Guaranteed" badge. They appear ABOVE regular Search Ads. For eligible trades, LSAs should be the PRIMARY campaign, with Search Ads as secondary.

**Eligible categories in Australia (as of 2026):** Plumber, electrician, locksmith, HVAC, pest control, cleaner, garage door, roofer, tree service, water damage restoration, and more. Check: https://ads.google.com/local-services-ads/

**LSA setup is a separate workflow** (different from Search Ads):
1. Go to ads.google.com/local-services-ads
2. Business profile setup (services, hours, area)
3. Background check + licence verification (category-dependent)
4. Set weekly budget (pay per lead, typically $15–$80/lead depending on category)
5. Leads come via phone call or message through Google's platform
6. You can dispute invalid leads within 30 days

> **If LSA-eligible:** Set up LSA first, then add a Search campaign as a secondary capture net. LSA gets priority in budget allocation.

> **If not LSA-eligible:** Skip this, proceed to Phase 1.

---

## Phase 1: Account Creation

### Step 1 — Create Google Ads account

1. Go to **ads.google.com** → sign in with a Google account
2. Click **Start Now** or **New Google Ads Account**

### Step 2 — Switch to Expert Mode (CRITICAL)

1. Google will push you into a "Smart Campaign" — **DECLINE**
2. Look for a small link: **"Switch to Expert Mode"** or **"Create an account without a campaign"**
3. Click it

> **Why Expert Mode?** Smart Campaigns give Google full control. You can't choose keywords, can't control bids, can't see search terms. You WILL waste money. Expert Mode gives you full control — always use it.

`📸 Screenshot opportunity: Expert Mode link (easy to miss)`

### Step 3 — Account settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Billing country** | Australia | Or client's country |
| **Currency** | AUD | Match to client's currency |
| **Timezone** | (GMT+10:00) Brisbane | **CRITICAL: Set this correctly NOW — cannot be changed later.** Match to client's operating timezone, NOT your timezone. |
| **Payment method** | Client's credit card | Add during setup |

> **GOTCHA — Timezone is permanent.** Google locks the timezone at account creation. If you set it wrong (e.g., Perth instead of Brisbane), you're stuck with it forever. All reporting and scheduling will be offset. If already locked to wrong timezone, offset your ad schedule to compensate (e.g., AWST is 2hrs behind AEST: enter 04:00–18:00 to get 06:00–20:00 AEST).

`📸 Screenshot opportunity: Account settings — timezone selection`

---

## Phase 2: Advertiser Verification

Google requires identity verification for all advertisers. If you're an agency managing client ads, there are **two parts**. Start this IMMEDIATELY — it takes 3–5 business days and ads won't run until approved.

### How to access

**Tools & Settings** (wrench icon) → **Account** (previously "Advertiser verification")

### Part A — Agency Verification (your identity)

**What:** Proves YOU (the person managing the ads) are real.

1. Click **"Submit your agency's documents"**
2. Enter your full legal name (must match ID exactly)
3. Upload your photo ID:
   - **Passport:** Upload the photo page
   - **Driver's licence:** Upload front AND back
4. ID issuing country: Australia (or your country)
5. Submit → Status shows "Verification in progress"

> **Passport and driver's licence are equally valid.** Use whichever is clearest.

`📸 Screenshot opportunity: Agency verification submission page`

### Part B — Client Verification (the business being advertised)

**What:** Proves the business identity. This is what appears in the public "About this advertiser" disclosure on every ad.

1. Click **"Submit documents for your client"** → **Start**
2. On "Select a profile" screen:
   - **DO NOT select your personal profile**
   - Click **"+ Create new payments profile"**
3. Fill in client's business details:

| Field | Value |
|-------|-------|
| **Profile type** | Business (not Individual) |
| **Business name** | Client's registered business name (from ABN lookup) |
| **ABN** | Client's ABN |
| **Address** | Client's registered business address |
| **Country** | Australia |

4. Click **Continue** → "Verify your organization" page appears
5. Three sub-steps:
   - **Step 1 — Organization name:** Confirm business name. Upload ABN registration PDF (free from abr.business.gov.au)
   - **Step 2 — Organization address:** Confirm business address
   - **Step 3 — Your name and ID:** Enter YOUR name and upload YOUR ID (you are the submitter, signing on behalf of the client)
6. Submit → Confirmation: "Thanks for starting verification!" → 3–5 business days

> **GOTCHA — Don't select your personal profile for client verification.** If you do, the "About this advertiser" disclosure on every ad will show YOUR name instead of the client's business name. Always create a new business profile for the client.

> **Why your ID in Step 3?** Think of it like signing a legal form on behalf of a company. Steps 1–2 identify the company. Step 3 identifies the person signing. That's you.

### What you can do while waiting

| Status | What you can do |
|--------|----------------|
| Verification in progress | Build everything: campaigns, keywords, ads, extensions, conversion tracking |
| Verified | Publish and run ads |
| Rejected | Check email for reason, fix, resubmit |

`📸 Screenshot opportunity: Verification confirmation page showing business name`

---

## Phase 3: Conversion Tracking

**Set this up BEFORE creating the campaign.** You need to measure results from Day 1.

### Step 1 — Access conversion setup

**Tools & Settings** → **Conversions** (under Measurement) → **+ New conversion action** → **Website**

### Step 2 — Scan the website

1. Enter client's website URL → Click **Scan**
2. On data sources screen, check:
   - **Google tag** (the tracking code)
   - **Google Analytics property** (if one is linked)
3. Click **Done**

> **GOTCHA — Lovable/SPA sites:** Google's scanner may fail to find anything on client-side rendered sites. The red "No keywords found" warning is cosmetic — ignore it. Proceed with manual setup.

### Step 3 — Choose conversion types (BRANCHED BY ARCHETYPE)

**`local-service` / `local-service-lsa` / `trades-home`:**
- Website form submissions (quote request, contact form)
- Phone calls from ads (click-to-call)
- Phone calls from website (call tracking)

**`professional-b2b`:**
- Website form submissions (consultation request, contact form)
- Phone calls from ads
- **Offline conversion import** (upload which leads became paying clients — tells Google's algorithm what a GOOD lead looks like). Set up later once CRM data flows.

**`local-retail`:**
- **Get directions** clicks (Google Maps)
- Phone calls
- Menu/catalogue views (if applicable)
- Store visit conversions (if enough foot traffic data — requires linked Google Business Profile)

**`ecommerce`:**
- **Purchase** (with dynamic revenue value — each sale tracked with its actual dollar amount)
- Add to cart
- Begin checkout
- Requires: Google Merchant Center + enhanced e-commerce tracking (gtag or Google Tag Manager)

**`hospitality-tourism`:**
- **Booking completed** (integration with booking system — e.g., confirmation page)
- Phone calls
- Check availability clicks
- Direction requests

**`health-medical`:**
- **Appointment booked** (integration with practice management software or booking page)
- Phone calls
- "Book Now" button clicks (micro-conversion if no online booking)

### Step 4 — Create the primary conversion action

#### For form/page-load conversions (local-service, professional-b2b, trades-home):

1. Choose category: **"Submit lead form"**
2. Select data source: **Google tag** (not Analytics)
3. Configure:

| Setting | Value | Why |
|---------|-------|-----|
| **Event type** | Page load | Thank-you page loading = proof the form was submitted. More reliable than form detection on SPAs. |
| **Match when** | URL contains | Flexible matching |
| **URL** | `/thank-you` (or client's confirmation page path) | The page users land on after form submission |
| **Conversion name** | `Quote Form Submission` (or descriptive name) | Clean name for reports |
| **Value** | Estimated lead value in AUD | Calculate: (average job value x close rate). E.g., $10k job x 5% close = $500/lead. |
| **Count** | One | One lead per person. Prevents double-counting on page refresh. |
| **Click-through window** | 90 days | Service businesses have long consideration periods |
| **Attribution** | Data-driven (Recommended) | Let Google figure out which touchpoints matter |

> **Why "Page load" not "Form submission"?** The "Form submission" option tries to auto-detect form submit events — unreliable on SPAs (Lovable, React, etc.) where the page doesn't actually reload. Page load on the thank-you URL is simpler and bulletproof.

#### For e-commerce purchase conversions:

1. Choose category: **"Purchase"**
2. Select data source: **Google tag**
3. Configure:

| Setting | Value |
|---------|-------|
| **Event type** | Page load (order confirmation page) OR custom event (`purchase`) |
| **Value** | **Use different values for each conversion** — dynamic revenue from the data layer |
| **Count** | Every | Each purchase counts (unlike leads where you count one per person) |
| **Click-through window** | 30 days | E-commerce decisions are faster |

4. Requires additional setup: pass transaction value via the data layer:
```javascript
gtag('event', 'purchase', {
  transaction_id: 'ORDER_123',
  value: 79.99,
  currency: 'AUD',
  items: [{ item_name: 'Product Name', price: 79.99 }]
});
```

#### For booking conversions (health-medical, hospitality-tourism):

1. Choose category: **"Book appointment"** or **"Purchase"** (depending on what the booking represents)
2. Track the booking confirmation page URL (e.g., `/booking-confirmed`, `/appointment-confirmed`)
3. If the client uses an external booking system (Calendly, Fresha, Cliniko, etc.):
   - Option A: Track the "Book Now" button click as a micro-conversion + the confirmation redirect as the primary conversion
   - Option B: Use Google Tag Manager to fire on the booking widget's completion event
   - Option C: If no redirect back to client site, track the "Book Now" click as the primary conversion (less accurate but functional)

#### For directions/map conversions (local-retail):

1. This is tracked automatically if Google Business Profile is linked to Google Ads
2. Additionally track phone calls and any website actions (menu views, etc.)

### Step 5 — Install the Google tag

Google will provide a code snippet like:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXXX');
</script>
```

**Install this in the `<head>` of every page** (for Lovable sites: add to `index.html` `<head>` via a Lovable prompt).

Click **Test Installation** → should show green tick.

### Step 6 — Install event snippets

Add conversion event code to the relevant pages:

**For thank-you/confirmation pages:**
```html
<script>
  gtag('event', 'ads_conversion_[event_name]', {});
</script>
```

For Lovable/React sites, fire this in a `useEffect` on the ThankYou/Confirmation component:
```javascript
useEffect(() => { window.gtag('event', 'ads_conversion_[event_name]', {}); }, []);
```

**For e-commerce (on order confirmation page):**
```javascript
gtag('event', 'ads_conversion_Purchase', {
  value: orderTotal,
  currency: 'AUD',
  transaction_id: orderId
});
```

### Step 7 — Enable enhanced conversions

On the summary page, check **"Turn on enhanced conversions"** → **Agree and finish**

Enhanced conversions use hashed customer data (email, phone from forms) to improve conversion matching accuracy. Free uplift, no downside.

### Step 8 — Set up offline conversion import (professional-b2b only)

For B2B / high-ticket clients where the real conversion (signing a client, closing a deal) happens offline weeks later:

1. **Tools & Settings** → **Conversions** → **+ New conversion action** → **Import**
2. Select **"Other data sources or CRMs"** → **"Track conversions from clicks"**
3. Name it: "Closed Deal" or "Signed Client"
4. Set the value to actual deal value
5. Upload conversion data periodically (CSV or API): Google Click ID (GCLID) + conversion date + value
6. This teaches Google's algorithm which TYPES of clicks lead to real revenue — dramatically improves lead quality over time

> **This is the single biggest lever for B2B Google Ads.** Without it, Google optimises for form fills (which may be tyre-kickers). With it, Google optimises for form fills that BECOME clients.

`📸 Screenshot opportunity: Google tag successfully detected confirmation`

---

## Phase 4: Campaign Creation

### Step 1 — New campaign

**Campaigns** (left sidebar) → **blue + button** → **New campaign**

### Step 2 — Objective

| Archetype | Objective | Why |
|-----------|-----------|-----|
| `local-service` / `local-service-lsa` / `trades-home` | **Leads** | Optimises for calls + form fills |
| `professional-b2b` | **Leads** | Form fills → pipeline |
| `local-retail` | **Local store visits and promotions** (if eligible) or **Leads** | Foot traffic is the goal |
| `ecommerce` | **Sales** | Optimises for purchases + revenue |
| `hospitality-tourism` | **Leads** or **Sales** (if direct booking with payment) | Depends on whether booking = payment |
| `health-medical` | **Leads** | Appointment bookings |

### Step 3 — Campaign type (BRANCHED)

| Archetype | Primary Campaign Type | Secondary (add later if budget allows) |
|-----------|----------------------|---------------------------------------|
| `local-service` | **Search** | — |
| `local-service-lsa` | **Local Services Ads** (separate setup) + **Search** | — |
| `professional-b2b` | **Search** | Display remarketing (retarget website visitors) |
| `local-retail` | **Search** | Performance Max (for Google Maps + local inventory) |
| `ecommerce` | **Shopping** (requires Merchant Center) + **Search** (brand + category) | Performance Max (once you have conversion data) |
| `hospitality-tourism` | **Search** | Performance Max (visuals + Maps + Discovery) |
| `health-medical` | **Search** | — |
| `trades-home` | **Search** | — |

> **GOTCHA — Performance Max trap.** Google often defaults to Performance Max after selecting an objective. PMax spreads budget across Search, Display, YouTube, Gmail, Maps. On small budgets ($4–$10/day), this is wasteful for most archetypes. **Always explicitly select "Search"** unless the archetype table above says otherwise.

> **When IS Performance Max OK?** When visuals matter (hospitality, retail, ecommerce), when you have 30+ conversions for the algorithm to learn from, AND when budget is $20+/day. Not on Day 1 for most clients.

### Step 4 — Conversion goals

Your previously created conversion goals should appear automatically. Verify they're listed. If not, click "Add goal" to include them.

### Step 5 — Ways to reach your goal

**`local-service` / `trades-home` / `health-medical`:**
- Check: Website visits, Phone calls, Lead form submissions
- Uncheck: Store visits

**`local-retail`:**
- Check: Website visits, Phone calls, Store visits (if eligible)
- Uncheck: Lead form submissions (unless they have one)

**`ecommerce`:**
- Check: Website visits (purchases happen on site)
- Uncheck: Phone calls, Store visits (unless also has physical store)

**`professional-b2b`:**
- Check: Website visits, Phone calls, Lead form submissions
- Uncheck: Store visits

**`hospitality-tourism`:**
- Check: Website visits, Phone calls
- Uncheck: Store visits (unless walk-in venue)

### Step 6 — Campaign name

Use a consistent naming convention:
```
[Client Initials] - [Campaign Type] - [Service/Product] - [Location]
```
Examples:
- `GDC - Search - Bore Drilling - Darling Downs`
- `BCS - Shopping - Candles - Australia`
- `TDH - Search - Dentist - Toowoomba`

Click **Continue**

`📸 Screenshot opportunity: Campaign type selection`

---

## Phase 5: Campaign Settings

### Bidding (BRANCHED)

| Archetype | Starting Bid Strategy | Why | Switch to... |
|-----------|----------------------|-----|-------------|
| `local-service` (low budget <$10/day) | **Manual CPC** ($5–$8 max) | Full control on tiny budgets. Smart bidding needs volume. | Maximize Conversions after 15+ conversions |
| `local-service` ($10+/day) | **Maximize Conversions** (no target) | Enough budget for Google to learn | Target CPA after 30+ conversions |
| `professional-b2b` | **Maximize Conversions** (no target) | Leads have high value, let Google explore | Target CPA after 15+ conversions. Import offline conversions to improve quality. |
| `local-retail` | **Maximize Clicks** with max CPC cap ($3–$5) | Foot traffic = volume game, low CPC | Maximize Conversions after conversion data builds |
| `ecommerce` | **Maximize Conversions** (no target) for Search. **Maximize conversion value** for Shopping. | Shopping should optimise for revenue, not just conversion count | Target ROAS after 30+ conversions |
| `hospitality-tourism` | **Maximize Conversions** (no target) | Bookings have clear value | Target CPA or Target ROAS after data builds |
| `health-medical` | **Maximize Conversions** (no target) | Appointment bookings are clear conversions | Target CPA after 15+ conversions |
| `trades-home` (low budget) | **Manual CPC** ($8–$15 max) | High-ticket, low-volume — every click expensive | Maximize Conversions after 10+ conversions |
| `trades-home` ($15+/day) | **Maximize Conversions** | Enough budget for smart bidding | Target CPA after 15+ conversions |

> **Smart bidding volume rule of thumb:** Google recommends 15–30 conversions/month minimum for smart bidding to optimise. Below that, Manual CPC gives you more control. Check: (daily budget / average CPC) x conversion rate x 30 = estimated monthly conversions.

### Networks

**ALL archetypes — Uncheck BOTH:**
- **Google Search Partners** — low-quality third-party sites. Waste of budget.
- **Google Display Network** — banner ads across random websites. Wrong format for search intent.

> **Exception:** `ecommerce` with $30+/day budget MAY benefit from Search Partners for Shopping campaigns. Test with a separate campaign, not your main one.

### Locations (BRANCHED)

**`local-service` / `local-service-lsa` / `trades-home` / `health-medical`:**
1. Add each town/city in the client's service area individually
2. For larger service areas, use radius targeting from the client's base
3. **Location options → "Presence: People in or regularly in your targeted locations"**

**`local-retail`:**
1. Tight radius (5–15km) around the physical location
2. **Location options → "Presence: People in or regularly in your targeted locations"**

**`professional-b2b`:**
1. City/metro area if local. State or national if remote services.
2. **Location options → "Presence: People in or regularly in your targeted locations"**

**`ecommerce`:**
1. State-wide or national (wherever you ship to)
2. **Location options → "Presence: People in or regularly in your targeted locations"**
3. Exclude locations you don't ship to

**`hospitality-tourism`:**
1. **This is the ONE archetype where "Presence or interest" is correct.**
2. Tourists search for "hotel toowoomba" from Sydney. You WANT to reach them.
3. Target the local area with **"Presence or interest: People in, regularly in, or who've shown interest in your targeted locations"**
4. Also consider targeting major cities as source markets (e.g., target Brisbane and Sydney with ads for a Toowoomba hotel)

> **CRITICAL for all other archetypes: Always change to "Presence" only.** The default "Presence or interest" will show your plumber ads to someone in Melbourne who once googled Toowoomba. Massive budget waste.

### Languages

**English** (or appropriate language for the market)

### Ad Schedule (BRANCHED)

| Archetype | Schedule | Why |
|-----------|----------|-----|
| `local-service` / `trades-home` | Mon–Sat, 06:00–20:00 | Business hours when they can answer the phone |
| `professional-b2b` | Mon–Fri, 08:00–18:00 | Office hours — B2B buyers don't search on weekends |
| `local-retail` | Match opening hours | No point running ads when you're closed |
| `ecommerce` | 24/7 (all hours, all days) | People shop anytime. No phone to answer. |
| `hospitality-tourism` | 24/7 (all hours, all days) | Tourists plan trips at all hours |
| `health-medical` | Mon–Fri 07:00–19:00, Sat 08:00–13:00 | Practice hours + Saturday morning common |

> **GOTCHA — Check the account timezone.** If the account timezone is wrong, offset the schedule. AWST is 2hrs behind AEST: enter 04:00–18:00 to get 06:00–20:00 in client's actual timezone.

### Broad Match & AI Max

**Leave AI Max OFF for ALL archetypes on launch.** AI Max enables broad match for all keywords and auto-rewrites ad copy. On small budgets, you need precision — not Google experimenting with your money.

**When to reconsider:** After 30+ conversions AND $20+/day budget. Even then, test in a separate campaign first.

### Audience segments

Skip for Search campaigns — keywords handle targeting. Exception: `professional-b2b` may add "In-market audiences" for their industry as an OBSERVATION (not targeting) to gather data.

`📸 Screenshot opportunity: Location targeting with correct setting selected`

---

## Phase 6: Keywords (BRANCHED BY ARCHETYPE)

### Match type strategy (same for all)

Use **phrase match** for all keywords on launch. This balances reach with relevance.

| Match type | Symbol | Risk on small budget |
|-----------|--------|---------------------|
| Broad match | none | **HIGH** — matches anything vaguely related. Avoid on launch. |
| Phrase match | "keyword" | **LOW** — matches searches containing your phrase. Use this. |
| Exact match | [keyword] | **VERY LOW** — too restrictive for small budgets. Use sparingly. |

### Keyword count by budget (same for all)

| Budget | Recommended keywords |
|--------|---------------------|
| $4–$5/day | 10–15 keywords (high-intent only) |
| $10–$20/day | 15–25 keywords (add research-phase) |
| $30+/day | 25–40 keywords (add broader terms, more ad groups) |

---

### `local-service` / `local-service-lsa` keyword templates

**High-intent (people ready to buy):**
```
"[service] [city/town]"              → "bore drilling toowoomba"
"[service] near me"                  → "bore drilling near me"
"[service] [state/region]"           → "bore drilling qld"
"[service] [town]" x each town      → "bore drilling dalby"
"[service type] [service]"           → "stock and domestic bore drilling"
"[specific service]"                 → "irrigation bore drilling"
"[service] quote"                    → "bore drilling quote"
"[service] company"                  → "bore drilling company"
```

**Research-phase (add Week 2+ if budget allows):**
```
"[service] cost"                     → "bore drilling cost"
"how much does [service] cost"       → "how much does a bore cost"
```

---

### `professional-b2b` keyword templates

**High-intent:**
```
"[service] [city]"                   → "accountant brisbane"
"[service] for [client type]"        → "accountant for small business"
"[industry] [service]"               → "construction accountant"
"[service] near me"                  → "accountant near me"
"[service] firm [city]"              → "accounting firm brisbane"
```

**Consideration-phase:**
```
"best [service] [city]"              → "best accountant brisbane"
"[service] reviews [city]"           → "accountant reviews brisbane"
"[outcome] [service]"                → "tax minimisation accountant"
```

**Brand (if established):**
```
"[business name]"                    → "smith & co accounting"
```

---

### `local-retail` keyword templates

**High-intent (ready to visit):**
```
"[business type] near me"            → "cafe near me"
"[business type] [suburb/area]"      → "cafe toowoomba"
"best [business type] [city]"        → "best cafe toowoomba"
"[business type] open now"           → "cafe open now"
"[specialty] [business type]"        → "specialty coffee toowoomba"
```

**Experience-based:**
```
"[food/product type] [city]"         → "sourdough bread toowoomba"
"[occasion] [business type] [city]"  → "brunch cafe toowoomba"
```

---

### `ecommerce` keyword templates

**Product-intent (ready to buy):**
```
"buy [product] online"               → "buy soy candles online"
"[product] australia"                → "soy candles australia"
"[brand] [product]"                  → "lumino soy candles"
"[product] [material/type]"          → "hand-poured soy candles"
"[product] gift"                     → "candle gift set"
```

**Comparison/research:**
```
"best [product]"                     → "best soy candles"
"[product] vs [product]"             → "soy candles vs beeswax candles"
"[product] review"                   → "soy candle review"
```

**Category:**
```
"[category] shop"                    → "candle shop online"
"[category] store australia"         → "candle store australia"
```

---

### `hospitality-tourism` keyword templates

**Booking-intent:**
```
"[accommodation type] [city]"        → "hotel toowoomba"
"[activity] [region]"                → "wine tour darling downs"
"things to do [city]"                → "things to do toowoomba"
"[accommodation type] near [landmark]" → "motel near toowoomba showgrounds"
```

**Planning-phase:**
```
"[city] accommodation"               → "toowoomba accommodation"
"where to stay [city]"               → "where to stay toowoomba"
"[event] [city] [year]"              → "carnival of flowers toowoomba 2026"
```

---

### `health-medical` keyword templates

**Booking-intent:**
```
"[practitioner] [city]"              → "dentist toowoomba"
"[practitioner] near me"             → "dentist near me"
"[treatment] [city]"                 → "teeth whitening toowoomba"
"[condition] [practitioner]"         → "back pain physio"
"emergency [practitioner] [city]"    → "emergency dentist toowoomba"
```

**Consideration:**
```
"best [practitioner] [city]"         → "best dentist toowoomba"
"[practitioner] bulk billing"        → "dentist bulk billing toowoomba"
"[treatment] cost"                   → "teeth whitening cost"
```

---

### `trades-home` keyword templates

**High-intent:**
```
"[trade] [city]"                     → "builder toowoomba"
"[specific service] [city]"          → "deck builder toowoomba"
"[trade] near me"                    → "builder near me"
"[trade] quote [city]"               → "builder quote toowoomba"
"[project type] [trade]"             → "house extension builder"
```

**Research-phase:**
```
"[project type] cost [city]"         → "house extension cost toowoomba"
"how much does [project] cost"       → "how much does a deck cost"
"[trade] reviews [city]"             → "builder reviews toowoomba"
```

---

### Negative keywords (ALL archetypes — add IMMEDIATELY)

**Universal negative list (apply to every campaign):**
```
Employment:     jobs, career, salary, apprentice, apprenticeship, hire, hiring, recruitment, vacancy, resume
DIY/Education:  DIY, how to, training, course, youtube, video, tutorial, images, pdf, wikipedia, reddit
Budget wasters: free, cheap, second hand, rental, rent, used
Research only:  what is, definition, meaning, history
```

**Archetype-specific negatives:**

| Archetype | Additional Negatives |
|-----------|---------------------|
| `local-service` | [wrong service types], [wrong regions], [wrong terminology — e.g., "borewell" for Australian bore drilling] |
| `professional-b2b` | jobs, salary, intern, template, example, sample, free download |
| `local-retail` | recipe, homemade, make your own, delivery (if no delivery) |
| `ecommerce` | free, DIY, make, wholesale (unless you sell wholesale), [competitor brand names if unwanted] |
| `hospitality-tourism` | jobs, live, real estate, rent, buy property, move to [city] |
| `health-medical` | study, degree, nursing, symptoms (unless content strategy), home remedy |
| `trades-home` | DIY, how to build, plans, permits (unless you help with permits), [subcontractor-type searches] |

> **Week 1 action (ALL archetypes):** Check the Search Terms report (Campaigns → Keywords → Search Terms) on Day 3. Add any irrelevant actual searches as negatives. This is the single highest-ROI activity in Google Ads management.

### Keyword entry in Google Ads

1. In the "Enter keywords" text box, paste keywords one per line WITH quotes for phrase match
2. Ignore any red "No keywords found for URL" warnings (auto-suggestion tool failing, common with SPA sites)
3. Remove any auto-generated terms using wrong terminology

`📸 Screenshot opportunity: Keywords entered in the campaign builder`

---

## Phase 7: Ad Copy — RSA (BRANCHED BY ARCHETYPE)

Google Search Ads use **Responsive Search Ads (RSAs)**. You provide up to 15 headlines (30 chars each) and 4 descriptions (90 chars each). Google mixes and matches.

### Headline formula — 15 headlines per archetype

#### `local-service` / `local-service-lsa` / `trades-home`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Service + expertise | [Service] Experts | Water Bore Drilling Experts |
| 2 | Location + service | [Location] [Service] | Darling Downs Bore Drilling |
| 3 | Professional | Professional [Service] | Professional Bore Drilling |
| 4 | Specific service | [Service Type] | Stock & Domestic Bores |
| 5 | CTA | Get a Free Quote Today | Get a Free Quote Today |
| 6 | CTA variant | Call Us For a Free Quote | Call Us For a Free Quote |
| 7 | Brand | [Business Name] | Grundy Drilling Company |
| 8 | Location | [Location] & Surrounds | Toowoomba & Surrounds |
| 9 | Price signal | Competitive Rates | Competitive Rates |
| 10 | Specialisation | [Niche] Specialists | Farm Bore Specialists |
| 11 | Service variant | [Another Service] | Irrigation Bore Drilling |
| 12 | Coverage | Servicing All [Region] | Servicing All Darling Downs |
| 13 | Trust | Local Family-Owned Business | Local Family-Owned Business |
| 14 | Benefit | Reliable [Outcome] | Reliable Water Supply |
| 15 | CTA variant | Free Site Assessment | Free Site Assessment |

#### `professional-b2b`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Service + expertise | Expert [Service] | Expert Tax Accounting |
| 2 | Client type | [Service] for [Client Type] | Accounting for Small Business |
| 3 | Location | [City] [Service] | Brisbane Accounting Firm |
| 4 | Outcome | [Benefit/Result] | Minimise Your Tax Legally |
| 5 | CTA | Book a Free Consultation | Book a Free Consultation |
| 6 | Brand | [Business Name] | Smith & Co Accounting |
| 7 | Trust — experience | [X] Years Experience | 20 Years Experience |
| 8 | Trust — credentials | [Qualification/Cert] | Certified Practising Accountant |
| 9 | Industry niche | [Industry] [Service] | Construction Industry Experts |
| 10 | CTA variant | Schedule a Call Today | Schedule a Call Today |
| 11 | Differentiator | [USP] | Fixed-Fee Pricing |
| 12 | Location variant | Servicing [Region] | Servicing South East QLD |
| 13 | Availability | New Clients Welcome | New Clients Welcome |
| 14 | Outcome variant | [Specific Outcome] | Stress-Free BAS Lodgement |
| 15 | Service variant | [Secondary Service] | Business Advisory & Tax |

#### `local-retail`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Type + location | [Type] in [City] | Cafe in Toowoomba |
| 2 | Specialty | Best [Specialty] in [City] | Best Coffee in Toowoomba |
| 3 | Brand | [Business Name] | The Corner Grind |
| 4 | Experience | [Vibe/Experience] | Cosy Brunch Spot |
| 5 | CTA | Visit Us Today | Visit Us Today |
| 6 | Location specific | [Suburb/Area] | Margaret Street, Toowoomba |
| 7 | Product highlight | [Signature Item] | Freshly Roasted Coffee |
| 8 | Open hours | Open [Days/Hours] | Open 7 Days |
| 9 | Social proof | Rated #1 on Google | Rated #1 on Google |
| 10 | Occasion | Perfect for [Occasion] | Perfect for Weekend Brunch |
| 11 | CTA variant | See Our Menu | See Our Menu |
| 12 | Differentiator | [USP] | All-Day Breakfast Menu |
| 13 | Community | Locally Owned & Loved | Locally Owned & Loved |
| 14 | Product variant | [Another Product] | Fresh Baked Pastries |
| 15 | Convenience | [Location Benefit] | Free Parking Available |

#### `ecommerce`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Product + buy | Shop [Product] Online | Shop Soy Candles Online |
| 2 | Brand | [Brand Name] | Lumino Candle Co |
| 3 | Shipping | Free Shipping Over $[X] | Free Shipping Over $50 |
| 4 | Product range | [Range/Collection] | Hand-Poured Soy Candles |
| 5 | CTA | Shop Now | Shop Now |
| 6 | Quality | [Quality Signal] | 100% Natural Soy Wax |
| 7 | Gift angle | Perfect Gift Idea | Perfect Gift Idea |
| 8 | Australian | Australian Made & Owned | Australian Made & Owned |
| 9 | Sale/offer | [Current Offer] | 20% Off First Order |
| 10 | CTA variant | Order Online Today | Order Online Today |
| 11 | Range | [# Products]+ [Products] | 50+ Scents Available |
| 12 | Speed | Fast Australia-Wide Delivery | Fast Australia-Wide Delivery |
| 13 | Returns | Easy Returns | Easy Returns |
| 14 | Niche/feature | [Product Feature] | Long-Lasting 60hr Burn Time |
| 15 | Bundle | Gift Sets Available | Gift Sets Available |

#### `hospitality-tourism`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Type + location | [Type] in [City] | Hotel in Toowoomba |
| 2 | Experience | [Experience Highlight] | Boutique Country Retreat |
| 3 | Brand | [Business Name] | Range View Lodge |
| 4 | CTA | Book Now — Best Rates | Book Now — Best Rates |
| 5 | Feature | [Key Feature] | Pool, Spa & Restaurant |
| 6 | Event/attraction | Near [Attraction] | Near Carnival of Flowers |
| 7 | Rating | [Star Rating] Rated | 4.8 Star Rated |
| 8 | Location | [Neighbourhood/Area] | Heart of the CBD |
| 9 | CTA variant | Check Availability | Check Availability |
| 10 | Price | From $[X] Per Night | From $120 Per Night |
| 11 | Special | [Current Deal] | Midweek Special Available |
| 12 | Group | Perfect for [Group] | Perfect for Couples |
| 13 | Amenity | [Unique Amenity] | Free Breakfast Included |
| 14 | Season | [Season] Getaway | Winter Getaway Special |
| 15 | Direct booking | Book Direct — Save More | Book Direct — Save More |

#### `health-medical`:

| # | Category | Template | Example |
|---|----------|----------|---------|
| 1 | Practitioner + city | [Practitioner] [City] | Dentist Toowoomba |
| 2 | Practice name | [Practice Name] | Toowoomba Family Dental |
| 3 | Service | [Key Service] | General & Cosmetic Dentistry |
| 4 | CTA | Book Online Now | Book Online Now |
| 5 | Availability | Accepting New Patients | Accepting New Patients |
| 6 | Trust | Experienced & Caring Team | Experienced & Caring Team |
| 7 | Convenience | [Location/Parking] | Free Parking On-Site |
| 8 | Payment | [Payment Info] | HICAPS & Payment Plans |
| 9 | Emergency | Emergency [Service] Available | Emergency Dental Available |
| 10 | CTA variant | Schedule Your Appointment | Schedule Your Appointment |
| 11 | Family | Family-Friendly Practice | Family-Friendly Practice |
| 12 | Tech/quality | [Equipment/Approach] | Latest Digital Technology |
| 13 | Treatment | [Specific Treatment] | Teeth Whitening From $[X] |
| 14 | Comfort | Gentle & Comfortable Care | Gentle & Comfortable Care |
| 15 | Insurance | All Health Funds Accepted | All Health Funds Accepted |

### Description formula (4 descriptions per archetype)

**`local-service` / `trades-home`:**
1. Professional [service] across [region]. [Service types]. Free quotes.
2. Local [service] experts servicing [Town], [Town], [Town] & surrounds. Free quotes.
3. Secure your [outcome] with professional [service]. Call for a free quote today.
4. Competitive rates. Quality [equipment]. Local [region] family business. Free quotes.

**`professional-b2b`:**
1. Expert [service] for [client types] across [region]. [X] years experience. Book a free consultation.
2. [Outcome] with [service] from [Business Name]. [Credential]. Serving [region].
3. [USP]. Tailored [service] for your business. Call or book online today.
4. Trusted by [X]+ businesses. [Service types]. Fixed-fee / transparent pricing.

**`local-retail`:**
1. Visit [Business Name] in [suburb] for [specialty]. Open [hours]. [Differentiator].
2. [Product/experience] in the heart of [city]. Locally owned. Visit us today.
3. Discover [city]'s favourite [type]. [Signature items]. [Location detail].
4. [Vibe description]. [Menu/product highlights]. Free parking. Open [days].

**`ecommerce`:**
1. Shop [product range] at [Brand]. [Quality signal]. Free shipping over $[X]. Shop now.
2. Australian-made [products]. [# products]+ options. Fast delivery. Easy returns.
3. Find the perfect [product] — [use case]. Order online today. [Offer if applicable].
4. [Quality/material detail]. Handcrafted in [location]. Gift sets available. Shop now.

**`hospitality-tourism`:**
1. Book [type] in [city] — [experience]. [Key features]. Book direct for best rates.
2. [Star rating] rated [type] near [attraction/area]. [Amenities]. Check availability now.
3. Plan your [city] getaway. [Room types/options]. From $[X]/night. Book online.
4. [Unique selling point]. [Location benefit]. [Amenity highlights]. Reserve your stay.

**`health-medical`:**
1. [Practice Name] — [services] in [city]. Accepting new patients. Book online or call today.
2. Experienced [practitioners] providing [services]. [Payment options]. New patients welcome.
3. [Specific treatment] at [Practice Name]. [Technology/approach]. Gentle, caring team.
4. Family-friendly [practice type] in [suburb]. [Convenience features]. Book your appointment.

### Ad copy rules (ALL archetypes)

> **GOTCHA — No phone numbers in ad text.** Google policy rejects ads with phone numbers in headlines or descriptions. Use the **Call extension** instead.

> **Character counting:** Always check character counts. Headlines max 30, descriptions max 90. One character over = rejected.

> **GOTCHA — Australian English for Australian businesses.** Use "specialise" not "specialize", "colour" not "color", "centre" not "center". And use local terminology — "bore drilling" not "borewell", "tradies" not "handymen".

### Restricted category ad copy rules

**`health-medical`:**
- Cannot claim to cure diseases or conditions
- Cannot use before/after imagery in ads
- Cannot make guarantees about treatment outcomes
- Can say: "experienced", "caring", "gentle", "professional"
- Cannot say: "guaranteed results", "cure your pain", "best dentist"
- Remarketing restrictions: cannot remarket to people based on health conditions

**`professional-b2b` (finance/legal):**
- Financial services may require licensing disclosures
- Legal services cannot guarantee outcomes
- Must comply with state/territory advertising rules for regulated professions

**`ecommerce` (alcohol, if applicable):**
- Age-gating requirements
- Cannot target minors
- Placement restrictions apply

### Ad strength target

Aim for **Good or above (80%+)** for all archetypes. Key factors:
- Use all 15 headline slots
- Use all 4 description slots
- Include keywords in headlines
- Make headlines and descriptions unique from each other
- Add sitelinks and callouts

`📸 Screenshot opportunity: RSA editor with all headlines and descriptions filled`

---

## Phase 8: Extensions / Assets (BRANCHED)

Extensions make your ad bigger and give more ways to click. They increase CTR by 10–15% and are free to add.

### Must-have extensions (ALL archetypes)

| Extension | What | Notes |
|-----------|------|-------|
| **Sitelinks** (2–4) | Links to key pages | Every archetype benefits. Single-page sites: use anchor links or homepage. |
| **Callouts** (4–8) | Short trust phrases | "Free Quotes", "Family-Owned", "Australian Made", etc. |

### Archetype-specific extensions

| Archetype | Critical Extensions | Notes |
|-----------|-------------------|-------|
| `local-service` / `trades-home` | **Call**, Callouts, Sitelinks | Click-to-call is critical — most leads come via phone |
| `professional-b2b` | **Call**, **Structured snippets** (Services: ...), Sitelinks | List services in structured snippets |
| `local-retail` | **Location** (link GBP), **Call**, Callouts | Location extension shows address + map pin + directions |
| `ecommerce` | **Promotion** (sale/discount), **Price**, Sitelinks (product categories) | Promotion extensions show offers. Price extensions list products with prices. |
| `hospitality-tourism` | **Call**, **Location**, **Price** (room rates), **Image** (property photos) | Image extensions show a thumbnail — great for visual businesses |
| `health-medical` | **Call**, **Location**, **Structured snippets** (Services: ...) | List treatments in structured snippets |

### Sitelinks per archetype

| Archetype | Sitelink Ideas |
|-----------|---------------|
| `local-service` | Get a Free Quote, Our Services, About Us, Contact |
| `professional-b2b` | Book a Consultation, Our Services, About the Team, Client Testimonials |
| `local-retail` | Our Menu, Visit Us, About Us, Gallery |
| `ecommerce` | Shop All, New Arrivals, Best Sellers, Sale |
| `hospitality-tourism` | Book Now, Rooms & Rates, Gallery, Things to Do |
| `health-medical` | Book Online, Our Services, Meet the Team, Patient Info |

### Callout ideas per archetype

| Archetype | Callout Examples |
|-----------|-----------------|
| `local-service` | Free Quotes, Locally Owned, Licensed & Insured, Competitive Rates, [X] Years Experience, Fast Response |
| `professional-b2b` | Free Initial Consultation, Fixed-Fee Pricing, [X] Years Experience, Industry Specialists, Trusted by [X]+ Clients |
| `local-retail` | Open 7 Days, Free Parking, Locally Owned, Fresh Daily, [Award/Rating] |
| `ecommerce` | Free Shipping Over $[X], Easy Returns, Australian Made, Secure Payment, Gift Wrapping Available |
| `hospitality-tourism` | Free WiFi, Free Breakfast, Free Parking, Pool & Spa, Pet Friendly, Best Rate Guarantee |
| `health-medical` | Accepting New Patients, All Health Funds, Payment Plans, Emergency Appointments, Family Friendly |

### Nice-to-have extensions (add after launch)

| Extension | Best For | When |
|-----------|---------|------|
| **Business name + logo** | All | After advertiser verification approved |
| **Location** | local-retail, health-medical, hospitality | After Google Business Profile claimed + linked |
| **Image** | hospitality-tourism, ecommerce, trades-home | After approval (Google reviews image quality) |
| **Promotion** | ecommerce, hospitality | When running a sale or seasonal offer |

`📸 Screenshot opportunity: Extensions section filled out`

---

## Phase 9: Budget (BRANCHED)

### Daily budget calculation

Daily budget = weekly budget / 7

| Weekly budget | Daily budget | Monthly estimate |
|--------------|-------------|-----------------|
| $28/week | $4/day | ~$120/month |
| $50/week | $7/day | ~$215/month |
| $70/week | $10/day | ~$305/month |
| $140/week | $20/day | ~$610/month |
| $350/week | $50/day | ~$1,525/month |

> **Google may overspend on individual days** (up to 2x daily budget) but balances over the month. Don't panic at daily spikes — check weekly totals.

### Industry CPC benchmarks (Australia, 2026 approximate)

These are RANGES — actual CPC depends on competition, location, and quality score.

| Industry / Archetype | Avg CPC Range | Typical CPL | Notes |
|---------------------|---------------|-------------|-------|
| **Trades — general** (plumber, electrician) | $3–$12 | $20–$60 | High competition in metro, lower in regional |
| **Trades — specialist** (bore drilling, underpinning) | $4–$15 | $30–$80 | Lower volume, higher intent |
| **Home services** (builder, roofer, pool) | $5–$18 | $40–$100 | High ticket = higher CPC acceptable |
| **Professional — accounting** | $5–$20 | $30–$80 | Competitive in major cities |
| **Professional — legal** | $10–$50+ | $50–$200+ | Most expensive category. Personal injury astronomical. |
| **Professional — IT/tech** | $5–$25 | $40–$100 | B2B keywords expensive |
| **Cafe / restaurant** | $0.50–$3 | $5–$15 | Low CPC, high volume, low conversion value |
| **Retail / boutique** | $0.50–$4 | $5–$20 | Low CPC, conversion = visit |
| **E-commerce — general** | $0.50–$5 | N/A (use ROAS) | Measure return on ad spend, not CPL |
| **E-commerce — niche** | $1–$8 | N/A (use ROAS) | Less competition = lower CPC |
| **Hospitality / accommodation** | $1–$8 | $15–$50 | Seasonal variation, event-driven spikes |
| **Tourism / activities** | $1–$6 | $10–$40 | Highly seasonal |
| **Dentist** | $4–$15 | $25–$70 | Competitive in metro |
| **Physio / chiro / allied health** | $3–$12 | $20–$60 | Less competitive than dental |
| **GP / medical** | $3–$10 | $15–$50 | Lower competition (many don't advertise) |

### Budget strategy by archetype

| Archetype | Minimum viable budget | Recommended budget | Strategy |
|-----------|----------------------|-------------------|----------|
| `local-service` | $4/day ($28/week) | $10–$15/day | High-intent only. Every click must count. |
| `professional-b2b` | $10/day ($70/week) | $20–$30/day | Higher CPC means you need more budget for meaningful data. |
| `local-retail` | $3/day ($21/week) | $5–$10/day | Low CPC, but low conversion value too. Volume game. |
| `ecommerce` | $10/day ($70/week) | $20–$50/day | Need volume for Shopping + Search. Track ROAS not CPL. |
| `hospitality-tourism` | $5/day ($35/week) | $10–$20/day | Seasonal — increase budget during peak periods. |
| `health-medical` | $7/day ($49/week) | $15–$25/day | Appointment value justifies decent spend. |
| `trades-home` | $10/day ($70/week) | $20–$30/day | High ticket, high CPC. Need enough budget for data. |

> **If client's budget is below minimum viable:** Consider Meta Ads only (lower CPCs, better for awareness/demand generation). Google Ads needs enough budget to get 3–5 clicks/day minimum to learn anything.

---

## Phase 10: Review & Publish

### Pre-publish checklist (ALL archetypes)

- [ ] Campaign type matches archetype recommendation (Search / Shopping / etc.)
- [ ] Networks = Google Search only (both partners and display unchecked) — unless archetype exception
- [ ] Location targeting = correct area (radius, towns, or national)
- [ ] Location options = correct setting ("Presence" for most, "Presence or interest" for hospitality-tourism only)
- [ ] Ad schedule = appropriate for archetype (business hours / 24/7 / etc.)
- [ ] Keywords = all phrase match, correct count for budget
- [ ] Negative keywords = universal list + archetype-specific negatives added
- [ ] Headlines = 15 filled, no phone numbers, under 30 chars each
- [ ] Descriptions = 4 filled, under 90 chars each
- [ ] Call extension = business phone number added (if phone-based archetype)
- [ ] Callouts = 4–8 trust phrases added
- [ ] Sitelinks = 2–4 added
- [ ] Budget = correct daily amount
- [ ] Conversion tracking = installed and verified (green tick)
- [ ] Event snippets = added to conversion pages
- [ ] Advertiser verification = submitted
- [ ] Ad strength = 80%+ (Good or above)
- [ ] Ad copy uses correct Australian English
- [ ] No restricted category policy violations

### Policy quick-check by archetype

| Archetype | Watch Out For |
|-----------|--------------|
| ALL | Phone numbers in ad text, excessive caps, misleading claims, competitor trademarks |
| `health-medical` | No cure claims, no before/after, no outcome guarantees, remarketing restrictions |
| `professional-b2b` (finance) | Licensing disclosures, no guaranteed returns |
| `professional-b2b` (legal) | No guaranteed outcomes, jurisdiction disclaimers |
| `ecommerce` (alcohol) | Age restrictions, placement limits |
| `ecommerce` (supplements) | Health claim restrictions |

### After publishing

Campaign enters review (typically 1 business day). Status changes:
1. **Under review** → Google checking ad policy compliance
2. **Eligible** → Approved, waiting for verification
3. **Active** → Running and showing ads (once verification clears)

---

## Phase 11: Post-Launch Management (BRANCHED)

### Day 1–3: Monitor (ALL archetypes)

- Are ads showing? Check for disapprovals.
- Don't change anything yet — let data accumulate.
- Verify conversion tracking is firing (submit a test form/booking yourself).

### Day 3–7: First optimisation (ALL archetypes)

- **Check Search Terms report** (Campaigns → Keywords → Search Terms)
- Add any irrelevant actual searches as negative keywords
- This is the #1 most important weekly task across ALL archetypes

### Weekly routine (15 minutes)

1. **Search Terms report** — add negatives for junk searches
2. **Check CPC** — compare against industry benchmark table above
3. **Check CTR** — see benchmark table below
4. **Check conversions** — any keywords with 20+ clicks and 0 conversions → pause
5. **Check budget pacing** — spending full daily budget? If underspending, keywords may be too narrow

### KPI benchmarks by archetype

| Archetype | Target CTR | Warning CTR | Target Conversion Rate | Target CPL / ROAS |
|-----------|-----------|-------------|----------------------|-------------------|
| `local-service` | > 4% | < 2% | > 5% | CPL < $50 |
| `professional-b2b` | > 3% | < 1.5% | > 3% | CPL < $80 |
| `local-retail` | > 5% | < 2.5% | > 3% (directions/calls) | CPL < $15 |
| `ecommerce` (Search) | > 3% | < 1.5% | > 2% | ROAS > 400% |
| `ecommerce` (Shopping) | > 1% | < 0.5% | > 1.5% | ROAS > 400% |
| `hospitality-tourism` | > 4% | < 2% | > 3% | CPL < $40 |
| `health-medical` | > 4% | < 2% | > 5% | CPL < $50 |
| `trades-home` | > 3% | < 1.5% | > 4% | CPL < $80 |

### Monthly review (ALL archetypes)

| Metric | Action if bad |
|--------|--------------|
| **CPC above benchmark** | Add negatives, improve Quality Score, review keyword competition |
| **CTR below target** | Rewrite ad copy, check keyword relevance, test new headlines |
| **Conversion rate below target** | Improve landing page, check form/booking works, check mobile experience |
| **CPL above target** | Pause expensive keywords, focus budget on converters, add negatives |
| **Quality Score < 4** | Match ad copy to keywords, improve landing page relevance |

### Bidding evolution (ALL archetypes)

| Milestone | Strategy | Why |
|-----------|----------|-----|
| **Launch (0 conversions)** | Manual CPC or Maximize Conversions (see Phase 5) | Control or explore, archetype-dependent |
| **5–15 conversions** | Maximize Conversions (no target) | Some data — let Google start learning |
| **15–30 conversions** | Maximize Conversions with Target CPA | Enough data to set a target |
| **30+ conversions** | Target CPA or Target ROAS | Algorithm has enough data to optimise effectively |
| **B2B with offline imports** | Target CPA using offline conversion data | Optimise for REAL clients, not just form fills |

> **Volume rule:** Google recommends daily budget of at least 15x your Target CPA. If target CPA is $50, that's $750/day. Don't set a Target CPA until you have both the data AND the budget to support it.

---

## Gotchas & Hard-Won Lessons

Real issues encountered during actual campaign setups. Each one cost time or money to discover.

| # | Gotcha | Impact | Prevention |
|---|--------|--------|-----------|
| 1 | **Timezone locked at account creation** | All scheduling and reporting offset permanently | Triple-check timezone during account setup |
| 2 | **Performance Max default** | Budget spread across Display, YouTube, Gmail — wasted on small budgets | Always explicitly select campaign type |
| 3 | **Phone number in ad text** | Ad rejected by policy | Use Call extension, never put numbers in headlines/descriptions |
| 4 | **"Presence or interest" location default** | Ads shown to people not in service area | Change to "Presence" for all archetypes except hospitality-tourism |
| 5 | **SPA sites fail Google's scanner** | Red "No keywords found" error | Ignore warning, enter keywords manually, use page-load tracking |
| 6 | **Verification takes 3–5 business days** | Ads paused until approved | Submit verification on day 1. Build campaign while waiting. |
| 7 | **Wrong profile for client verification** | "About this advertiser" shows your name | Always create a new business payments profile per client |
| 8 | **Search Partners + Display Network checked by default** | Budget leaks to low-quality placements | Uncheck both immediately |
| 9 | **Australian English matters** | Wrong terminology misses local searches | Always localise. "Bore drilling" not "borewell". |
| 10 | **Broad match on small budgets** | Budget consumed by irrelevant searches | Phrase match only until you have data |
| 11 | **Smart bidding on low volume** | Erratic spend, bad optimisation with <15 conversions/month | Use Manual CPC until volume supports smart bidding |
| 12 | **Health/medical ad restrictions** | Ads rejected for cure claims or before/after imagery | Follow restricted category rules. No outcome guarantees. |
| 13 | **E-commerce without Merchant Center** | Can't run Shopping campaigns (the best campaign type for products) | Set up Google Merchant Center BEFORE campaign build |
| 14 | **No negative keywords on launch** | First week budget wasted on junk clicks | Always add universal + archetype negatives before going live |
| 15 | **Ignoring Search Terms report** | Ongoing budget bleed to irrelevant searches | Check Day 3, then weekly. This is THE most important optimisation task. |

---

## E-commerce Addendum: Google Merchant Center Setup

**Only for `ecommerce` archetype.** Shopping campaigns require a Google Merchant Center account with a product feed.

### Quick setup steps:
1. Create account at merchants.google.com
2. Verify and claim your website URL
3. Upload product feed (product name, price, image, availability, GTIN/MPN, description)
   - Manual: CSV/Google Sheet upload
   - Automated: Shopify/WooCommerce/BigCommerce have built-in Merchant Center integrations
   - Lovable sites: manual feed or use a feed management tool
4. Link Merchant Center to Google Ads account
5. Fix any product disapprovals (missing fields, policy violations, image quality)
6. Create Shopping campaign in Google Ads (linked to Merchant Center)

> **Product feed quality = Shopping campaign quality.** Bad titles, missing images, or wrong prices = disapproved products and wasted spend. Get the feed right before spending money.

---

## Files This Skill Produces

When used via `/create-plan` or `/implement`:
- Client-specific keyword list with match types (tailored to archetype)
- Client-specific RSA copy (15 headlines + 4 descriptions, archetype-appropriate)
- Client-specific negative keyword list (universal + archetype-specific)
- Conversion tracking setup instructions (archetype-appropriate conversion types)
- Campaign configuration summary
- For ecommerce: Merchant Center setup checklist

---

## Related Files

- **Parent skill:** `.claude/skills/paid-ads.md` — Discovery questions (Q1–Q5) + budget split logic. Run this first.
- **Meta Ads skill:** `.claude/skills/meta-ads.md` — Facebook/Instagram campaign setup (companion skill)

---

## Skill Metadata

- **Version:** 2.0
- **Created:** 2026-03-12
- **Last updated:** 2026-03-13
- **Built from:** Real hands-on campaign setup (Grundy Drilling Company, March 2026) + research across business types
- **Platform version:** Google Ads interface as of March 2026
- **Business archetypes:** 8 (local-service, local-service-lsa, professional-b2b, local-retail, ecommerce, hospitality-tourism, health-medical, trades-home)
