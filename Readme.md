## What is it?

A [Model Context Protocol](https://modelcontextprotocol.io/) Server running over SSE

## What it offers?

Tools for LLM to get decisions of the Czech Supreme Court, Supreme Administrative Court and Constitutional Court based on the case number.

In addition, it also can assess proposals discussed in Czech Chamber of Deputies. It can either find a proposal based on the act name or get details on the specific proposal state based on its number.

### Available Tools

#### 🏛️ `get-court-decision`

**Description:** Retrieves Czech court decisions with automatic court type detection based on case number format.

**Supported Courts:**
- **Supreme Court (Nejvyšší soud)** - Civil and criminal cases
- **Supreme Administrative Court (Nejvyšší správní soud)** - Administrative cases  
- **Constitutional Court (Ústavní soud)** - Constitutional cases

**Parameters:**
- `case_number` (string, required): Case number in court-specific format

**Supported Formats:**

| Court | Format | Example | Identification Pattern |
|-------|--------|---------|----------------------|
| Supreme Court | `XX Cdo XXXX/YYYY` or `XX Tdo XXXX/YYYY` | `21 Cdo 1096/2021` | Contains `Cdo` or `Tdo` |
| Supreme Administrative Court | `X(X) [Registry] XXXX/YYYY` | `7 As 218/2021` | Contains registry codes (As, Ads, Afs, etc.) |
| Constitutional Court | `[Senate].ÚS XX/YY` | `I.ÚS 23/23`, `Pl.ÚS 1589/22` | Contains `ÚS` |

---

### 📋 `search-act-proposal`

**Description:** Searches for act proposals in the Czech Chamber of Deputies with automatic detection of search type (by number or by name).

**Search Types:**
- **By Proposal Number**: Direct lookup using proposal number
- **By Act Name**: Text search through act names and descriptions

**Parameters:**
- `query` (string, required): Search query - either proposal number or act name

**Search Format Detection:**

| Input Type | Detection Rule | Example |
|------------|---------------|---------|
| Proposal Number | Pure digits or numeric string | `"5"`, `"255"`, `"1234"` |
| Act Name | Contains letters | `"o inspekci práce"`, `"zákoník práce"` |

## What do I need?

MCP Client, such is Claude Desktop or [LibreChat](https://github.com/danny-avila/LibreChat)

## How to run this?

Using Docker with precompiled image as per docker-compose.yml. App is listening on port 8957.

## How to add to LibreChat

In your librechat.yaml file, add the following section:

```yaml
mcpServers:
  mcp-czech-legal:
    type: streamable-http
    url: URL of your docker container # e.g. http://localhost:8957/mcp
```

## How to use in LibreChat

After the server is added to LibreChat as per above, restart LibreChat to connect to MCP server and discover tools. Then, create an agent and add the respective tools to agent.

When the agent is created, you may ask the agent to summarize a decision of the provided case number.