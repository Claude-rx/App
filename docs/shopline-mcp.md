# SHOPLINE Developer MCP

Connects Claude to SHOPLINE's developer docs and API specs.
Source: https://developer.shopline.com/docs/apps/development-tool/shopline-developer-mcp

## Setup (this repo)
- `.mcp.json` registers the server (stdio, `npx -y @shoplineos/shopline-developer-mcp`).
- Claude Code asks once to approve the project server, then loads it in every session for this repo.
- No API key needed. Requires Node.js 18+.

## Tools
| Tool | Use |
|---|---|
| `shopline_readme` | Usage rules and best practices |
| `search_shopline_docs` | Search the developer docs |
| `read_full_docs` | Read a full doc page by URL |
| `search_admin_rest_endpoints` | Find Admin REST endpoints |
| `get_admin_rest_endpoint_detail` | Request/response params and examples |
| `get_rest_api_definition` | Full Admin REST spec |
| `get_graphql_schema` | Storefront GraphQL schema |
| `validate_graphql_codes` | Check GraphQL for invalid or deprecated fields |
| `shopline_mcp_feedback` | Send feedback to SHOPLINE |

## Claude Desktop / Cursor
Paste the same block into `claude_desktop_config.json` (Settings → Developer → Edit Config) or Cursor (Settings → Tools & MCP), then fully restart the app:

```json
{
  "mcpServers": {
    "shopline-developer-mcp": {
      "command": "npx",
      "args": ["-y", "@shoplineos/shopline-developer-mcp"]
    }
  }
}
```

## Verify
`claude mcp list` → `shopline-developer-mcp: ✓ Connected`.
