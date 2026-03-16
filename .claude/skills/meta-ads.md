---
name: meta-ads
description: Full Meta (Facebook/Instagram) Ads campaign setup — Business Portfolio, pixel, targeting, creative, lead forms, CRM automation, and optimisation. Branched by business archetype.
---

# Skill: Meta Ads Campaign Setup — Multi-Business-Type

**Purpose:** Complete, repeatable workflow for setting up Facebook & Instagram ad campaigns via Meta Ads Manager for ANY business type. Uses decision-tree logic: classify the business → every downstream setting adapts automatically.

**When to use:** New client needs Facebook/Instagram ads, or existing client needs a new campaign.

**Prerequisites skill:** Run `paid-ads` discovery questions first (Q1–Q5) before starting this skill. The archetype classification from `paid-ads` Phase 1 drives every setting in this skill.

**Version:** 1.1 — Built live during Grundy Drilling campaign setup (2026-03-14). Updated with CRM automation, lead delivery, and pixel connection gotchas.

---

## How This Skill Works

Every phase reads the **business archetype** (set in Phase 0) and adjusts its advice. Look for conditional blocks like:

```
IF archetype = local-service → do X
IF archetype = ecommerce → do Y
```

Claude should auto-classify the business from discovery answers. Aaron should never need to pick an archetype manually.

---

## Phase 0: Business Classification

**Same archetypes as google-ads skill.** Read the paid-ads discovery answers (Q1–Q5) and classify:

| Archetype | Examples | Meta Ads Signal |
|-----------|----------|-----------------|
| `local-service` | Plumber, bore driller, cleaner, pest control | Lead forms, location targeting, phone calls matter |
| `local-service-lsa` | Same as above (LSA status only affects Google, not Meta) | Treat same as `local-service` for Meta |
| `professional-b2b` | Accountant, lawyer, IT consultant | Longer copy, website conversions, LinkedIn may be better |
| `local-retail` | Cafe, restaurant, salon, boutique | Store visits, directions, visual-heavy, promotions |
| `ecommerce` | Online shop, product brand | Catalog ads, purchase tracking, Shopping integration |
| `hospitality-tourism` | Hotel, tour operator, holiday rental | Booking conversions, visual storytelling, interest + location targeting |
| `health-medical` | Dentist, physio, vet | Special Ad Category (housing/credit/employment rules may apply), booking focus |
| `trades-home` | Builder, roofer, painter, pool builder | Portfolio/before-after creative, higher ticket, lead forms |

### Archetype Variables for Meta

| Variable | `local-service` / `trades-home` | `professional-b2b` | `local-retail` | `ecommerce` | `hospitality-tourism` | `health-medical` |
|----------|--------------------------------|--------------------:|---------------:|-------------:|----------------------:|------------------:|
| **Campaign objective** | Leads | Leads or Traffic | Awareness / Traffic | Sales | Traffic / Engagement | Leads |
| **Conversion event** | Lead (instant form or website) | Lead / ViewContent | Store visits / directions | Purchase / AddToCart | Booking / ViewContent | Lead (booking form) |
| **Primary creative** | Photo of work/team + lead form | Professional headshot + value prop | Food/product photos + offer | Product shots / lifestyle | Destination imagery / video | Friendly practice photos |
| **Ad format** | Single image or video | Single image | Carousel / video | Carousel / collection / dynamic | Video / carousel | Single image or video |
| **Targeting style** | Location + age + broad interests | Job title / industry / company size | Tight radius (5-15km) | Interest + behaviour + lookalike | Interest + travel intent + location FROM | Location + age + health interests |
| **Location radius** | 50-150km (service area) | City / state / national | 5-25km (foot traffic) | State / national / international | National + feeder cities | 10-30km |
| **Avg CPC (AUD)** | $0.50-$3 | $1-$5 | $0.30-$2 | $0.50-$3 | $0.50-$3 | $1-$4 |
| **Avg CPL (AUD)** | $10-$50 | $20-$80 | $3-$15 (per visit/action) | N/A (ROAS-based) | $10-$40 | $15-$60 |
| **Budget min (AUD/day)** | $15 | $20 | $10 | $20 | $15 | $15 |
| **Visual importance** | Medium-High | Low-Medium | High | High | Very High | Medium |

---

## Phase 1: Prerequisites & Access

Before touching Ads Manager, confirm ALL of these:

### 1.1 — Facebook account setup
- [ ] Your Facebook account has **2FA enabled** — required for full Meta Business portfolio admin access
  - Go to: facebook.com/security/2fac/setup/intro
  - Without 2FA you get "partial access" — can't create ad accounts
