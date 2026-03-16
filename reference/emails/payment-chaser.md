# Payment Chaser Emails

For failed payments or overdue invoices. Start friendly, escalate if needed.

---

## Level 1: Friendly Heads-Up (Day 1 of failed payment)

**Subject:** Quick heads-up — payment didn't go through

**Body:**

Hi [Name],

Just a quick heads-up — your monthly payment of $[amount] didn't go through on [date]. This sometimes happens if a card's expired or the bank flagged it.

I've sent a fresh payment link below — should only take a minute to sort:
[Stripe payment link]

No rush, just whenever you get a chance.

Cheers,
Aaron

---

## Level 2: Gentle Reminder (Day 7)

**Subject:** Payment reminder — [Business Name] hosting

**Body:**

Hi [Name],

Following up on the payment from last week — it's still showing as unpaid ($[amount] for [month]).

Here's the payment link again: [Stripe payment link]

If there's an issue with the card or you'd prefer a different payment method, just let me know and I'll sort it.

Cheers,
Aaron

---

## Level 3: Firm but Fair (Day 14)

**Subject:** Action needed — [Business Name] account

**Body:**

Hi [Name],

I've reached out a couple of times about the outstanding payment of $[amount] for your website hosting/maintenance. I want to keep everything running smoothly for you, so I'd appreciate if we could get this sorted.

Payment link: [Stripe payment link]

If there's something going on or you'd like to chat about it, I'm happy to work something out. Just let me know.

Cheers,
Aaron

---

## Level 4: Final Notice (Day 21)

**Subject:** Final notice — [Business Name] hosting

**Body:**

Hi [Name],

This is a final reminder regarding the overdue payment of $[amount]. I haven't heard back from my previous emails.

If payment isn't received by [date — 7 days from now], I'll need to pause hosting services for [Business Name]'s website. The site can be reactivated once payment is up to date.

Payment link: [Stripe payment link]

I'd prefer not to go down that path — if there's an issue, please reach out and we can figure something out.

Cheers,
Aaron

---

## Notes for Aaron

- **Always send a payment link** — make it as easy as possible to pay
- **SMS is often better** for Level 1 — people check texts faster than email
- **Check Stripe first** — was it a card decline, insufficient funds, or fraud flag? If fraud flag, check Stripe Radar rules (see outstanding actions)
- **Don't threaten on Level 1-2.** Most failed payments are accidental.
- **Level 4 is rare.** If you get here, consider whether this client is worth keeping.
- **After Level 4:** If still unpaid, pause the site (remove DNS or take down deployment). Keep the code — they can reactivate if they pay up.
- **Log everything** in CRM with dates
