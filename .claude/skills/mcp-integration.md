---
name: MCP Integration
description: Use when adding an MCP server, integrating MCP, configuring .mcp.json, setting up Model Context Protocol, or connecting an external service. Covers SSE, stdio, HTTP, WebSocket server types.
---

## When to Use

- User asks to "add MCP server", "integrate MCP", "configure .mcp.json"
- Setting up a new external tool connection for Claude Code
- Discussing MCP server types (SSE, stdio, HTTP, WebSocket)
- Troubleshooting MCP server connections

## Overview

Model Context Protocol (MCP) enables Claude Code to integrate with external services by providing structured tool access. Use MCP to expose external service capabilities as tools.

**Key capabilities:**
- Connect to external services (databases, APIs, file systems)
- Provide 10+ related tools from a single service
- Handle OAuth and complex authentication flows

## MCP Server Configuration

All MCP servers are configured in `.mcp.json` at the project root. **Every server must use `${ENV_VAR}` references** for credentials — no hardcoded values.

### Method: .mcp.json (Standard)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-package"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

## MCP Server Types

### stdio (Local Process)

Best for: local tools, custom servers, NPM packages.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": { "LOG_LEVEL": "debug" }
  }
}
```

### SSE (Server-Sent Events)

Best for: hosted cloud services, OAuth authentication.

```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

### HTTP (REST API)

Best for: REST API backends, token-based auth.

```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### WebSocket (Real-time)

Best for: real-time streaming, low-latency.

```json
{
  "realtime": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": { "Authorization": "Bearer ${TOKEN}" }
  }
}
```

## Quick Reference

| Type | Transport | Best For | Auth |
|------|-----------|----------|------|
| stdio | Process | Local tools, custom servers | Env vars |
| SSE | HTTP | Hosted services, cloud APIs | OAuth |
| HTTP | REST | API backends, token auth | Tokens |
| ws | WebSocket | Real-time, streaming | Tokens |

## Adding a New MCP Server (Checklist)

1. Choose server type (stdio/SSE/HTTP/ws)
2. Add entry to `.mcp.json` using `${ENV_VAR}` refs
3. Add env vars to `.env` + `.env.example` (under MCP section)
4. Add row to MCP Server Summary in `reference/integrations-catalog.md`
5. Run any one-time auth flows (OAuth, etc.)
6. Restart Claude Code
7. Test with `/prime` — integration status will show

## Security Rules

- Always use HTTPS/WSS, never HTTP/WS
- Use `${ENV_VAR}` for all tokens — never hardcode
- Pre-allow specific MCP tools in commands, not wildcards
- Document required env vars in `.env.example`

## Deep-Dive References

For detailed information on specific topics, consult:

- **`reference/mcp/server-types.md`** — Deep dive on each server type, lifecycle, troubleshooting
- **`reference/mcp/authentication.md`** — OAuth, tokens, env vars, dynamic headers, security
- **`reference/mcp/tool-usage.md`** — Using MCP tools in commands and agents, patterns
- **`reference/mcp/examples/`** — Working JSON config examples (stdio, SSE, HTTP)
