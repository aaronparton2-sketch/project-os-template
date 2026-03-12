---
name: skill-creator
description: Create or update skills for Claude Code. Use when designing, structuring, or packaging a new skill, or updating an existing skill's content and resources.
---

## When to Use

- User asks to create a new skill
- User wants to update or restructure an existing skill
- Designing skill content, triggers, or bundled resources

## About Skills

Skills are markdown files in `.claude/skills/` that extend Claude's capabilities with specialised knowledge and workflows. Each skill is a single `.md` file with YAML frontmatter (`name` + `description`) and a markdown body.

**What skills provide:**
1. Specialised workflows — multi-step procedures for specific domains
2. Tool integrations — instructions for working with specific file formats or APIs
3. Domain expertise — company-specific knowledge, schemas, business logic

## Core Principles

### Concise is Key

The context window is shared. Only add context Claude doesn't already have. Challenge each piece: "Does Claude really need this?" Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

- **High freedom** (text instructions): Multiple approaches valid, context-dependent
- **Medium freedom** (pseudocode/parameters): Preferred pattern exists, some variation OK
- **Low freedom** (specific scripts): Operations are fragile, consistency critical

## Skill Structure

Each skill is a single `.md` file in `.claude/skills/`:

```
.claude/skills/
├── my-skill.md
├── another-skill.md
└── ...
```

If a skill needs supporting files:
- **Scripts** → `scripts/` (project root)
- **Reference docs** → `reference/` (project root)
- **Assets/templates** → `reference/` or `outputs/`

### Skill File Format

```markdown
---
name: my-skill
description: Clear explanation of what the skill does AND when to use it. Include specific triggers.
---

## When to Use

- Bullet list of specific scenarios that trigger this skill
- Include example user phrases

## [Main content sections...]
```

### Frontmatter Rules

- `name`: The skill name (lowercase, hyphenated)
- `description`: Primary triggering mechanism. Must include WHAT the skill does AND WHEN to use it. This is what Claude reads to decide whether to load the skill.

## Creating a New Skill

1. **Understand the need** — What task does this skill help with? Get concrete examples.
2. **Plan the content** — What scripts, references, or knowledge does Claude need?
3. **Write the skill file** — Create `.claude/skills/skill-name.md` with frontmatter + body
4. **Add supporting files** — Move scripts to `scripts/`, references to `reference/`
5. **Update CLAUDE.md** — Add the skill to the skills table in CLAUDE.md
6. **Test and iterate** — Use the skill, notice struggles, improve

### Naming Rules

- Lowercase letters, digits, and hyphens only
- Under 64 characters
- Prefer short, verb-led phrases (e.g., `excalidraw-diagram`, `mcp-integration`)

### Helper Scripts

Available in `scripts/` for scaffolding (from original skill-creator):
- `scripts/init-skill.py` — Generate a skill template
- `scripts/package-skill.py` — Package a skill for distribution
- `scripts/quick-validate.py` — Validate skill structure

## Progressive Disclosure

Keep skill files lean. If a skill needs deep reference material:
1. Keep core workflow in the `.md` file (under 500 lines)
2. Move detailed references to `reference/` with clear file names
3. Reference them from the skill: "For details, see `reference/my-topic.md`"

## What NOT to Include

- README.md, CHANGELOG.md, or other meta-docs
- Information Claude already knows (general programming, common tools)
- Setup/installation guides (those go in `.env.example` or `integrations-catalog.md`)
