# Ben Excalidraw — Content Summary

**Open in browser:** https://app.excalidraw.com/l/7vTbysPSW2a/5n4Fge8lOuJ

**Source:** `Ben Excalidraw.excalidraw` (527 elements, 45 embedded images, 259 text blocks)
**What it is:** "The 5 Step Vibe-Coded SaaS Blueprint" — a visual guide for building a full-stack SaaS as a complete beginner using AI coding tools. Written by someone who built a dental AI x-ray diagnostics SaaS (ScanWise).

---

## Structure Overview

```
Step 1: Find a Problem → Step 2: Build the Output → Step 3: Validate the Product
→ Step 4: Build the Frontend → Step 5: Build the MVP (connect frontend + backend)
```

---

## Step 1: Find a Problem

**Key principle:** Start with local service-based businesses. LLMs lower the barrier to entry for most industries — you don't have to be a professional, just willing to learn.

**How to find problems:**
- How do you get customers?
- How do you fulfil the service?
- What makes you want to punch your computer?
- Start with warm networks: friends, family, colleagues
- "There's always something..."

**New AI models = new problems to solve.** Pain points 1-5 might already be solved, but problem 6 with a large enough TAM is still worth money. Even crumbs can be worth an 8-9 figure valuation.

**Examples of AI unlocking new problems:**
- Voice realism + latency with ElevenLabs/GPT Realtime
- Text to image/video with Sora and similar tools

### Ben's Story
- Met a random Bulgarian dentist who shared interest in AI/automation
- "What if we trained an AI x-ray diagnostics model?"
- Got a quote from Microsoft Azure: $1.5M (slightly above budget)
- Already had the hard part: 500k+ dental x-rays (data)
- Hired a dev team, got it done in 45 days
- **Speed is KEY**

---

## Step 2: Build the Output

**Core principle:** Don't build a SaaS yet — just build the thing the SaaS produces. No UI, no dashboard, no login. Just the core output. You need fast feedback.

**Two options:**

| Option | When to Use | How |
|--------|-------------|-----|
| **No-Code (Make.com or n8n)** | Logic is simple, no heavy processing | Ask ChatGPT to generate the blueprint → download JSON → import into Make.com |
| **Vibe Code** | Too custom or logic-heavy for no-code | Build the output-only with code |

**Key rule:** If your output is useful but ugly → perfect. If it's pretty but useless → you've wasted your time.

### Ben's First Solution (ScanWise)
```
Upload X-Ray → AI detects conditions → Processes conditions, treatments, urgency → Creates & sends PDF report
```

---

## Step 3: Validate the Product

**Core principle:** Stop building in a cave and talk to professionals. Validation doesn't happen on ChatGPT. It happens in clinics, offices, shops.

### The Greg Approach (Don't Do This)
- Spends 2 weeks making a pitch deck
- "Validates" his SaaS with ChatGPT
- Wants to add 1 more feature before talking to anyone
- Takes ages to get useful feedback

### The Chad Approach (Do This)
1. Get clear on the industry pain points
2. Have substance to get feedback on
3. Spend the morning preparing, the afternoon doing
4. Cold called, cold walk-in, oozing charisma

**What Ben did:**
- Searched "dentist near me" and cold called them
- Cold called his own dentist, friend of a friend, dad's college mates
- Walked into dentists in his area, sat down with the owner, showed how the SaaS could solve their problems
- "Instantly knew where the holes were — invaluable feedback"

**Key insight:** Having an industry friend/advisor is critical. They unlock faster feedback and real conversations. Keep this person close — you'll need them later.

---

## Step 4: Build the Frontend

**What is a frontend?** The part of your app users actually see — buttons, screens, pages, forms, everything they click.

### Process
1. **Brainstorm with ChatGPT** — figure out what screens your frontend needs
2. **Paste UI prompts into Lovable** (5 free credits/day, usually enough)
3. **Download the code** (click the code button → download)
4. If Lovable gives something slightly off, tell Cursor: "Fix the spacing, alignment, colors and make it consistent"

**Ben's UI map (ScanWise):**
1. Upload X-Ray screen
2. AI Results screen
3. Report View & Send screen
4. Dashboard

---

## Step 5: Build the MVP

**You already have 2 things:**
- A frontend/UI (Step 4)
- An output/backend (Step 2)
- Time to connect them with vibe coding

