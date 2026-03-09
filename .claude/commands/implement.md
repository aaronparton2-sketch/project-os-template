# Implement

Execute an implementation plan created by `/create-plan`.

## Variables

plan_path: $ARGUMENTS (e.g. `HOW-plans/2026-01-28-add-command.md`)

---

## Phase 1: Understand the Plan

1. Read the plan file completely — do not skim.
2. Check for blockers:
   - Open questions requiring user input?
   - Missing env vars needed for this plan? (check `.env` presence only)
   - Dependencies on external decisions?
   - If blockers exist: **stop and ask the user before proceeding.**
3. Confirm plan is ready: Status = "Draft" or "Ready", no unfilled placeholders.

---

## Phase 2: Execute

1. Follow Step-by-Step Tasks in exact order.
2. For each step:
   - Read affected files before modifying
   - Write complete files — never stubs
   - Verify correctness before moving to next step
3. If a step can't be completed as written: note the issue, adapt if intent is clear, or ask user.
4. Document any deviations as you go.

---

## Phase 3: Validate

Run through the plan's Validation Checklist:
- Check off each item
- Note any that fail

Verify Success Criteria are met.

Check cross-references:
- New files referenced where they should be
- CLAUDE.md updated if structure changed
- Naming conventions followed

---

## Phase 4: Update Plan Status

In the plan file:
1. Change `**Status:** Draft` → `**Status:** Implemented`
2. Append at end of file:

```markdown
---

## Implementation Notes

**Implemented:** YYYY-MM-DD

### Summary
<Brief summary of what was done>

### Deviations from Plan
<List deviations, or "None">

### Issues Encountered
<List issues and resolutions, or "None">
```

---

## Phase 5: Update WHAT-scope-of-work.md (if plan includes scope changes)

If the plan's Scope Check section indicates a scope change was accepted:
1. Update `context/WHAT-scope-of-work.md` — edit In Scope / Out of Scope sections to reflect the change
2. Append a row to the Scope Change Log: `Date/Time | Change requested | Accepted | Impact | Plan link`

If no scope change: skip this phase entirely.

---

## Phase 6: Update WHERE-current-data.md (REQUIRED)

After every `/implement` run, update `context/WHERE-current-data.md`:
- Set **Last updated** to current date/time
- Update **Current status**, **What's done**, **In progress**, **Blockers**
- Append a line to the **Progress log**
- Update **Next steps** and **What Claude should do next**

---

## Phase 7: Update learnings-register.md (when relevant)

If any of the following occurred during implementation:
- A mistake was made and corrected
- An assumption was wrong
- A tool or API behaved unexpectedly
- A workflow improvement was discovered

→ Append a row to `learnings-register.md` with: Date/Time | Type | Issue | Learning | Fix | Files/Links

If nothing noteworthy: skip.

---

## Phase 8: Suggest Content Ideas (when relevant)

After implementation, check if the work done could generate video or content ideas:
1. Suggest 1-3 content ideas related to the completed work (build tutorials, behind-the-scenes, results/reveals, hot takes)
2. Ask Aaron: *"Want me to add these to the Content Pipeline?"*
3. If yes: read **Content List** tab first to validate dropdown values, then append rows to Google Sheet (ID: `1N8CkEx3_pHPdxhtrRHHpYGu-50STsDb5Y0T2IxmY47o`)
4. If the work is minor or no content angle exists: skip.

---

## Phase 9: Idea Capture & Passion Projects (when relevant)

Check if the implementation surfaced anything worth tracking:

1. **Idea Capture** — Did any new ideas come up during implementation (app concepts, features, business opportunities, tool suggestions)? If so, ask: *"Would you like me to add this to Idea Capture?"*
2. **Passion Projects** — Is this a non-client project? Check if it exists in the Passion Projects tab. If not, ask: *"Would you like me to add this to Passion Projects?"* If it exists, update its row (status, last updated, next step).
3. **CRM Awareness** — Does this work involve a client? Check the CRM tab. If the client isn't listed, ask: *"I don't see [client] in the CRM. Would you like me to add them?"* If they exist, review their current state for context.
4. **Dropdown Validation Protocol** — Before writing ANY row to any tab, read the corresponding reference list tab (CRM Lists or Content List) and validate that all categorical values match an existing dropdown option exactly. Never guess or invent values.

---

## Report

End with this format in chat:

```
## Implementation Complete

### Summary
- <What was done>
- <What was done>

### Files Changed
**Created:**
- `path/to/new-file`

**Modified:**
- `path/to/modified-file`

**Deleted:**
- (none)

### Validation
- [x] <Passed check>
- [ ] <Failed check — note why>

### Learnings Logged
- <Row added to learnings-register.md, or "None">

### Deviations from Plan
<None, or describe>

### Plan Status
Updated `HOW-plans/<filename>.md` → Implemented

### Idea Capture / Passion Projects / CRM
- <Any additions offered or made, or "None">

### Next Steps
<1-3 recommended next actions>
```
