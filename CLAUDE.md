# CLAUDE.md

Core context for Claude Code. Loaded automatically every session. Keep it accurate — it is the single source of truth for how Claude operates in this workspace.

---

## What This Is

A **Project OS** — a structured, repeatable workspace for running AI business projects with Claude Code as an agent assistant. Built for Mycelium AI but designed to be the default starting point for every new project.

---

## First-Time Setup (after cloning from template)

**IMPORTANT — do this before anything else:**

1. **Copy your `.env` file** into this project root. The template does not include `.env` (secrets are gitignored). Copy it from an existing project or from your secure backup:
   ```
   cp /path/to/your/master/.env .env
   ```
2. **Verify integrations:** Run `/prime` — it will check which env vars are present and flag any missing ones.
3. **Update `context/` files** for this project: `business-info.md` (if project-specific), `strategy.md`, `WHAT-scope-of-work.md`.
4. **Update this section** of CLAUDE.md — once setup is done, you can remove or collapse this checklist.

---

## The Claude-User Relationship

- **User (Aaron):** Defines goals, directs work, provides decisions
- **Claude:** Reads context, acts as business strategist + dev co-pilot, executes commands, maintains workspace consistency

**Default behavior:** Chat-first. Do not create new files unless:
- Required by a command (`/create-plan`, `/implement`), OR
- Explicitly requested by the user

---

## Workspace Structure