- [ ] You have a personal Facebook account (needed to manage everything)

### 1.2 — Meta Business Portfolio (formerly Business Manager)
- [ ] Go to business.facebook.com
- [ ] You have a business portfolio with **full admin access**
- [ ] **CRITICAL:** Check if the client's portfolio is restricted BEFORE creating assets under it
  - Settings → Business info → look for any restriction banners
  - If restricted: create ALL assets under your agency portfolio instead
  - If appeal denied: the portfolio is permanently dead — all child assets are tainted

> **Gotcha:** When a Meta Business portfolio is restricted, ALL child assets (ad accounts, pixels, pages) are tainted and restricted too. Appeal denial is final. Always have the agency portfolio as fallback.

### 1.3 — Facebook Page
- [ ] Client's Facebook Business Page exists
- [ ] Page branding is current (name, logo, cover photo, contact info, hours)
- [ ] Page is connected to the business portfolio you're using for ads
  - If page is owned by a different (restricted) portfolio, the current owner must approve a sharing request
  - Workaround: if you have personal full control, Ads Manager may let you select it at ad level anyway
- [ ] Page category is accurate (e.g. "Drilling Contractor", "Plumber", "Cafe")

> **Gotcha:** Personal full control of a Facebook Page ≠ ability to move it between portfolios. Ownership is at portfolio level. You can manage content but can't transfer ownership.

### 1.4 — Instagram (optional but recommended)
- [ ] Instagram Professional account (Creator or Business)
- [ ] Linked to the Facebook Page (Instagram Settings → Linked Accounts → Facebook)
- [ ] Connected to the business portfolio

### 1.5 — Ad Account
- [ ] Ad account exists under the correct business portfolio
- [ ] Create if needed: Settings → Ad accounts → + Add → Create new
  - **Name:** "[Client Name]" (e.g. "Grundy Drilling")
  - **Timezone:** Australia/Brisbane (AEST) — cannot be changed later!
  - **Currency:** AUD — cannot be changed later!
