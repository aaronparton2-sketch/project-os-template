# SMS Outreach Templates

Cold SMS outreach via Twilio. Same principles as email but way shorter. Every character counts.

---

## Principles

1. **Always use first name** — "Hey {name}," is mandatory. No exceptions.
2. **Self-aware** — Acknowledge you're cold-texting. "I know you get these" / "not gonna lie, this is a cold text"
3. **Irresistible offer** — Free website, no strings, yours to keep. Or mates rates $299.
4. **Australian** — Casual Aussie tone. Contractions. "Reckon", "keen", "cheers".
5. **Slightly self-deprecating** — Don't oversell. "Chances you read this are slim" energy.
6. **Trade lingo** — Use 1 trade term naturally if it fits. Don't force it.
7. **Research-based** — Reference their Facebook post, reviews, or suburb if available.
8. **STOP opt-out** — Every SMS ends with "Reply STOP to opt out" (Spam Act 2003 compliance).
9. **Max 280 chars** — Aim for 160-250. Under 160 = 1 SMS segment (cheapest). 161-306 = 2 segments.

---

## Template 1: Standard

> Hey {name}, Aaron here. I build free websites for {trade}s in {region}. No strings, yours to keep. Worth a quick chat? 0498 201 788
> Reply STOP to opt out

**~180 chars. 2 segments.**

---

## Template 2: Self-Aware

> Hey {name}, I know tradies get heaps of these msgs. But I'm local, build free websites, and yours would take me about a week. Keen? - Aaron 0498 201 788
> Reply STOP to opt out

**~200 chars. 2 segments.**

---

## Template 3: Social-Active

> Hey {name}, saw your {trade reference} in {suburb}. Reckon you could use a website to match. I'll build it free, no catch. Text back if keen - Aaron 0498 201 788
> Reply STOP to opt out

**~210 chars. 2 segments.**

---

## Template 4: Rogue (~5%)

> Hey {name}, not gonna lie, this is a cold text. But I build bloody good websites for {trade}s and yours would look mint. Free, no bs. - Aaron 0498 201 788
> Reply STOP to opt out

**~210 chars. 2 segments.**

---

## Template 5: Mates Rates

> Hey {name}, doing websites from $299 this month for {trade}s. Normally $1,500+. Filling my calendar. Keen? - Aaron 0498 201 788
> Reply STOP to opt out

**~170 chars. 2 segments.**

---

## Cost

- ~$0.08-0.10 AUD per SMS segment (outbound to Australian mobile)
- 1 segment = up to 160 chars (GSM-7 encoding)
- 2 segments = 161-306 chars
- Most of our SMS will be 2 segments (~$0.16-0.20 each)
- Daily cap: 10 SMS = ~$2/day max
- $20 credit = ~100-125 SMS

---

## Compliance (Australian Spam Act 2003)

- Every commercial SMS must include opt-out mechanism
- "Reply STOP to opt out" at end of every message
- Twilio auto-handles STOP keyword (unsubscribes the number)
- Must include sender identification (Aaron's name + number)
- Do not text numbers that have opted out (Twilio blocks these automatically)

---

## Targeting

**Current (skeleton):**
- Must have Australian mobile (04xx)
- Lead score >= 7
- SMS Toggle is ON in n8n

**Future (smart targeting):**
- Historical conversion data: which trades/regions/offer types get replies
- "SMS-worthy" score based on email engagement + lead profile
- Only text the top 10% of leads
- Can text leads already emailed (different channel, trades don't check email)

---

## Notes

- SMS is independent of email — not a follow-up delay
- Aaron reviews drafts before sending (same Pipeline Leads sheet, channel column = 'sms')
- Inbound replies hit n8n webhook, auto-classified as positive/negative/stop
- Positive replies flag lead as "engaged" in Supabase for CRM pipeline
