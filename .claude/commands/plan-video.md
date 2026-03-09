# Plan Video

Plan a YouTube video from scratch. Walk through the brief, generate the script, shot list, and AI image prompts.

Standalone command — run anytime, not tied to `/create-plan`.

---

## Context to load

1. `context/youtube-style.md` — Aaron's voice, tone, structure, visual style
2. `context/personal-info.md` — who Aaron is
3. `context/business-info.md` — Mycelium AI context
4. `context/strategy.md` — current priorities (content alignment)

If a project is active, also read:
- `context/WHAT-scope-of-work.md` — what was built (for the video subject matter)
- `context/WHERE-current-data.md` — current state (what's done, what's interesting to show)

---

## Step 1: Video Brief (ask questions)

Ask the user these questions to fill out the Video Brief. Use `AskUserQuestion` for structured choices where applicable. Ask in batches of 3-4 max.

**Required brief fields:**

| Field | Question to ask |
|-------|----------------|
| Working title | "What's the working title or topic for this video?" |
| Target viewer | "Who is the ONE specific person watching this? (e.g., 'a creative 25-year-old who runs a side hustle and is curious about AI')" |
| Video promise | "In one sentence — what will the viewer be able to do, know, or feel after watching?" |
| Hook angle | "What's your hook? Options: surprising statement, question, demonstration, transformation reveal" |
| Primary emotion | "What emotion drives the click? Options: curiosity, FOMO, aspiration, frustration, relief" |
| Length target | "How long? (3-5 min / 5-7 min / 7-10 min)" |
| CTA goal | "What's the single action you want viewers to take?" |
| Thumbnail concept | "Describe the thumbnail: your expression, the product/visual, any text overlay" |

If the user has already provided some of this info (e.g., in the prompt), skip those questions and confirm what you have.

---

## Step 2: Generate the Video Brief

Create `outputs/youtube/[video-slug]/brief.md` with all fields filled in.

Format:

```markdown
# Video Brief — [Working Title]

| Field | Detail |
|-------|--------|
| Working title | ... |
| Target viewer | ... |
| Video promise | ... |
| Hook angle | ... |
| Primary emotion | ... |
| Length target | ... |
| CTA goal | ... |
| Thumbnail concept | ... |
| SEO keywords | ... (suggest 3-5 based on topic) |
```

---

## Step 3: Generate the Script

Create `outputs/youtube/[video-slug]/script.md` using the structure from `context/youtube-style.md`.

**Script format — each section must include:**

```markdown
## SECTION NAME (timestamp range)

### Script
> The actual words Aaron will say. Written in his voice (see youtube-style.md).
> Use natural language, not bullet points.

### A-Roll
- Camera angle and delivery notes

### B-Roll / Visuals
- Specific B-roll shots, screen recordings, stock footage
- **AI image:** [Description of illustration to generate] — style: clean cartoon/illustration
- Sound effects if applicable

### Notes
- Delivery tips, pacing notes, where to pause for jokes
```

**Section sequence:**
1. Hook (max 15 seconds — 2-3 sentences)
2. Why + Intro (max 60 seconds)
3. Body sections (B1, B2, B3 — expand to B4/B5 for longer videos)
4. Outro + CTA (max 60 seconds — primary CTA first, secondary CTA second)

**Rules:**
- Write in Aaron's voice (casual, self-deprecating, "bloke" energy)
- Include retention bridges between body sections
- Every body section needs a mini-payoff
- AI image prompts should specify "clean illustration / cartoon style"
- Include timestamp estimates based on ~150 words per minute

---

## Step 4: Generate the Shot List

Create `outputs/youtube/[video-slug]/shot-list.md`.

**Group shots by SETUP (not chronological) — for efficient batch filming:**

```markdown
# Shot List — [Working Title]

## Setup 1: Talking Head (main angle)
| Shot # | Section | Description | Notes |
|--------|---------|-------------|-------|
| 1 | Hook | Deliver hook line, energetic | Look into camera, hand gestures |
| 2 | Why+Intro | "If you've ever wanted to..." | Slightly amused expression |
...

## Setup 2: Side Angle (desk/dev setup)
...

## Setup 3: Screen Recordings
| Shot # | Section | Description | Notes |
|--------|---------|-------------|-------|
| 10 | B2 | VS Code with Claude Code running | Speed up 3x, zoom on key moments |
...

## Setup 4: Outdoor / Lifestyle
...

## AI Images to Generate
| # | Description | Style | Used in |
|---|-------------|-------|---------|
| 1 | ... | Clean cartoon | B1 |
...

## Sound Effects
| # | Description | Used in |
|---|-------------|---------|
| 1 | ... | B2 |
...
```

---

## Step 5: Update project state

If a project is active:
- Add a note to `context/WHERE-current-data.md` that a video plan has been created
- Add the plan path to the "Pointers" section

---

## Output structure

```
outputs/youtube/
  [video-slug]/
    brief.md
    script.md
    shot-list.md
```

`[video-slug]` = kebab-case of the working title (e.g., `build-saas-with-ai`).

---

## Notes

- This command does NOT create implementation plans (that's `/create-plan`)
- This command does NOT touch code or build anything (that's `/implement`)
- If the user says "plan a video for this project", load the project context first
- Always read `context/youtube-style.md` before generating ANY script content
