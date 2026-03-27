# Plan: Pattern Interrupt Email Variant (15%) + Twilio SMS Outreach Skeleton

**Created:** 2026-03-27
**Status:** Implemented
**Type:** Full
**Request:** Add a "pattern interrupt" email opener variant at 15% allocation + build a working Twilio SMS outreach skeleton in n8n with the same personalisation principles as email.

---

## Overview

### What This Accomplishes
Two upgrades to the outreach system: (1) A new email variant that leads with self-aware, "I know you get these daily" openers — tested at 15% of emails alongside existing variants, not replacing them. (2) A complete SMS outreach channel via Twilio, built as a toggleable branch in n8n that sends personalised texts to leads with phone numbers. SMS follows the same anti-AI-slop framework, trade lingo, and personalisation principles as email.

### Why This Matters
Aaron closed a client through text → call → Google Meet. The client said "I get these messages every day" — what stood out was the free offer, being local, and being a real person. Email is the volume/awareness channel; SMS is the high-conversion spear. The pattern interrupt variant tests whether acknowledging the spam reality improves open/reply rates. Together, these changes align the automated pipeline with what's actually closing deals.

---

## Current State

### Relevant Existing Structure
- **Build Email Prompt A** — Code node with trade lingo, social gating, humour A/B, offer A/B, 7 email variants
- **Variant selection** — `STANDARD_VARIANTS` array (5 variants), `SOCIAL_ACTIVE_VARIANT`, `NEW_BUSINESS_VARIANT`
- **Offer type A/B** — deterministic: free_website 80%, mates_rates 10%, portfolio_build 10%
- **Humour A/B** — deterministic ~10%
- **outreach_events** table — tracks variant, trade, humour, offer_type, personalisation_type
- **Sign-off** — "Aaron Parton | Perth, WA" (needs to be dynamic for non-Perth leads)
- **Twilio** — Aaron has $20 credit loaded, phone number purchased. No env vars in `.env` yet.
- **Parse Email A** — extracts subject, body, call_script, offer_type from OpenAI response
- **Deploy pattern** — Python scripts fetch workflow via n8n API, update node code, PUT back

