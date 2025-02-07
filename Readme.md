# What is it?

A [Model Context Protocol](https://modelcontextprotocol.io/) Server running over SSE

# What it offers?

Tools for LLM to get decisions of the Czech Supreme Court, Supreme Administrative Court and Constitutional Court based on the case number.

In addition, it also can assess proposals discussed in Czech Chamber of Deputies. It can either find a proposal based on the act name or get details on the specific proposal state based on its number.

# What do I need?

MCP Client, such is Claude Desktop or [LibreChat](https://github.com/danny-avila/LibreChat)

# How to run this?

Using Docker with precompiled image as per docker-compose.yml. App is listening on port 8957.

## How to add to LibreChat

In your librechat.yaml file, add the following section:

```yaml
mcpServers:
  media-creator:
    type: sse # type can optionally be omitted
    url: URL of your docker container # e.g. http://localhost:8957/sse
```

## How to use in LibreChat

After the server is added to LibreChat as per above, restart LibreChat to connect to MCP server and discover tools. Then, create an agent and add the respective tools to agent.

When the agent is created, you may ask the agent to summarize a decision of the provided case number.