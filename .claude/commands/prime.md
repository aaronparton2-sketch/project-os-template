# Prime

Session initialization. Load full workspace context, report current state, recommend next action.

---

## Run

```
pwd
ls -la
```

If `tree` is available: `tree -L 4 --gitignore`
Otherwise: `find . -not -path './.git/*' -not -path './node_modules/*' | sort | head -60`

List recent plans: `ls -lt HOW-plans/ | head -5`
List recent outputs: `ls -lt outputs/ | head -5`

---

## Read (in this order)

1. `CLAUDE.md`
2. `PROJECT-MAP.md`
3. `reference/integrations-catalog.md`  ← read BEFORE context so integration status informs state report
4. `context/WHAT-scope-of-work.md`  ← WHAT we're building; read before current-data
5. `context/WHERE-current-data.md`  ← WHERE we are now; drives the status report
6. `.claude/skills/README.md`
7. `learnings-register.md`
8. All files in `./context/`

---

## Check environment

**First: check if `.env` exists at all.** If it does NOT exist, output a prominent warning BEFORE anything else in the report:

```
⚠️  NO .env FILE FOUND — integrations will not work.
Copy your .env from an existing project or your secure backup:
  cp /path/to/your/master/.env .env
Then re-run /prime.
```

If `.env` exists, check each integration's env vars.
Report which are **present** (✓) and which are **missing** (✗). **Never print values.**

Run these checks (one per integration):
```bash
[ -f .env ] && grep -q "ANTHROPIC_API_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "OPENAI_API_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "N8N_MCP_SERVER_URL=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "N8N_MCP_ACCESS_TOKEN=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "N8N_API_URL=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "N8N_API_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "APIFY_API_TOKEN=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "APIFY_USER_ID=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "SUPABASE_URL=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "SUPABASE_ANON_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "SUPABASE_SERVICE_ROLE_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "SUPABASE_PUBLISHABLE_KEY=." .env && echo "present" || echo "missing"
[ -f .env ] && grep -q "GOOGLE_SERVICE_ACCOUNT_JSON=." .env && echo "present" || echo "missing"
```

---

## Output

Provide a structured report:

### 1. Who I am + workspace purpose + Claude's role
One short paragraph. Pull from context/.

### 2. Current scope summary
Pull from `context/WHAT-scope-of-work.md`:
- Project goal (1 sentence)
- In-scope highlights (top 3 deliverables)
- Out-of-scope highlights (key exclusions)
- Any recent scope changes (last row of Scope Change Log, or "None")

### 3. Current project state
Pull directly from `context/WHERE-current-data.md`:
- Active project name + goal
- Current status
- What's done / in progress / blockers

### 4. Available commands
Brief table: command → purpose.

### 5. Available skills + integrations
- Skills: list from `.claude/skills/README.md`
- Integrations: list from `reference/integrations-catalog.md` with ✓/✗ env var status
  - Group by integration (not per-var) for readability
  - Flag any integration with ALL vars missing as "not configured"
  - Flag any integration with SOME vars missing as "partially configured — missing: VAR_NAME"

### 6. Latest plans + relevant outputs
List recent plan files and any relevant outputs.

### 7. Outstanding actions
Pull from `context/outstanding-actions.md` — list any pending items that need Aaron's input.

### 8. Top 3 blockers or open questions
Pulled from WHERE-current-data.md or inferred from context.

### 9. Recommended next action
Exact command syntax:
- `/create-plan <description>` if no plan exists for the next step
- `/implement HOW-plans/<filename>.md` if a plan is ready
- Or a specific chat prompt if input is needed first
