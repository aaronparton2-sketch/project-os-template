# Create Plan

Create a detailed implementation plan. Planning only — no implementation happens here.

## Variables

request: $ARGUMENTS

---

## Instructions

**You are creating a PLAN, not implementing.** Research thoroughly, then output a plan document.

---

## Step 1: Classify plan size

**Short plan** — Use when:
- 1–3 files affected
- Low risk, reversible change
- Single clear step

**Full plan** — Use when:
- 4+ files, new command/workflow, or structural changes
- Medium/high risk or multiple steps
- Requires design decisions

State which type you're writing and why.

---

## Step 2: Research phase

Before writing, investigate:

1. Read `CLAUDE.md`, `PROJECT-MAP.md`, `context/WHERE-current-data.md`
2. Read `context/WHAT-scope-of-work.md` — this is the authoritative WHAT; plans must stay inside it
3. Read relevant existing files (commands, outputs, reference, scripts) depending on what's being changed
4. Check `.claude/skills/README.md` — identify which skills (if any) apply
5. Check `reference/integrations-catalog.md` — identify which integrations + env vars are needed
6. Check `learnings-register.md` for relevant past mistakes or insights

---

## Step 3: Write the plan

Save to: `HOW-plans/YYYY-MM-DD-kebab-case-title.md`

Use this structure:

```markdown
# Plan: <descriptive title>

**Created:** YYYY-MM-DD
**Status:** Draft
**Type:** Short | Full
**Request:** <one-line summary>

---

## Overview

### What This Accomplishes
<2-3 sentences: end result + why it matters>

### Why This Matters
<Connect to project goals>

---

## Current State

### Relevant Existing Structure
<Files/folders/patterns that relate to this change>

### Gaps Being Addressed
<What's missing or suboptimal>

---

## Proposed Changes

### New Files

| File Path | Purpose |
|-----------|---------|
| `path/to/file` | Description |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `path/to/file` | What changes and why |

### Files to Delete

| File Path | Reason |
|-----------|--------|

---

## Scope Check

- **Inside scope?** Yes / No — reference `context/WHAT-scope-of-work.md`
- **Scope delta (if No):** List what would change about WHAT we're delivering
- **Decision required:** If out of scope, stop and confirm with user before continuing

_If scope change is accepted: add Step 1 to update `context/WHAT-scope-of-work.md` (In Scope / Out of Scope sections) and add a row to the Scope Change Log._

---

## Integrations & Env Vars

| Service | Env Var(s) Needed | Status |
|---------|-------------------|--------|
| e.g. Supabase | `SUPABASE_URL`, `SUPABASE_ANON_KEY` | Check .env |

_If no integrations needed: "None"_

---

## Skills to Use

| Skill | Why |
|-------|-----|
| e.g. mcp-integration | Setting up MCP server |

_If no skills needed: "None"_

---

## Design Decisions

1. **<Decision>:** <Rationale>
2. **<Decision>:** <Rationale>

### Alternatives Considered
<Other approaches and why rejected>

### Open Questions
<Anything needing user input before implementation — list clearly or write "None">

---

## Step-by-Step Tasks

### Step 1: <Title>
<What to do>

**Actions:**
- <Specific action>

**Files affected:**
- `path/to/file`

---

### Step 2: <Title>
...

---

## Validation Checklist

- [ ] <Verification step>
- [ ] <Verification step>
- [ ] CLAUDE.md updated if structure changed
- [ ] No secrets in tracked files
- [ ] learnings-register.md updated if relevant

---

## Success Criteria

1. <Specific, measurable criterion>
2. <Specific, measurable criterion>

---

## Notes

<Additional context, future considerations>
```

---

## Step 4: Suggest Content Ideas

After creating the plan, check if the work could generate video/content ideas. If so:

1. Suggest 1-3 video or content ideas that relate to the plan (build tutorials, behind-the-scenes, results/reveals, hot takes)
2. Ask Aaron: *"Want me to add these to the Content Pipeline?"*
3. If yes: read **Content List** tab first to validate dropdown values, then append rows to the Google Sheet
4. Reference: master sheet ID = `1N8CkEx3_pHPdxhtrRHHpYGu-50STsDb5Y0T2IxmY47o`

---

## Step 5: Idea Capture & Passion Projects

After creating the plan, check:

1. **Idea Capture** — Did the planning process surface any new ideas (app concepts, business opportunities, tool suggestions)? If so, ask: *"Would you like me to add this to Idea Capture?"*
2. **Passion Projects** — Is this plan for a non-client project? If so, check if it exists in the Passion Projects tab. If not, ask: *"Would you like me to add this to Passion Projects?"*
3. **CRM** — Does the plan involve a client? Check the CRM tab. If the client isn't listed, ask: *"I don't see [client] in the CRM. Would you like me to add them?"*
4. **Dropdown validation** — Before writing ANY row, read the reference list tab (CRM Lists or Content List) and validate all categorical values match exactly.

---

## Step 6: Report

After creating the plan, output:

1. **Plan type** (Short/Full) + brief summary of what it covers
2. **Integrations needed** (env var names) + any that appear missing
3. **Skills to use** (from skills index)
4. **Open questions** requiring user input (if any)
5. **Plan path:** `HOW-plans/YYYY-MM-DD-{name}.md`
6. **Next command:** `/implement HOW-plans/YYYY-MM-DD-{name}.md`
7. **Content ideas** (if any suggested)
8. **Idea Capture / Passion Projects / CRM** — any additions offered or made