### The Tech Stack

| Tool | Purpose | Analogy |
|------|---------|---------|
| **Cursor** | AI-powered coding partner. Replaces need for a full dev team. | Your co-founder |
| **GitHub** | Storage home for your code. Like Google Drive for software. | Your filing cabinet |
| **Render** | Where your app actually runs. Takes code from GitHub → turns into a live URL. | Your hosting |
| **Supabase** | Your app's memory. Stores users, data, handles login/signup. | Your database |

**Total cost: less than $100/mo. "It's insanely accessible, there's no excuses."**

### Pro Tips
1. Create a private GitHub repo on day one, connect to Cursor
2. Use dictate feature for fast prompting
3. Keep an eye out for new model promotion weeks
4. You don't need to do anything in Supabase manually — ask Cursor to generate SQL, paste it in
5. Backend logs (Render) are your best friend for troubleshooting — screenshot them, paste into Cursor

### Bug Fixing Hack
1. Use Render's API to fetch latest error logs
2. Save logs to a file in your repo (`latest_error.txt`)
3. Tell Cursor: "Whenever I run my debug script, read latest_error.txt and fix the issue"

### Getting Stuck?
Hire off Upwork or Fiverr to fix specific bugs. Don't panic.

---

## The Dunning-Kruger Effect of Vibe Coding

| Stage | What Happens | Feeling |
|-------|-------------|---------|
| **S1: Peak Confidence (Mt Stupid)** | Cursor writes one component: "I'm basically a full-stack engineer now" | Overconfident |
| **S2: Valley of Despair** | Errors, something breaks: "Maybe this SaaS thing isn't for me" | **Most people quit here** |
| **S3: Slow Climb** | Fix bugs, understand folder structure, get little wins | Growing |
| **S4: Quiet Competence** | Cursor feels like your co-founder. Pieces fall into place. | Confident for real |

**Key insight:** "Coding hasn't changed, but the experience of becoming a coder has. AI compresses the whole emotional journey into days instead of years."

---

## The "Big Bang" of Vibe Coding (AI Timeline)

| Date | Event | Significance |
|------|-------|-------------|
| March 2023 | GPT-4 | AI can write working code but still breaks constantly |
| Nov 2023 | Cursor Release | AI refactoring, file-level context, repo-wide edits |
| Early 2024 | LLM Flood | GPT-4.1, Gemini 1, Grok 1.5, DeepSeek, Llama 3 |
| March 2024 | Anthropic on the map | Claude Opus, Sonnet, Haiku — proved AI could be a real coding partner |
| July 2024 | Grok 2 | Fastest model, pushed speed + reasoning forward |
| **24 Nov 2025** | **Opus 4.5 Release ("The Big Bang")** | "First model in history capable of reliably building, refactoring, and debugging full-stack applications end-to-end for beginners. For the first time ever, you can build a production SaaS without a developer." |

---

## Key Takeaways for Mycelium AI

### What aligns with Aaron's approach:
- Start with local service businesses (Aaron already does this)
- Build fast, validate fast (Aaron's Lovable workflow)
- Cold calling/walking in (Aaron does cold outreach)
- Tech stack overlap: Supabase, Lovable, GitHub (Aaron uses all of these)

### What Aaron could adopt:
- **The "output first" approach** — before building a full product, build just the output and validate it with real users
- **The Chad validation method** — cold call/walk into businesses with a working demo (Aaron already does the demo approach but could be more aggressive with walk-ins)
- **n8n blueprint generation** — ask ChatGPT to generate n8n blueprints for automation outputs
- **Render for hosting** — worth evaluating vs Netlify/Vercel for more complex apps (supports backend services)

### What differs from Aaron's stack:
- Ben uses Cursor; Aaron uses Claude Code (arguably more capable with Opus 4.6)
- Ben uses Make.com for no-code; Aaron uses n8n (better choice — self-hostable, more flexible)
- Ben uses Render; Aaron uses Netlify/Vercel (fine for frontend, but Render better for backend services)
- Ben's SaaS focus is different from Aaron's agency/service model, but the build methodology applies to both

### Potential SaaS ideas from Ben's framework:
- Aaron could build a SaaS version of his Google Sheet CRM + n8n automation stack
- The review automation could become a standalone SaaS product
- Lead reactivation system could be productised