- [ ] You are assigned to the ad account (People tab → Add yourself with full access)
- [ ] Payment method added (client's credit card)
  - Ad Account Settings → Payment Methods → Add
  - Enter client's ABN for tax invoices

> **Gotcha:** Timezone and currency are locked at ad account creation. Always double-check before creating.

### 1.6 — Meta Pixel
- [ ] Pixel created in Events Manager (Connect Data Sources → Web)
- [ ] Named clearly: "[Client Name] Pixel" (e.g. "Grundy Drilling Pixel")
- [ ] **CRITICAL: Connect pixel to ad account** — creating a pixel does NOT auto-connect it
  - Go to: Events Manager → Settings → Data Sources → Datasets & pixels → Connected assets
  - Click "Add assets" → select your ad account → Save
  - **Must reload Ads Manager tab after connecting** (it caches dropdown options)
- [ ] Base pixel code installed in website `<head>` tag
- [ ] Standard events configured:
  - `PageView` — fires on all pages (automatic with base code)
  - `Lead` — fires on thank-you/confirmation page
  - Optional: `Contact` — fires on click-to-call
- [ ] Verified with **Meta Pixel Helper** Chrome extension (green checkmark)
- [ ] Verified in Events Manager → Test Events

> **Gotcha:** Creating a pixel does NOT connect it to your ad account. You must manually link it via Data Sources → Connected assets. Without this, the pixel won't appear in the Ads Manager dropdown when building a campaign.

> **Gotcha:** When creating a campaign, Ads Manager can default to a WRONG pixel from another project you have access to. Always verify pixel name AND ID match the current project. Close and reopen the Ads Manager tab after connecting a new pixel — it caches the dropdown.

**For Lovable + Netlify sites:**
- Add pixel code to `index.html` `<head>` via Lovable prompt
- For the Lead event on /thank-you, add `fbq('track', 'Lead');` in a script tag or component
- Must have Netlify `_redirects` file (`/*  /index.html  200`) for SPA routes to work

---

## Phase 2: Facebook Page Optimisation (Pre-Ads)

**Do this BEFORE running any ads.** Your page IS your ad's landing experience — people click your profile from ads.

### Required updates:
1. **Page name** — must match business name exactly
2. **Profile picture** — logo or recognisable brand image (displays at 170x170px on desktop)
3. **Cover photo** — hero image: equipment, team at work, or landscape with branding (820x312px)
4. **Category** — most accurate business category
5. **Contact info** — phone, email, website URL
6. **Address** — full business address
7. **Service area** — if applicable (service businesses)
8. **About/Bio** — 1-2 sentences: what you do, where, CTA
9. **Hours** — operating hours
10. **CTA button** — set to "Get Quote", "Call Now", or "Send Message"

### By archetype:

| Archetype | Cover photo | CTA button | Bio emphasis |
|-----------|-------------|------------|-------------|
| `local-service` / `trades-home` | Rig/equipment on site, team working | Get Quote / Call Now | Service area + services + phone |
| `professional-b2b` | Office / team headshot / branded | Contact Us / Book Now | Expertise + credentials + location |
| `local-retail` | Storefront / hero product / food | Order Now / Get Directions | Location + hours + what makes you special |
| `ecommerce` | Product hero / lifestyle | Shop Now | What you sell + shipping + USP |
| `hospitality-tourism` | Destination / room / experience | Book Now | Location + experience + booking |
| `health-medical` | Practice exterior / friendly team | Book Now | Services + qualifications + location |

---

## Phase 3: Campaign Creation

### 3.1 — Open Ads Manager
1. Go to adsmanager.facebook.com (or Meta Business Suite → Ads Manager)
2. Select the correct ad account from the dropdown — verify the name matches your client
3. Click **+ Create**

### 3.2 — Choose campaign objective

| Archetype | Recommended objective | Why |
|-----------|----------------------|-----|
| `local-service` / `trades-home` | **Leads** | Optimises for form submissions — you want enquiries |
| `professional-b2b` | **Leads** or **Traffic** | Leads if you have a form; Traffic if sending to website |
| `local-retail` | **Awareness** or **Traffic** | Drive foot traffic and local visibility |
| `ecommerce` | **Sales** | Optimises for purchases with conversion tracking |
| `hospitality-tourism` | **Traffic** or **Engagement** | Drive bookings via website; engagement for inspiration content |
| `health-medical` | **Leads** | Appointment bookings via form |

### 3.3 — Campaign settings
1. **Campaign name:** `[Client] — [Objective] — [Month Year]`
   - Example: "Grundy Drilling — Lead Gen — Mar 2026"
2. **Campaign Budget Optimisation (CBO):** ON
   - This lets Meta distribute budget across ad sets based on performance
   - Better for small budgets — don't split manually
3. **Daily budget:** Set based on archetype minimums (see Phase 0 table)
4. **A/B Test:** OFF (not enough budget to split test at campaign level on small budgets)
5. **Special Ad Categories:** Check if applicable
   - Housing, Employment, Credit, Social Issues — these restrict targeting options
   - Most service businesses: NONE
   - Health/medical: usually NONE unless promoting health insurance

### 3.4 — CRITICAL: Verify Pixel/Dataset selection
- In the campaign setup, look for "Conversion location" or "Dataset" or "Pixel"
- **Verify the pixel name AND ID match your current project**
- If wrong: click the dropdown and select the correct pixel
- If the correct pixel doesn't appear: go to Events Manager first and ensure the pixel is connected to this ad account

> **Gotcha:** Meta Ads Manager can show pixels from other projects you have access to. It may default to the WRONG one. Always check.

---

## Phase 4: Ad Set Creation (Targeting)

Create 2 ad sets to start (Meta's CBO will allocate budget to the winner):

### 4.1 — Ad Set 1: Broad targeting

**Name:** `[Location] — Broad`

**Conversion event:**
- `local-service` / `trades-home`: Lead (Instant Form or Website)
- `ecommerce`: Purchase
- `local-retail`: Link clicks or Store visits
- Others: Lead or ViewContent

**Location targeting:**

| Archetype | Location strategy |
|-----------|------------------|
| `local-service` | Town/city + radius covering service area (e.g. Toowoomba + 100km) |
| `trades-home` | Same as local-service |
| `local-retail` | Town/city + 10-25km radius |
| `ecommerce` | State or national |
| `hospitality-tourism` | Target where customers ARE (feeder cities), not where business is |
| `professional-b2b` | City or state |
| `health-medical` | Town/city + 15-30km |

- **Location type:** "People living in or recently in this location" (NOT "interested in")

**Age:**
- `local-service` / `trades-home`: 30-65+
- `local-retail`: 18-65+
- `professional-b2b`: 25-55
- `health-medical`: 25-65+
- `ecommerce`: depends on product

**Gender:** All (unless product/service is gender-specific)

**Detailed targeting:** NONE for Ad Set 1 — let Meta's algorithm find your audience. Broad targeting often outperforms interest targeting on small budgets because it gives Meta more room to optimise.

**Placements:** Advantage+ (automatic) — let Meta decide where to show ads.

### 4.2 — Ad Set 2: Interest-based targeting

**Name:** `[Location] — [Interest theme]`

Same location, age, gender as Ad Set 1, but ADD detailed targeting:

| Archetype | Interest targeting suggestions |
|-----------|-------------------------------|
| `local-service` (bore drilling) | Farming, Agriculture, Livestock, Rural property, Acreage, Irrigation, Horse property |
| `local-service` (plumber/electrician) | Homeowners, Home improvement, DIY, Property investment |
| `trades-home` (builder/roofer) | Home renovation, Architecture, Building design, New home |
| `local-retail` (cafe) | Coffee, Food, Brunch, Local events |
| `ecommerce` | Depends on product — use competitor brands, related interests |
| `hospitality-tourism` | Travel, Adventure, Holidays, specific destinations |
| `professional-b2b` | Business owners, Small business, Industry-specific |
| `health-medical` | Health & wellness, Fitness, Family, specific conditions |

**Placements:** Same as Ad Set 1 (Advantage+).

---

## Phase 5: Ad Creative

### 5.1 — How many ads to create

Start with **2 ads per ad set** (4 total across 2 ad sets). This gives Meta enough to test without spreading a small budget too thin.

### 5.2 — Ad format by archetype

| Archetype | Best format | Why |
|-----------|------------|-----|
| `local-service` | Single image + lead form | Simple, fast to create, works well for service enquiries |
| `trades-home` | Carousel (before/after or portfolio) | Showcases quality of work |
| `local-retail` | Carousel or video | Visual products/food/atmosphere |
| `ecommerce` | Carousel / Collection / Dynamic | Show multiple products |
| `hospitality-tourism` | Video / carousel | Sell the experience visually |
| `professional-b2b` | Single image | Professional, clean, benefit-focused |
| `health-medical` | Single image or video | Friendly, approachable, trustworthy |

### 5.3 — Ad copy formula

Works for ALL archetypes. Adapt the language:

```
HOOK:    [Problem or question the customer has — stop the scroll]
BODY:    [How the business solves it — 2-3 sentences max]
PROOF:   [Trust signal — years experience, reviews, local, qualifications]
CTA:     [Clear action — Get a free quote / Book now / Shop now / Call today]
```

**Ad copy fields:**
- **Primary text** (above the image): The full HOOK + BODY + PROOF + CTA. Keep first line under 125 characters (the "above the fold" text before "See more").
- **Headline** (below the image): Short, benefit-focused (e.g. "Free Quote Today", "Shop the Range", "Book Your Stay")
- **Description** (below headline): Phone number, key differentiator, or secondary CTA
- **CTA button:** Match objective — Get Quote, Learn More, Shop Now, Book Now, Call Now

### 5.4 — Creative persona approach (for local-service / trades-home)

Create 2 ads targeting different customer personas:

**Ad A — Primary persona** (the most common customer)
- Copy speaks directly to their situation
- Image shows the work environment they relate to

**Ad B — Secondary persona** (the next most common)
- Different angle, different pain point
- Different image

*Example for bore drilling:*
- Ad A: Farmer persona — "Sick of watching your dams dry up?"
- Ad B: Acreage owner persona — "Tired of relying on town water?"

### 5.5 — Image best practices
- Real photos outperform stock photos — always use client's photos if available
- Show the work being done, the team, the result
- Bright, high-quality, well-lit
- Text overlay: minimal (Meta penalises images with >20% text coverage)
- Recommended sizes: 1080x1080 (square) for Feed, 1080x1920 (9:16) for Stories

### 5.6 — Video best practices
- 15-30 seconds max
- Hook in first 3 seconds (start with action, not a logo)
- Vertical (9:16) for Stories/Reels, square (1:1) for Feed
- Captions/text overlay (most people watch with sound off)
- End with CTA

---

## Phase 6: Lead Form Setup (Instant Forms)

**Applies to:** `local-service`, `trades-home`, `professional-b2b`, `health-medical` — any archetype using Leads objective.

### 6.1 — Create the form
1. In the ad creation screen, under "Lead method", select **Instant form**
2. Click **Create form**

### 6.2 — Form type

| Option | When to use |
|--------|-------------|
| **More volume** | Starting out — pre-fills info from Facebook profile, more submissions, slightly lower quality |
| **Higher intent** | After 2+ weeks — adds a review step before submit, fewer but better-qualified leads |

**Start with "More volume"**, switch to "Higher intent" if lead quality is poor.

### 6.3 — Form fields

**Standard fields (auto-filled from Facebook profile):**
- Full name
- Phone number
- Email

**Custom questions (1-2 max — more = fewer completions):**

| Archetype | Custom Q1 | Custom Q2 (optional) |
|-----------|-----------|---------------------|
| `local-service` (bore drilling) | "Where is your property located?" (short answer) | "What do you need the bore for?" (multiple choice: Stock water / Domestic / Irrigation / Other) |
| `local-service` (plumber) | "What do you need help with?" (multiple choice) | "Is this urgent?" (Yes/No) |
| `trades-home` | "What work do you need done?" (short answer) | "When are you looking to start?" (multiple choice) |
| `professional-b2b` | "What does your business do?" (short answer) | "What's your biggest challenge right now?" (short answer) |
| `health-medical` | "What service are you interested in?" (multiple choice) | "Are you a new or existing patient?" |

### 6.4 — Privacy policy
- Link to client's privacy policy page
- If none exists: link to homepage (Meta requires a URL)

### 6.5 — Thank you screen
- **Headline:** "Thanks for your enquiry!"
- **Description:** "We'll be in touch within 24 hours. For urgent enquiries, call us on [PHONE]."
- **Button:** "Call Now" → tel:+61[number]

### 6.6 — Lead notifications
- After publishing, go to: Events Manager → Lead Form → Notifications
- Add your email AND the client's email
- Leads must be followed up within 1 hour if possible (speed to lead = #1 conversion factor)

---

## Phase 6.5: Lead Delivery & CRM Automation

**After the form is live, leads need to flow somewhere.** Don't rely on checking Ads Manager manually.

### 6.5.1 — Lead delivery options (pick one or combine)

| Method | Complexity | Latency | Best for |
|--------|-----------|---------|----------|
| **Meta → Google Sheets (built-in)** | Easy | Real-time | Quick setup, small teams |
| **Facebook Lead Ads API (n8n trigger)** | Hard | Real-time | Full automation, CRM sync |
| **Meta Sheets + n8n polling** | Medium | 1-2 min | When API is blocked (recommended workaround) |
| **Zapier / Make** | Easy | Near real-time | If client already pays for these tools |

### 6.5.2 — Recommended setup: Meta Sheets + n8n polling

This is the most reliable approach. Facebook Lead Ads API requires the Facebook Page to be in the same Meta Business portfolio as the app — if it isn't (common when page ownership is messy), the API returns 403/400.

**Step 1: Meta → Google Sheets (built-in)**
1. In Meta Business Suite → Integrations → or campaign setup → Lead delivery
2. Connect Google Sheets → select/create a sheet
3. Meta writes raw leads here automatically (one row per submission)

**Step 2: n8n polls that sheet**
1. Add a Google Sheets Trigger node (polls every minute for new rows)
2. Connect to a Code node that normalises the data:
   - Map Meta form fields to CRM column names
   - Strip Meta prefixes: phone `p:` prefix, postcode `z:` prefix
   - Convert `+61` phone to `0` prefix (Australian format)
   - Convert postcodes to suburb names via lookup table
   - Map form answers to CRM work types
   - Generate a unique lead ID (e.g. `META-[timestamp]-[random]`)
   - Filter out test leads (contain "dummy data" in fields)
3. Append normalised row to CRM Google Sheet
4. Send email notification to team

**Step 3: Google Sheets formatting for phone numbers**
- Format the Phone column as **Plain Text** (via Sheets API or Format → Number → Plain text)
- Without this, Google Sheets strips leading zeros (0439... → 439...)
- Also prefix phone values with apostrophe in Code node: `phone = "'" + phone`

### 6.5.3 — Postcode → suburb conversion

Meta instant forms capture postcode, not suburb. Build a lookup table in the n8n Code node:

```javascript
const postcodeMap = {
  '4350': 'Toowoomba', '4352': 'Highfields', '4355': 'Oakey',
  '4357': 'Dalby', '4358': 'Pittsworth', '4361': 'Warwick',
  '4401': 'Aubigny', '4400': 'Chinchilla',
  // Add postcodes for client's service area
};
let postcode = (raw['post_code'] || '').replace(/^z:/, '').trim();
const suburb = postcodeMap[postcode] || postcode;
```

Expand the lookup table for the client's service area. If postcode isn't in the map, display the raw postcode.

### 6.5.4 — Combined workflow (website + Meta in one)

Build ONE n8n workflow with two triggers feeding shared nodes:

```
Website Webhook ──→ Normalise Website Lead ──┬──→ Append to CRM ──→ (done)
                                             │
                                             ├──→ Email Team ──→ (done)
                                             │
Meta Sheet Trigger ──→ Normalise Meta Lead ──┘
```

Both normalise nodes output identical field names so the Append and Email nodes work for either source. The Email node should reference the upstream Normalise node explicitly: `$('Normalise Website Lead').item.json.name` (not `$json.name` which may reference the wrong upstream node).

### 6.5.5 — Facebook Lead Ads API (if page ownership allows)

If the Facebook Page IS in the same Meta Business portfolio as your app:

1. Create a Meta Developer App (developers.facebook.com)
2. Add "Facebook Login for Business" product
3. Configure OAuth redirect: `https://oauth.n8n.cloud/oauth2/callback` (for n8n cloud)
4. Add `oauth.n8n.cloud` to App Domains + Website platform
5. Enable `pages_read_engagement` and `leads_retrieval` permissions
6. In n8n: add Facebook Lead Ads Trigger node → connect via OAuth
7. Select Page → Select Form → wire to normalise/CRM/email

> **Gotcha:** If the Facebook Page is NOT in your business portfolio (e.g. owned by client's restricted portfolio), the API returns `400 (#100) Object does not exist`. You cannot bypass this — use the Google Sheets polling workaround instead.

> **Gotcha:** n8n cloud's OAuth redirect URL is `https://oauth.n8n.cloud/oauth2/callback` — NOT `https://yourinstance.app.n8n.cloud/rest/oauth2-credential/callback`. The Meta App needs this exact URL in Facebook Login for Business → Valid OAuth Redirect URIs.

---

## Phase 7: Budget & Scheduling

### 7.1 — Budget

Set at campaign level (CBO distributes across ad sets):

| Weekly Meta budget | Daily budget | Notes |
|-------------------|-------------|-------|
| $70/week | $10/day | Minimum viable — 1 ad set only |
| $105/week | $15/day | Okay — 2 ad sets, limited data |
| $140/week | $20/day | Good — 2 ad sets, enough to learn |
| $210/week | $30/day | Strong — 2-3 ad sets, faster learning |

### 7.2 — Scheduling
- **Start date:** Immediately (or specific date)
- **End date:** Leave open (ongoing)
- **Time schedule:** Run 24/7 — Meta's algorithm optimises delivery timing
  - Exception: very tight budgets (<$10/day) → limit to 5am-9pm local time

### 7.3 — Spending limit (safety net)
- Ad Account Settings → Payment Settings → Account Spending Limit
- Set to: monthly budget + 30% buffer
- Example: $140/week × 4.3 weeks = ~$600/month → set limit to $800

---

## Phase 8: Pre-Launch Checklist

Before clicking Publish, verify EVERY item:

- [ ] Correct Facebook Page selected at Ad level
- [ ] Correct Instagram account selected (if running on Instagram)
- [ ] Correct pixel/dataset selected — **verify name AND ID**
- [ ] Location targeting is correct (radius, not entire country)
- [ ] Age range is set (not default 18-65+, unless intentional)
- [ ] Budget is correct
- [ ] At least 2 ad variations exist
- [ ] Ad copy proofread — Australian English, no jargon, phone number correct
- [ ] Images/videos display correctly on all placements (preview each)
- [ ] Lead form works (preview and submit test)
- [ ] Privacy policy link works
- [ ] CTA button is appropriate
- [ ] No Special Ad Category flags missed
- [ ] Account spending limit set

---

## Phase 9: Launch & Initial Monitoring

### 9.1 — Publish
1. Click **Publish**
2. Ads enter **Review** — Meta checks policy compliance (15 min to a few hours)
3. Status changes to **Active** once approved
4. If rejected: read the rejection reason carefully, fix, and resubmit

### 9.2 — First 48 hours
- **Don't touch anything.** Let Meta's algorithm learn.
- Check once per day: are ads delivering? Any rejections?
- Don't panic if CPL is high on Day 1 — takes 3-5 days to stabilise

### 9.3 — Day 3-5 check
- Are impressions delivering evenly across ad sets?
- Which ad creative has better CTR?
- Are leads coming through? Check **Lead Center** in Meta Business Suite
- Download leads: Ads Manager → campaign → Results → Download Leads

### 9.4 — Respond to leads FAST
- Contact every lead within 1 hour (same business day minimum)
- Speed to lead is the #1 factor in lead-to-customer conversion
- Set up instant email notifications (Phase 6.6)

---

## Phase 10: Weekly Optimisation

### 10.1 — Key metrics to check

Open Ads Manager. Date range: Last 7 days.

| Metric | Good | Warning | Action |
|--------|------|---------|--------|
| **CPL (Cost Per Lead)** | < $30 | > $50 | Pause high-CPL ad sets, test new creative |
| **CTR (Click-Through Rate)** | > 1.5% | < 0.8% | Refresh creative — ad fatigue |
| **Frequency** | < 3 | > 5 | Audience seeing ads too often — broaden or refresh |
| **Impressions** | Steady/growing | Dropping | Check audience size, increase budget or broaden |
| **Lead form completion rate** | > 30% | < 15% | Simplify form — too many fields |
| **Spend** | On budget | Over/under | Adjust daily budget |

### 10.2 — Optimisation decisions

**CPL too high (> $40):**
1. Pause the underperforming ad set
2. Replace the lowest-CTR ad creative
3. Try broadening audience (wider radius or fewer interest restrictions)
4. Try a new hook in ad copy

**CPL good but lead quality poor:**
1. Switch form from "More volume" to "Higher intent"
2. Add a qualifying question
3. Narrow audience

**Ads not spending (low impressions):**
1. Check for policy rejections
2. Audience may be too small — increase radius or add interests
3. Increase budget slightly

**CTR dropping (ad fatigue):**
1. Create new creative (different image/video, new copy angle)
2. Refresh every 2-4 weeks
3. Keep best performer, swap underperformers

### 10.3 — A/B testing cadence
- **Week 1-2:** Run initial 2 ad sets × 2 creatives. Gather data.
- **Week 3:** Kill worst performer. Double down on winner. Test one new creative.
- **Week 4:** Review full month. Best audience + creative combo = new baseline.
- **Ongoing:** Always 1 proven "control" ad + 1 "test" ad.

---

## Phase 11: Reporting

### Weekly update (WhatsApp/text to client)
> "Hey [Client] — weekly ad update: Spent $[X], got [X] leads at $[X] per lead. [X] look promising. Any feedback on lead quality?"

### Monthly report (detailed)

| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| Total spend | $ | $ | +/-% |
| Total leads | # | # | +/-% |
| Cost per lead | $ | $ | +/-% |
| Leads contacted | # | # | |
| Quotes sent | # | # | |
| Jobs won | # | # | |
| Revenue from ads | $ | $ | |
| **ROAS** | **X:1** | **X:1** | |

---

## Gotchas (Hard-Won Lessons)

1. **2FA required** — Enable 2FA on Facebook BEFORE trying to get full Meta Business portfolio admin access. Without it you get "partial access" and can't create ad accounts.

2. **Restricted portfolios taint everything** — When a Meta Business portfolio is restricted, ALL child assets (ad accounts, pixels, pages) are tainted. Appeal denial is final. Create assets under agency portfolio from the start.

3. **Wrong pixel selection** — Ads Manager can default to a pixel from a different project. Always verify pixel name AND ID before publishing.

4. **Page ownership ≠ page access** — Personal full control of a Page doesn't let you move it between portfolios. Ownership is at portfolio level.

5. **Timezone/currency locked** — Ad account timezone and currency are set at creation and cannot be changed. Always double-check.

6. **Meta Business Suite navigation is inconsistent** — Direct URLs often redirect to wrong settings. Navigate manually: business.facebook.com → select portfolio → gear icon → desired section.

7. **Lovable/SPA sites need _redirects** — Netlify returns 404 on SPA routes (like /thank-you) unless you add `/*  /index.html  200` in a _redirects file. This breaks pixel event tracking if the thank-you page 404s.

8. **Don't optimise too early** — Meta's algorithm needs 3-5 days and ~50 events to exit the "learning phase". Don't pause/change ads in the first 48 hours.

9. **Lead form "More volume" vs "Higher intent"** — Start with More volume (pre-fills, more submissions). Switch to Higher intent (adds review step) only if lead quality is poor.

10. **Speed to lead** — The #1 factor in converting a Meta lead to a customer is response time. Set up instant email notifications and call within 1 hour.

11. **Pixel not connected to ad account** — Creating a Meta Pixel does NOT auto-connect it to your ad account. Must manually link via Events Manager → Settings → Data Sources → Connected assets → Add ad account. Must reload Ads Manager tab after (caches dropdown).

12. **n8n webhook modes** — `/webhook-test/` only works when n8n editor is listening. `/webhook/` is the production URL — only works when the workflow is ACTIVATED (toggled ON). If website form stops working after URL change, check workflow is active.

13. **Google Sheets strips leading zeros** — Phone numbers like 0439... become 439... when written with USER_ENTERED mode. Fix: format column as Plain Text AND prefix phone values with apostrophe in Code node.

14. **Meta instant form field prefixes** — Meta prefixes phone numbers with `p:` and postcodes with `z:` in their Google Sheets integration. Always strip these in normalisation code.

15. **Facebook Lead Ads API requires page in portfolio** — The `pages_read_engagement` permission only works for pages within the app's Meta Business portfolio. If page is under a different/restricted portfolio, use Google Sheets polling workaround instead.

16. **Advantage+ audience minimum age caps at 25** — You can only set minimum age (not a range), and the max you can set is 25. For tighter age targeting, use "Original audience options" instead of Advantage+.

17. **Lead Center requires page in portfolio** — Meta Business Suite Lead Center only shows pages that are in the current business portfolio. If your page is personal-only or under a different portfolio, you get "No Facebook Pages or Instagram accounts". Use Google Sheets notifications as workaround.

---

## Glossary

| Term | What It Means |
|------|--------------|
| **Ad Account** | The billing entity that holds campaigns, ad sets, and ads. Linked to one payment method. |
| **Ad Set** | A group of ads sharing the same targeting, budget, schedule, and placement settings. |
| **Advantage+** | Meta's AI-powered placements/targeting — lets the algorithm decide where and to whom ads show. |
| **Business Portfolio** | (Formerly Business Manager) The top-level container that owns pages, ad accounts, pixels, and people. |
| **Campaign** | The top level of Meta's ad structure. Sets the objective (Leads, Sales, Traffic, etc). |
| **CBO** | Campaign Budget Optimisation — Meta distributes daily budget across ad sets based on performance. |
| **Conversion API (CAPI)** | Server-side event tracking that supplements the pixel. More reliable than browser-only tracking. |
| **CPC** | Cost Per Click — how much each ad click costs you. |
| **CPL** | Cost Per Lead — how much each lead (form submission) costs you. |
| **CPM** | Cost Per Mille — cost per 1,000 impressions (how much to show your ad 1,000 times). |
| **CTR** | Click-Through Rate — % of people who saw the ad and clicked it. |
| **Dataset** | Meta's newer term for a pixel + server events combined. You may see "Dataset" instead of "Pixel" in newer UI. |
| **Events Manager** | Where you create and manage pixels, conversion events, and server-side tracking. |
| **Frequency** | Average number of times each person has seen your ad. Above 5 = fatigue risk. |
| **Instant Form** | A lead form that opens inside Facebook/Instagram — user doesn't leave the app. Higher completion rate. |
| **Lead Center** | In Meta Business Suite — shows incoming leads in real-time. Can reply directly. |
| **Learning Phase** | First ~50 conversion events after a campaign launches. Meta is testing delivery. Performance is unstable — don't make changes. |
| **Lookalike Audience** | An audience of people similar to a source audience (e.g. your existing customers). Needs 100+ people in source. |
| **Meta Pixel** | JavaScript code on your website that tracks visitor actions (page views, form submissions, purchases). |
| **Meta Pixel Helper** | Chrome extension that shows whether the pixel is firing correctly on a page. Essential for debugging. |
| **Placements** | Where your ad appears — Facebook Feed, Instagram Feed, Stories, Reels, Messenger, Audience Network, etc. |
| **Reach** | Number of unique people who saw your ad (vs impressions which count repeat views). |
| **Retargeting** | Showing ads to people who already visited your website or engaged with your page/ads. |
| **ROAS** | Return On Ad Spend — revenue generated divided by ad spend. 5:1 = $5 revenue per $1 spent. |
| **Special Ad Category** | Required flag for ads about housing, employment, credit, or social/political issues. Restricts targeting options. |

---

## Files This Skill Produces

When run via `/create-plan` or `/implement`, this skill may generate:
- Campaign setup checklist (client-specific)
- Ad copy document (primary text, headlines, descriptions per persona)
- Audience targeting document
- Lead form configuration
- Weekly/monthly performance report template

## Related Files
- **Parent skill:** `.claude/skills/paid-ads.md` — Discovery questions (Q1–Q5) + budget split logic. Run this first.
- **Google Ads skill:** `.claude/skills/google-ads.md` — Google Ads campaign setup (companion skill)
