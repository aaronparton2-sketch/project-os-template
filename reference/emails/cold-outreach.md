# Cold Outreach Emails

For reaching out to businesses that could benefit from a better web presence. Keep it short, specific, and value-first.

---

## Template 1: "I noticed your website" (for businesses with an outdated/bad site)

**Subject:** Quick thought about [Business Name]'s website

**Body:**

Hi [Name],

I came across [Business Name] and I can see you're doing great work — [specific compliment: "your Google reviews are excellent", "I can tell you're busy based on your social media", etc.].

I noticed your website might not be doing you justice though. [Specific issue: "it's not loading on mobile", "the contact form doesn't seem to work", "it's hard to find your phone number", etc.]

I build fast, modern websites for small businesses — typically have them live within a week. I'd be happy to show you what a refreshed version could look like, no obligation.

Would you be open to a quick 15-minute chat this week?

Cheers,
Aaron
Mycelium AI
[phone]

---

## Template 2: "No website at all" (for businesses with only social media)

**Subject:** Getting [Business Name] found online

**Body:**

Hi [Name],

I found [Business Name] through [Facebook/Instagram/Google Maps] — looks like you're doing solid work. [Specific detail showing you've actually looked at their business.]

I noticed you don't have a website yet. That's not unusual — heaps of good businesses run off social media. But the businesses I work with typically see 2-3x more enquiries once they've got a proper site showing up in Google.

I build simple, professional websites for trades and service businesses. Most are live within a week and come with a contact form that sends leads straight to your phone.

Happy to show you an example — no pressure, just a quick chat.

Cheers,
Aaron
Mycelium AI
[phone]

---

## Template 3: "Warm intro via referral"

**Subject:** [Referrer Name] suggested I reach out

**Body:**

Hi [Name],

[Referrer Name] mentioned you might be looking at getting a website sorted for [Business Name] — they thought I might be able to help.

I recently built [Referrer's business name]'s website and they've been happy with the results. I do the same thing for [type of business] — fast, professional sites with a contact form that emails you directly when someone enquires.

Would you be up for a quick 15-minute chat? I can show you what I've done for [Referrer] and talk through what would work for you.

Cheers,
Aaron
Mycelium AI
[phone]

---

---

## Template 4: "Free website — AI personalised" (for automated pipeline)

Used by the lead gen pipeline. AI generates a version of this for each lead using their actual Google reviews, suburb, competitor data.

**Subject:** Free website for [Business Name]

**Body:**

Hi [Name],

Found your business on Google — [Business Name] in [suburb] has some great reviews. [Quote from their actual Google review, e.g. "One customer said 'Dave turned up on time and fixed the issue in 20 minutes — absolute legend.'"]. That kind of feedback sells itself.

I noticed you don't have a website yet, and [X] of the [Y] [category]s in [suburb] do. That means when someone Googles "[category] [suburb]", they're finding your competitors instead of you — even though your reviews are better.

I build free websites for local tradies — no strings, no catch. I've already got an idea of what yours could look like.

Would you be open to a quick 10-minute chat?

Cheers,
Aaron
Mycelium AI
[phone]

**Variables the AI fills in:**
- `[Name]` — business owner name (from Google Maps or "there" if unknown)
- `[Business Name]` — from scrape
- `[suburb]` — from scrape
- `[Google review quote]` — pulled from their actual reviews
- `[X] of [Y]` — competitor count with websites vs total in suburb+category
- `[category]` — plumber, electrician, etc.

---

## Template 5: "New business — ABR lead" (for newly registered businesses)

**Subject:** Congrats on starting [Business Name]

**Body:**

Hi [Name],

Saw that [Business Name] just got started — congrats on taking the leap.

Most new businesses I work with want a website but don't want to spend thousands getting one built. So I build them for free — a professional site with a contact form that emails you when someone enquires. No catch, no lock-in. You keep the code.

If you're interested, I can have something ready for you within a week. Happy to jump on a quick call and show you an example.

Cheers,
Aaron
Mycelium AI
[phone]

---

## A/B Testing Plan

Track which template variant gets the highest response rate. Rotate templates across leads and log the variant in Supabase.

| Variant | Test Variable | Hypothesis |
|---------|--------------|------------|
| **A (current)** | Standard template — compliment + no website + offer | Baseline |
| **B** | Competitor angle — "[X] competitors have websites, you don't" | Creates urgency via competition |
| **C** | Review quote — lead with their actual Google review | Personal, proves you looked at their business |
| **D** | New business — congratulations angle (ABR leads) | Warm tone, timing advantage |
| **E** | Ultra-short — 3 sentences max | Tests if shorter = more responses |

**How to track:** Each email sent by the pipeline logs `email_variant` in Supabase. After 2 weeks, query: `SELECT email_variant, COUNT(*) as sent, COUNT(responded_at) as responses FROM leads GROUP BY email_variant` — compare response rates.

---

## Notes for Aaron

- **Subject line:** Keep it specific to THEM, not about you
- **First line:** Prove you've actually looked at their business — generic = delete
- **Length:** Max 5-6 sentences. If it scrolls on a phone, it's too long.
- **CTA:** Always a low-commitment ask ("quick 10-min chat", "happy to show you")
- **Never:** Attach price lists, use "we" language (you're a solo operator), or use marketing buzzwords
- **Follow-up:** If no response in 3-4 days, send one follow-up (see `follow-up.md`). Auto follow-up is handled by the lead pipeline if enabled.
- **Source leads from:** Automated pipeline (Google Maps, ABR, HiPages), Facebook groups, industry directories, driving around and noting businesses with no web presence
- **A/B testing:** Log which template variant was sent per lead in Supabase. Review response rates fortnightly. Kill underperformers, double down on winners.