### Gaps Being Addressed
1. No "pattern interrupt" opener variant — all emails start with standard approaches
2. No SMS outreach channel — proven to close but not in the automated pipeline
3. The sharpened offer wording ("let me build it, if you don't like it, it's yours anyway, all I need is to show you on a 15min call") isn't in the prompt
4. Sign-off mentions "Perth, WA" for all leads — should be dynamic based on lead region
5. No Twilio integration configured

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `scripts/deploy-pattern-interrupt.py` | Adds pattern interrupt variant to Build Email Prompt A + sharpens offer wording |
| `scripts/deploy-sms-outreach.py` | Creates SMS outreach branch in n8n (Twilio nodes, SMS prompt builder, toggle switch) |
| `scripts/lead-pipeline/sms-templates.json` | SMS template reference (like email-templates.json) |
| `reference/emails/sms-outreach.md` | SMS outreach guidelines and template reference |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `.env` | Add Twilio env vars: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` |
| `.env.example` | Add Twilio placeholder vars |
| `reference/integrations-catalog.md` | Add Twilio integration section |
| `context/WHERE-current-data.md` | Update with pattern interrupt + SMS channel |
| `context/outstanding-actions.md` | Update Twilio item from "future" to "in progress" |

### Files to Delete

None.

---

## Scope Check

- **Inside scope?** Yes — the lead gen pipeline scope includes outreach channels and A/B testing. SMS was already identified as a future channel in outstanding-actions.md.
- **Decision required:** None.

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | **Not yet in .env** — Aaron needs to add these |
| n8n API | `N8N_API_URL`, `N8N_API_KEY` | Present ✓ |
| OpenAI | `OPENAI_API_KEY` | Present ✓ |
| Supabase | `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF` | Present ✓ |

---

## Skills to Use

None.

---

## Design Decisions

### 1. Pattern Interrupt: New Variant, Not Replacement

**Decision:** Add `pattern_interrupt` as a 6th entry in `STANDARD_VARIANTS` array, selected 15% of the time. Existing variants keep running.

**Implementation:** Change the standard variant selection from pure random to weighted:
- 15% → `pattern_interrupt` (new)
- 85% → randomly chosen from existing 5 variants

This way we get clean A/B data: pattern_interrupt vs all others. The variant name `pattern_interrupt` is logged in `outreach_events.email_variant` like every other variant.

**Approved openers (Aaron's picks):**
- "Hey {name}, chances you read this are slim, but I build websites for {trade} businesses and I reckon I can help."
- "Hey {name}, I know you get 10 of these a day. But I'm a local Aussie who builds websites for {trade}s and I genuinely think I can help."

**Region-aware:** Never hardcode "Perth" — use `{region}` dynamically. The opener says "local Aussie", not "local Perth bloke".

### 2. Sharpened Offer Wording

**Decision:** Update the `free_website` offer pitch in `OFFER_TYPES` to use Aaron's proven wording:

**Old:** "Aaron builds the first site for free. Genuinely no catch..."
**New:** "Let me build it, if you don't like it, it's yours anyway. All I need is to show you on a 15-min call. No strings attached, you keep the full website."

This applies to ALL free_website offers (80% of emails), not just pattern interrupt. The proven close language should be everywhere.

### 3. Fix Sign-Off Location

**Decision:** Change "Aaron Parton | Perth, WA" to dynamically use the lead's state. Format: "Aaron Parton | {state}" (e.g., "Aaron Parton | WA", "Aaron Parton | QLD"). Falls back to "WA" if state unknown.

### 4. SMS Architecture: Separate Branch After Scorer

**Decision:** SMS is a separate branch that forks AFTER the email personaliser runs. The flow:

```
[Existing pipeline] → Score → Social Enrich → Email Personaliser → Parse Email
                                                                        │
                                                                   ┌────┴────┐
                                                                   │         │
                                                              [Email]   [SMS Filter]
                                                              (existing)    │
                                                                      [SMS Toggle]
                                                                           │
                                                                   [Build SMS Prompt]
                                                                           │
                                                                   [OpenAI API]
                                                                           │
                                                                   [Parse SMS]
                                                                           │
                                                                   [Send via Twilio]
                                                                           │
                                                                   [Log to Supabase]
