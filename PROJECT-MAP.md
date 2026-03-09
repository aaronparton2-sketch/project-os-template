# Project OS — Workspace Map

This workspace is the operating system for Mycelium AI projects. Every session starts with `/prime`. Every meaningful change goes through `/create-plan` → `/implement`.

---

## Structure

```
.
├── CLAUDE.md                    # Core context — always loaded. Source of truth.
├── PROJECT-MAP.md               # This file. Workspace map + workflow.
├── learnings-register.md        # Append-only log of mistakes, pivots, insights.
├── .env                         # Local secrets (gitignored — never commit)
├── .env.example                 # Placeholder var names only (tracked)
├── .claude/
│   ├── commands/                # Slash commands
│   │   ├── prime.md             # /prime — session init
│   │   ├── create-plan.md       # /create-plan — plan before building
│   │   ├── implement.md         # /implement — execute a plan
│   │   └── plan-video.md        # /plan-video — YouTube content planning
│   └── skills/
│       ├── README.md            # Skill index — what's installed + when to use
│       ├── mcp-integration/     # Skill: MCP server setup
│       └── skill-creator/       # Skill: Create/update skills
├── context/
│   ├── personal-info.md         # Who you are, your role
│   ├── business-info.md         # Business overview
│   ├── strategy.md              # Current priorities + goals
│   ├── youtube-style.md         # YouTube voice, tone, structure, visual style guide
│   ├── WHAT-scope-of-work.md    # WHAT we're building (deliverables, in/out, change log)
│   └── WHERE-current-data.md   # WHERE we are right now (living state — update frequently)
├── HOW-plans/                   # Implementation plans (dated, kebab-case)
├── outputs/                     # Deliverables and work products (tracked)
├── reference/
│   └── integrations-catalog.md  # Available integrations + env var names (non-sensitive)
└── scripts/                     # Automation scripts
```

---

## Core Workflow

```
Session start  →  /prime
New feature    →  /create-plan [request]  →  /implement [plan-path]
YouTube video  →  /plan-video [topic]     →  brief + script + shot list in outputs/youtube/
Content ideas  →  After /create-plan or /implement, Claude suggests video ideas → add to Content Pipeline tab
Idea capture   →  When interesting ideas surface in chat → Claude asks "Add to Idea Capture?" → writes to sheet
CRM awareness  →  When working with clients → Claude checks CRM tab → offers to add unknown clients
Passion proj   →  When working on non-client projects → Claude checks/updates Passion Projects tab
Mistake/pivot  →  Update learnings-register.md  →  Update CLAUDE.md if workflow changes
Progress       →  Update context/WHERE-current-data.md
```

## Active Projects

_No active projects. See CLAUDE.md → Active Projects once a project is started._

---

## Golden Rules

1. **Chat-first.** Don't create files unless required by a command or explicitly asked.
2. **Plan before building.** Use `/create-plan` for anything touching 2+ files or a new workflow.
3. **Secrets in .env only.** Never paste keys in chat or commit them.
4. **Keep WHERE-current-data.md current.** It's the single source of truth for project state.
5. **Log learnings.** Every mistake or pivot gets a row in learnings-register.md.
6. **CLAUDE.md stays accurate.** Update it whenever workspace structure changes.
7. **Scope = WHAT. Plans = HOW.** If WHAT changes, update WHAT-scope-of-work.md + log it. Plans change freely.