```
.
├── CLAUDE.md                    # This file — always loaded
├── PROJECT-MAP.md               # Workspace map + core workflow rules
├── learnings-register.md        # Append-only log: mistakes, pivots, insights
├── .env                         # Local secrets (gitignored)
├── .env.example                 # Placeholder var names only (tracked)
├── .mcp.json                    # MCP server config (Supabase, n8n) — tracked, uses ${ENV_VAR} refs
├── .claude/
│   ├── commands/                # /prime, /create-plan, /implement, /plan-video
│   └── skills/
│       ├── README.md            # Skill index — installed skills + when to use
│       ├── mcp-integration/
│       └── skill-creator/
├── context/
│   ├── personal-info.md         # Who Aaron is, his role
│   ├── business-info.md         # Business overview + sales process + tech stack
│   ├── money-model.md           # Pricing, service tiers, upsell ladder, unit economics
│   ├── outstanding-actions.md   # Pending actions requiring Aaron's input
│   ├── strategy.md              # Current priorities
│   ├── youtube-style.md         # YouTube voice, tone, structure, visual style guide
│   ├── WHAT-scope-of-work.md    # WHAT we're building — deliverables, in/out, acceptance, change log
│   └── WHERE-current-data.md   # LIVING STATE — current project status (update frequently)
├── HOW-plans/                   # Dated implementation plans
├── outputs/                     # Deliverables (tracked — do not gitignore)
│   └── youtube/                 # Video plans: outputs/youtube/[video-slug]/{brief,script,shot-list}.md
├── reference/
│   ├── integrations-catalog.md  # Available integrations + env var names
│   └── legal/                   # Service agreements, privacy policy, contract drafts
└── scripts/                     # Automation scripts
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `/prime` | Session init — loads all context, reports current state, recommends next action |
| `/create-plan [request]` | Plan a change (no implementation). Produces a dated plan in `HOW-plans/`. |
| `/implement [plan-path]` | Execute a plan step by step. Always updates `WHERE-current-data.md`. |
| `/plan-video [topic]` | Plan a YouTube video. Walks through brief questions, generates script + shot list in `outputs/youtube/`. After planning, suggest adding to content planner spreadsheet. |

---

## Secrets Policy

- All secrets live in `.env` (gitignored, never committed)
- `.env.example` contains placeholder names only — safe to track
- `reference/integrations-catalog.md` documents what integrations exist and which env vars they need
- Claude may check whether env vars are **present**. Claude must **never print their values**.
- If a var is missing, Claude states exactly which one and directs user to add it to `.env`

---

## Spend Cap Guardrails

API costs can accumulate fast. Layered safeguards to stay in control:

**1. Provider-level alerts and budgets (most important)**
- **Anthropic:** console.anthropic.com → Billing → Usage limits. Set a monthly spend cap and email alerts.
- **OpenAI:** platform.openai.com → Settings → Limits. Set hard limit + soft limit alert.
- **Apify:** console.apify.com → Billing. Set monthly spend limit. Actor runs are billed per compute unit.
- **Supabase:** Free tier has generous limits; watch DB size and egress on paid plans.

**2. Keep prepaid credits low**
- Top up in small amounts (e.g. $20–$50) rather than large lump sums.
- This naturally caps blast radius if a runaway script or misconfigured loop fires.

**3. Know which operations are expensive**
- LLM calls with large context windows (especially GPT-4o, Claude Opus) — avoid in loops without limits.
- Apify actors on large crawl targets — always set `maxItems` and `maxCrawlDepth` limits.
- n8n executions — monitor execution count in n8n dashboard; use error workflows to catch loops.

**4. No complex proxy needed**
- Do not implement a cost-tracking proxy unless explicitly requested.
- Provider dashboards + low prepaid credits are sufficient for current scale.

---

## Learnings Policy

- `learnings-register.md` is append-only — log every mistake, pivot, gotcha, or workflow improvement
- `/implement` must log to learnings-register.md when a learning is encountered
- Outside `/implement`: if meaningful progress was made in chat, Claude should ask: *"Want me to update WHERE-current-data.md with today's progress?"* — do not update unless user confirms
- If a learning changes workflow: update CLAUDE.md or the relevant command doc too

---

## Scope Policy

- `context/WHAT-scope-of-work.md` is the authoritative **WHAT** — deliverables, in/out of scope, acceptance criteria
- Plans (in `HOW-plans/`) are the **HOW** — tasks and steps to deliver the scope
- Plans may change without scope changing. Only update `WHAT-scope-of-work.md` when WHAT changes, not HOW.
- If scope changes: update `WHAT-scope-of-work.md` (In Scope / Out of Scope sections) + add a row to the Scope Change Log
- Rejected scope changes are still logged

---

## WHERE-current-data.md Rules

- This is the single source of truth for "where we're at right now"
- `/implement` MUST update it every run
- Keep it current — stale data limits Claude's usefulness as a strategic partner

---

## Google Sheet — Master Hub

- **Sheet:** "Mycelium AI CRM" — `https://docs.google.com/spreadsheets/d/1N8CkEx3_pHPdxhtrRHHpYGu-50STsDb5Y0T2IxmY47o/`
- Connected via service account (`mycelium-sheets@wide-hold-472208-d5.iam.gserviceaccount.com`)
- Python path: `/c/Users/aaron/AppData/Local/Programs/Python/Python313/python.exe` (Windows Store aliases don't work — use full path)
- Script to write rows: `scripts/add-content-ideas.py`

### Tabs (6)

| Tab | Purpose |
|-----|---------|
| **CRM** | Client pipeline — businesses, contacts, lifecycle stages, opportunities |
| **CRM Lists** | Dropdown reference values for CRM tab (Industry, Location, Lead Source, Lifecycle Stage, Lead Stage, Service Interest) |
| **Content Pipeline** | Content ideas — videos, shorts, posts, with status tracking |
| **Content List** | Dropdown reference values for Content Pipeline (Content Type, Primary Platform, Funnel Stage, Priority, Effort, Status, Owner) |
| **Idea Capture** | All new ideas — app ideas, business ideas, content ideas, anything worth capturing |
| **Passion Projects** | Non-client projects tracked for fun, learning, or portfolio (side projects, tools, experiments) |

### Proactive Behaviors (REQUIRED)

Claude must actively manage the master sheet during every session:

1. **Idea Capture** — When an interesting idea comes up in conversation (app idea, content angle, business opportunity, tool suggestion), ask: *"Would you like me to add this to Idea Capture?"* If yes, write a row using `scripts/add-content-ideas.py` pattern.

2. **Passion Projects** — When working on a non-client project, check if it exists in the Passion Projects tab. If not, ask: *"Would you like me to add this to Passion Projects?"* Keep existing rows updated (status, last updated, next step).

3. **CRM Awareness** — When Aaron mentions a client or business name, check the CRM tab. If the client doesn't exist, ask: *"I don't see [client] in the CRM. Would you like me to add them?"* If the client exists, reference their current lifecycle stage and next step.

4. **Content Ideas** — After `/create-plan` or `/implement`, suggest 1-3 video/content ideas related to the work. Ask: *"Want me to add these to the Content Pipeline?"*

5. **Dropdown Validation Protocol** — Before writing ANY row to any tab, read the corresponding reference list tab (CRM Lists or Content List) and validate that all categorical values match an existing dropdown option exactly. Never guess or invent values. If a value doesn't match any dropdown option, ask Aaron which option to use or whether to add a new one to the reference list.

---

## Naming Conventions

- Plans: `HOW-plans/YYYY-MM-DD-kebab-case-title.md`
- Outputs: `outputs/<project-or-type>/<descriptive-name>.<ext>`
- Scripts: `scripts/<verb-noun>.sh` or `.py`
- Context: prefix-tagged (`WHAT-`, `WHERE-`) for key files; lowercase, hyphenated otherwise

---

## Maintain This File

After any workspace change, check:
1. Does this add functionality users need to know about?
2. Does it change the documented structure?
3. Should a new command, skill, or reference be listed?
4. Does `context/` need updating?

If yes to any → update this file and relevant sections.

---

## Active Projects

_No active projects yet. When a project is started via `/create-plan`, add it here with:_

```
### [Project Name]
- **Status:** [Planning / In Progress / Shipped]
- **Source:** `outputs/[project-folder]/`
- **What:** [One-line description]
- **Scope:** `context/WHAT-scope-of-work.md`
- **State:** `context/WHERE-current-data.md`
```

---

## Project-Specific Notes

_Add project-specific technical context here as projects are built. This section holds knowledge that would otherwise be rediscovered each session — API quirks, SDK gotchas, architecture decisions, build commands, etc._

---

## Notes

- Keep context minimal but sufficient
- Plans live in `HOW-plans/` with dated filenames
- Outputs organized by type/purpose in `outputs/`
- Reference materials in `reference/` for reuse across projects
