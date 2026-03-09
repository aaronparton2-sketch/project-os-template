# Integrations Catalog

Non-sensitive catalog of available integrations. Env var **names** only — no values ever.
Raw secrets live exclusively in the local `.env` file (gitignored, never committed).

Claude may check whether env vars are present. Claude must **NEVER** print their values.

---

## Safety Rules

- `.env` is gitignored — never tracked, never committed, never shared.
- `.env.example` contains placeholder names only — safe to commit.
- If Claude needs to use an integration: check env var presence, then use. Never log values.
- If an env var is missing: Claude will state exactly which var and direct user to add it to `.env`.
- **Never** paste secret values into chat, plans, outputs, or any tracked file.

---

## Available Integrations

### Anthropic (Claude API)

| Field | Detail |
|-------|--------|
| **Purpose** | LLM API — primary AI provider for agents, completions, embeddings |
| **How used** | Direct API calls, Claude Code itself |
| **Required env vars** | `ANTHROPIC_API_KEY` |
| **Setup notes** | Get key from console.anthropic.com. Use prepaid credits; set spend alerts. |

---

### OpenAI

| Field | Detail |
|-------|--------|
| **Purpose** | LLM API (GPT-4o, o1), embeddings, Whisper transcription, DALL-E |
| **How used** | API calls, fallback models, embedding generation |
| **Required env vars** | `OPENAI_API_KEY` |
| **Setup notes** | Get key from platform.openai.com. Set usage limits in account settings. |

---

### n8n (MCP Server)

| Field | Detail |
|-------|--------|
| **Purpose** | Expose n8n workflows as MCP tools — Claude can trigger workflows directly |
| **How used** | MCP (Model Context Protocol) over HTTP; Claude connects to the MCP endpoint |
| **Required env vars** | `N8N_MCP_SERVER_URL`, `N8N_MCP_ACCESS_TOKEN` |
| **Setup notes** | MCP server URL is the HTTP endpoint of your n8n MCP server node. Access token is a bearer JWT issued by n8n. Configure in Claude's MCP settings (`.mcp.json`). Use `mcp-integration` skill for setup. |

---

### n8n (REST API)

| Field | Detail |
|-------|--------|
| **Purpose** | Manage n8n programmatically — list/trigger/create workflows, manage executions |
| **How used** | REST API calls; base URL + API key in request headers |
| **Required env vars** | `N8N_API_URL`, `N8N_API_KEY` |
| **Setup notes** | `N8N_API_URL` = your n8n base URL + `/api/v1` (e.g. `https://your-instance.app.n8n.cloud/api/v1`). API key is the master API key from n8n settings. |

---

### Apify

| Field | Detail |
|-------|--------|
| **Purpose** | Web scraping, crawlers, data collection, competitor research |
| **How used** | Trigger actors via REST API; poll for results |
| **Required env vars** | `APIFY_API_TOKEN`, `APIFY_USER_ID` |
| **Setup notes** | Get token from console.apify.com. Actor runs are billed per compute unit — check quotas before bulk runs. |

---

### Supabase

| Field | Detail |
|-------|--------|
| **Purpose** | PostgreSQL database, auth, storage, realtime — primary data layer |
| **How used** | API calls (anon/service role keys) + MCP server for Claude direct access |
| **Required env vars** | `SUPABASE_URL`, `SUPABASE_PROJECT_REF`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_ACCESS_TOKEN` (MCP only) |
| **MCP server** | `@supabase/mcp-server-supabase` — configured in `.mcp.json`. Requires `SUPABASE_ACCESS_TOKEN` (Personal Access Token, **not** service role key). |
| **Setup notes** | `SUPABASE_URL` = `https://<project-ref>.supabase.co`. **Service role key bypasses RLS — server-side only.** Personal Access Token: supabase.com/dashboard/account/tokens. |

---

### Google Sheets / Google APIs

| Field | Detail |
|-------|--------|
| **Purpose** | Master business hub — CRM, content pipeline, idea capture, passion projects |
| **How used** | Service account auth for server-side access; Sheets API v4 via gspread |
| **Required env vars** | `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID` |
| **Master sheet** | "Mycelium AI CRM" — `1N8CkEx3_pHPdxhtrRHHpYGu-50STsDb5Y0T2IxmY47o` |
| **Tabs** | CRM, CRM Lists, Content Pipeline, Content List, Idea Capture, Passion Projects |
| **Dropdown validation** | CRM Lists and Content List tabs contain reference values. Always read these before writing rows to validate categorical fields match exactly. |
| **Setup notes** | 1. Create a Google Cloud project and enable the Sheets API. 2. Create a service account, download the JSON key. 3. Share the sheet with the service account email (editor). 4. Store the entire JSON key as a single-line string in `GOOGLE_SERVICE_ACCOUNT_JSON`. |
| **Service account email** | `mycelium-sheets@wide-hold-472208-d5.iam.gserviceaccount.com` |
| **Status** | Fully configured. Sheet shared with service account. Both env vars set in `.env`. |

---

### YouTube (Data API v3 + Analytics API)

| Field | Detail |
|-------|--------|
| **Purpose** | Channel analytics — views, comments, watch time, audience retention, demographics, traffic sources |
| **How used** | OAuth 2.0 Desktop App flow; YouTube MCP server for Claude access |
| **Required env vars** | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_PROJECT_ID` |
| **APIs enabled** | YouTube Data API v3, YouTube Analytics API (both in Google Cloud Console) |
| **Free tier** | 10,000 quota units/day (very generous — hundreds of read calls) |
| **MCP server** | `pauling-ai/youtube-mcp-server` (40 tools, Python + FastMCP) |
| **Status** | Credentials configured in `.env`. MCP server setup pending. |
| **Setup notes** | OAuth token generated on first run (browser consent flow). Token auto-refreshes. Same Google Cloud project as Sheets service account. |

---

### Instagram (Graph API)

| Field | Detail |
|-------|--------|
| **Purpose** | Account insights — post reach, impressions, engagement, saves, shares, comments |
| **How used** | OAuth 2.0 via Meta Developer App; long-lived access token (60-day expiry) |
| **Required env vars** | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` |
| **Pre-requisites** | Instagram Professional account (Creator/Business), Facebook Page linked, Meta Developer App |
| **Free tier** | 200 API calls/hour per account |
| **Status** | Not configured |
| **Setup notes** | Long-lived tokens expire after 60 days of non-use. Needs periodic refresh. |

---

### Upwork (GraphQL + REST API)

| Field | Detail |
|-------|--------|
| **Purpose** | Job monitoring, proposal drafting, messages, contracts. Both freelancer and hirer workflows. |
| **How used** | OAuth 2.0; GraphQL queries for jobs/proposals/messages |
| **Required env vars** | `UPWORK_API_KEY`, `UPWORK_API_SECRET` |
| **Free tier** | 40,000 requests/day (free with approved key) |
| **Status** | Not configured |
| **CRITICAL** | Auto-submitting proposals is **banned by Upwork ToS** — use for monitoring + drafting only, human submits. |
| **Setup notes** | API key approval takes up to 2 weeks. Apply at upwork.com/developer. |

---

## Adding a New Integration

1. Add placeholder var name(s) to `.env.example`
2. Add a section to this file (purpose, how used, required vars, setup notes)
3. Add real value to `.env` locally
4. If using MCP: reference `mcp-integration` skill for `.mcp.json` setup
5. If Claude needs to use it: reference this catalog in the plan or chat