```

**Why fork after email personaliser?** The lead already has all enrichment data, score, trade lingo, social data. The SMS just needs a different (shorter) prompt. The lead still gets an email AND a text (different channels, different timing).

### 5. SMS Toggle: Simple On/Off

**Decision:** A single boolean flag in the n8n workflow controls whether SMS sends. Implementation: an IF node called "SMS Toggle" that checks a static value (or workflow variable). When off, the branch stops. When on, leads flow through.

**Aaron flips it in n8n UI** — no code change needed. Just double-click the IF node and change the value.

### 6. SMS Filter: Who Gets Texted

**Decision (skeleton):** For now, SMS goes to ALL leads that have a phone number AND score >= 7. Smart targeting (based on historical data) comes later.

Filter criteria:
- `phone` exists and is valid Australian mobile (starts with 04)
- `score >= 7`
- Not already texted in the last 30 days (dedup)
- SMS toggle is ON

**Future upgrade (not this plan):** Replace the score threshold with a machine-learned "SMS-worthy" score based on historical conversion data.

### 7. SMS Timing: Delayed, Not Simultaneous

**Decision:** SMS sends 3-5 days AFTER the email. Not at the same time. This gives the email a chance to work first, and the SMS feels like a natural follow-up rather than a spam blast.

**Implementation:** The SMS branch uses a "Wait" node (3-5 day delay, randomised per lead) before sending. This means SMS runs as a delayed follow-up, not a parallel channel.

**Why:** Aaron's close came from texting, then calling. The email warms them up ("oh I got an email from this guy"), then the text is the personal touch that gets the reply.

### 8. SMS Prompt: Same Framework, Way Shorter

**Decision:** SMS messages are max 160 characters ideally (1 SMS segment = cheapest), hard cap at 320 characters (2 segments). Follow the same principles:
- Always use first name
- Self-aware ("I know you get these")
- Irresistible offer
- Australian/casual tone
- Slightly self-deprecating
- Occasional cussing (~5% — the "rogue" variant)
- Research-based personalisation (trade lingo, social reference if applicable)

**SMS template direction:**
- "Hey {name}, Aaron here. I build free websites for {trade}s in {region}. No strings, yours to keep. Worth a quick chat? 0498 201 788"
- "Hey {name}, I know tradies get heaps of these msgs. But I'm local, I build free websites, and yours would take me about a week. Keen? - Aaron"
- "Hey {name}, saw your {trade} work on Facebook. Reckon you could use a website. I'll build it for free, no catch. Text back if keen - Aaron"
- Rogue (~5%): "Hey {name}, not gonna lie, this is a cold text. But I build bloody good websites for {trade}s and yours would look mint. Free, no bs. - Aaron"

**Personalisation via OpenAI:** Same as email — OpenAI generates the SMS text using lead context, trade lingo, social data. Shorter prompt, same quality.

### 9. SMS Cost Control

**Decision:** Hard daily cap of 10 SMS per day. At ~$0.08 AUD per SMS segment, that's ~$0.80/day or ~$24/month worst case. Well within $20 credit for initial testing.

Cap is enforced in the SMS Filter node: count today's SMS sends in Supabase, if >= 10, skip.

### 10. Supabase Schema: Reuse outreach_events

**Decision:** Log SMS sends in the same `outreach_events` table with `channel = 'sms'`. Add a `channel` column (default 'email' for backwards compat). SMS responses tracked same way as email.

New column: `outreach_events.channel` — TEXT, default 'email', values: 'email', 'sms'
New column: `outreach_events.sms_body` — TEXT, nullable (the actual SMS sent)

### Alternatives Considered

1. **SMS as a completely separate workflow** — Rejected. Aaron prefers one consolidated workflow. SMS is just another branch.
2. **SMS immediately (same time as email)** — Rejected. Feels spammy. 3-5 day delay is more natural and gives email a chance to work first.
3. **Manual SMS list (no automation)** — Rejected. The whole point is automation. Aaron can always manually text from the daily digest too.
4. **Use n8n's built-in Twilio node** — Preferred. n8n has a native Twilio node. Simpler than HTTP Request to Twilio API.

### Open Questions

1. **Twilio env vars** — Aaron: do you have your Twilio Account SID, Auth Token, and phone number ready to add to `.env`? Need these before implementation.
2. **SMS timing** — 3-5 day delay after email feel right? Or would you prefer shorter (1-2 days) or longer (5-7 days)?
3. **Daily SMS cap** — 10/day to start? That's ~$24/month at worst. Can adjust up/down.
4. **SMS opt-out** — Australian spam laws (Spam Act 2003) require opt-out for commercial SMS. We should include "Reply STOP to opt out" at the end. Twilio can handle STOP keyword auto-replies. Confirm this is fine?

---

## Step-by-Step Tasks

### Step 1: Add Twilio to .env and integrations catalog

**Actions:**
- Aaron adds `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` to `.env`
- Add placeholders to `.env.example`
- Add Twilio integration section to `reference/integrations-catalog.md`
- Add n8n Twilio credential (Account SID + Auth Token)

**Files affected:**
- `.env` (Aaron manual)
- `.env.example`
- `reference/integrations-catalog.md`

---

### Step 2: Supabase schema — add channel column + sms_body

**Actions:**
- Run SQL migration: `ALTER TABLE outreach_events ADD COLUMN channel TEXT DEFAULT 'email';`
- Add CHECK: `channel IN ('email', 'sms')`
- Add `sms_body TEXT` column (nullable)
- Update analytics views to filter/group by channel
- Add `sms_performance` view

**Files affected:**
- Supabase pipeline DB (SQL via MCP)

---

### Step 3: Deploy pattern interrupt variant to Build Email Prompt A

**Actions:**
- Add `pattern_interrupt` variant to `STANDARD_VARIANTS` with instruction:
  - Two approved openers (randomly picked): "chances you read this are slim" / "I know you get 10 of these a day"
  - Always uses lead's first name
  - Region-aware (never hardcodes Perth)
  - Uses whichever offer type is selected (free_website/mates_rates/portfolio_build)
- Change standard variant selection to weighted: 15% pattern_interrupt, 85% random from other 5
- Update `free_website` offer pitch to proven wording: "Let me build it, if you don't like it, it's yours anyway. All I need is to show you on a 15-min call."
- Fix sign-off: "Aaron Parton | Perth, WA" → "Aaron Parton | {state}" (dynamic)

**Files affected:**
- `scripts/deploy-pattern-interrupt.py` (new)
- n8n Build Email Prompt A Code node

---

### Step 4: Build SMS outreach nodes in n8n

**Actions:**
- Create **SMS Filter** node (Code):
  - Checks: has phone (04xx), score >= 7, not texted in 30 days, daily cap not hit (10/day)
  - Queries Supabase for today's SMS count and recent SMS to this phone
- Create **SMS Toggle** node (IF):
  - Simple boolean check. Default: ON for testing, Aaron flips to OFF when done.
- Create **Wait** node:
  - 3-5 day random delay (configurable)
  - Positioned before SMS send so texts go out days after email
- Create **Build SMS Prompt** node (Code):
  - Uses same lead data (trade lingo, social data, offer type, region)
  - Builds a shorter OpenAI prompt optimised for 160-320 char SMS
  - Same anti-AI-slop rules, same banned phrases
  - ~5% rogue variant (occasional mild cussing)
  - Always includes first name, always self-aware tone
  - Includes "Reply STOP to opt out" in every message
- Create **SMS OpenAI** node (HTTP Request):
  - Calls OpenAI with SMS prompt
  - Model: gpt-4o-mini (same as email)
- Create **Parse SMS** node (Code):
  - Extracts SMS text from OpenAI response
  - Validates length (warn if >320 chars, truncate if >480)
  - Post-processes: strip em dashes, banned phrases
- Create **Send SMS** node (Twilio):
  - Uses n8n native Twilio node
  - From: `TWILIO_PHONE_NUMBER`
  - To: lead's phone (formatted E.164: +61...)
  - Body: parsed SMS text
- Create **Log SMS** node (Supabase):
  - Insert to outreach_events with channel='sms', sms_body, variant, trade, offer_type

**Files affected:**
- `scripts/deploy-sms-outreach.py` (new)
- n8n workflow (8 new nodes)

---

### Step 5: Wire SMS branch into existing workflow

**Actions:**
- Connect Parse Email A output → SMS Filter input (fork after email parsing)
- SMS Filter → SMS Toggle → Wait → Build SMS Prompt → SMS OpenAI → Parse SMS → Send SMS → Log SMS
- Add sticky note: "SMS OUTREACH (toggle on/off via SMS Toggle node)"

**Files affected:**
- n8n workflow (connections)

---

### Step 6: Create SMS template reference doc

**Actions:**
- Create `reference/emails/sms-outreach.md` with:
  - SMS principles (same as email but shorter)
  - Template examples (standard, social-active, rogue)
  - Character limits and cost info
  - Opt-out compliance notes
- Create `scripts/lead-pipeline/sms-templates.json` as structured reference

**Files affected:**
- `reference/emails/sms-outreach.md` (new)
- `scripts/lead-pipeline/sms-templates.json` (new)

---

### Step 7: Update context files

**Actions:**
- Update `context/WHERE-current-data.md` with pattern interrupt variant + SMS channel
- Update `context/outstanding-actions.md` — move Twilio from "future" to "built"
- Update `.env.example` with Twilio placeholders

**Files affected:**
- `context/WHERE-current-data.md`
- `context/outstanding-actions.md`
- `.env.example`

---

### Step 8: Test

**Actions:**
- Run Manual Trigger in n8n
- Verify pattern interrupt variant appears in ~15% of emails (check 20 sample outputs)
- Verify sharpened offer wording appears in free_website emails
- Verify sign-off uses dynamic state (not hardcoded "Perth, WA")
- Test SMS branch: verify filter, toggle, prompt, Twilio send (use Aaron's own number first)
- Check SMS logged in outreach_events with channel='sms'
- Verify daily cap enforcement (send 10, then check 11th is blocked)

**Files affected:**
- n8n workflow (Manual Trigger)

---

## Validation Checklist

- [ ] Pattern interrupt variant fires for ~15% of standard (non-ABR, non-social-active) emails
- [ ] Pattern interrupt openers use first name + don't hardcode Perth
- [ ] Sharpened offer wording appears in free_website pitch
- [ ] Sign-off shows dynamic state, not "Perth, WA"
- [ ] Twilio env vars in .env and working
- [ ] SMS Filter correctly gates on: has mobile, score >= 7, not texted in 30 days, daily cap
- [ ] SMS Toggle can be flipped on/off in n8n UI
- [ ] SMS messages are 160-320 characters
- [ ] SMS includes "Reply STOP to opt out"
- [ ] SMS uses first name, trade lingo, self-aware tone
- [ ] SMS logged in outreach_events with channel='sms'
- [ ] Rogue SMS variant fires ~5% of the time
- [ ] Daily SMS cap enforced at 10
- [ ] Wait node delays SMS 3-5 days after email
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. **Pattern interrupt variant generates measurable data** — after 1 week, can compare pattern_interrupt reply rate vs other variants
2. **SMS sends successfully via Twilio** — test SMS received on Aaron's phone with correct personalisation
3. **SMS cost controlled** — 10/day cap means max ~$24/month, well within $20 credit for testing
4. **Toggle works** — Aaron can flip SMS on/off in n8n without touching code
5. **Both channels log to same analytics** — outreach_events shows email + SMS data, views work for both

---

## Notes

- **Australian Spam Act compliance** — Commercial SMS must include opt-out mechanism and sender identification. "Reply STOP to opt out" + Aaron's name covers this. Twilio handles STOP keyword auto-unsubscribe.
- **SMS timing is key** — The 3-5 day delay after email is deliberate. It creates the "oh I got an email from this guy too" effect. If we sent both at once, it'd feel like a spam blast.
- **Future: smart targeting** — Once we have 2+ weeks of SMS data, build a "SMS-worthy" score using historical conversion rates by trade, region, score, source, offer type. Only text leads above the threshold. This is NOT in this plan — just the skeleton.
- **Future: reply handling** — Twilio can forward SMS replies to a webhook. When a lead replies, n8n could update their status in Supabase and notify Aaron. Park for a future plan.
- **Pattern interrupt is the riskiest email variant** — self-aware openers could backfire if they sound too clever. Monitor unsubscribe/stop rates closely in the first week. If stop rate is 2x+ other variants, kill it.
- **Phone number formatting** — Australian mobiles: 04XX XXX XXX locally, +614XX XXX XXX in E.164. Twilio needs E.164 format. The SMS Filter node handles conversion.

---

## Implementation Notes

**Implemented:** 2026-03-27

### Summary
- Pattern interrupt variant deployed to Build Email Prompt A (15% weighted selection, 2 approved openers)
- free_website offer pitch sharpened to proven close language across all emails
- Sign-off changed from hardcoded "Perth, WA" to dynamic `${lead.state || "WA"}`
- Supabase migration: `channel`, `sms_body`, `sms_sent_at` on outreach_events; `sms_status`, `sms_sent_at`, `sms_reply`, `sms_reply_at` on leads
- 3 new Supabase views: `sms_performance`, `sms_trade_performance`, updated `weekly_outreach_summary`
- 13 new n8n nodes (8 outbound SMS chain + 4 inbound reply handler + sticky note). Workflow: 63 -> 76 nodes.
- SMS uses Twilio HTTP API (form-encoded POST with Basic Auth)
- Inbound SMS webhook handler classifies replies as positive/negative/stop, updates leads table
- Two deployment scripts: `deploy-pattern-interrupt.py` and `deploy-sms-outreach.py`

### Deviations from Plan
- SMS is standalone (not 3-5 day delayed follow-up) — Aaron wants to test immediately, not wait for email
- Draft review mode — Aaron reviews SMS drafts before live sending (not auto-send from day 1)
- Added inbound SMS reply handler (not in original plan) — webhook already existed in Twilio config
- Daily cap (10 SMS) not enforced in filter yet — will add Supabase count check when going live
- Used Twilio HTTP API instead of n8n native Twilio node (more control over auth + form encoding)

### Issues Encountered
- Supabase MCP server pointed to original project, not pipeline project. Used curl-based deployment approach (same as all other deploy scripts) instead of MCP.
