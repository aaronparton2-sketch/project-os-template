# Skills Index

Installed skills and when to use them. Reference this during `/create-plan` to identify which skills apply.

---

## Installed Skills

| Skill | Trigger / When to Use | Key Capabilities |
|-------|----------------------|-----------------|
| **mcp-integration** | Adding an MCP server, connecting external tools via Model Context Protocol, configuring `.mcp.json` | SSE, stdio, HTTP, WebSocket server setup; authentication patterns; tool usage examples |
| **skill-creator** | Designing, structuring, or packaging a new skill; updating an existing skill's scripts or references | Skill scaffolding, init/package/validate scripts |
| **excalidraw-diagram** | User asks to draw a diagram, make an Excalidraw diagram, or build an editable visual | Generates `.excalidraw` JSON files; color-coded zones; arrows with labels; fully editable in excalidraw.com |

---

## Usage Rule

Before `/create-plan`, ask: *does this task benefit from an installed skill?*

If yes → reference the skill in the plan's "Skills to use" section.
If a needed capability doesn't exist as a skill → consider creating one with `skill-creator`.

---

## Adding a New Skill

Use the `skill-creator` skill. Each skill lives at `.claude/skills/<skill-name>/` with a `SKILL.md` entry point. Add a row to this table after creation.
