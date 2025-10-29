# MCP SSE Server Documentation

## 📋 Overview

The MCP (Model Context Protocol) SSE (Server-Sent Events) server provides a standardized way for AI models and applications to exchange context information in real-time using Server-Sent Events.

## 🚀 Quick Start

### 1. Enable MCP Server

In your `.env` file:

```bash
MCP_ENABLED=true
MCP_ENDPOINT=/mcp/sse
```

### 2. Start the Application

```bash
uvicorn main:app --reload
```

### 3. Test the Connection

```bash
# Check server info
curl http://localhost:8000/mcp/sse/info

# Connect to SSE stream
curl -N http://localhost:8000/mcp/sse
```

## ⚙️ Configuration

All MCP settings are configured via environment variables with the `MCP_` prefix.

### Basic Configuration

```bash
# Enable/disable MCP server
MCP_ENABLED=true

# SSE endpoint path
MCP_ENDPOINT=/mcp/sse

# Server identification
MCP_SERVER_NAME=FastAPI MCP Server
MCP_SERVER_VERSION=0.1.0
```

### SSE Configuration

```bash
# SSE retry interval in milliseconds
MCP_SSE_RETRY=15000

# Ping interval to keep connection alive (seconds)
MCP_SSE_PING_INTERVAL=30
```

### Security Configuration

```bash
# Require authentication
MCP_REQUIRE_AUTH=true

# API key for authentication
MCP_API_KEY=your-secret-api-key-here
```

### Feature Configuration

```bash
# Enable tools capability
MCP_ENABLE_TOOLS=true

# Enable resources capability
MCP_ENABLE_RESOURCES=true

# Enable prompts capability
MCP_ENABLE_PROMPTS=true
```

## 📡 API Endpoints

### Server Information

**GET** `/mcp/sse/info`

Get MCP server information and capabilities.

**Response**:
```json
{
  "name": "FastAPI MCP Server",
  "version": "0.1.0",
  "protocol_version": "2024-11-05",
  "capabilities": {
    "tools": {"list": true, "call": true},
    "resources": {"list": true, "read": true},
    "prompts": {"list": true, "get": true}
  }
}
```

### SSE Stream

**GET** `/mcp/sse`

Connect to the MCP SSE stream.

**Headers**:
- `Authorization: Bearer <api-key>` (if authentication is enabled)

**Response**: SSE stream with events:
- `server_info` - Initial server information
- `ping` - Periodic keepalive messages

**Example**:
```bash
curl -N -H "Authorization: Bearer your-api-key" http://localhost:8000/mcp/sse
```

### List Tools

**GET** `/mcp/sse/tools`

List all available MCP tools.

**Response**:
```json
{
  "tools": [
    {
      "name": "get_user_info",
      "description": "Get information about a user by ID",
      "input_schema": {
        "type": "object",
        "properties": {
          "user_id": {
            "type": "integer",
            "description": "The user ID to query"
          }
        },
        "required": ["user_id"]
      }
    }
  ]
}
```

### List Resources

**GET** `/mcp/sse/resources`

List all available MCP resources.

**Response**:
```json
{
  "resources": [
    {
      "uri": "api://users/list",
      "name": "Users List",
      "description": "List of all users in the system",
      "mime_type": "application/json"
    }
  ]
}
```

### List Prompts

**GET** `/mcp/sse/prompts`

List all available MCP prompts.

**Response**:
```json
{
  "prompts": [
    {
      "name": "summarize_user",
      "description": "Generate a summary of user information",
      "arguments": [
        {
          "name": "user_id",
          "description": "The user ID to summarize",
          "required": true
        }
      ]
    }
  ]
}
```

## 🔧 Usage Examples

### Python Client

```python
import httpx
import json

# Connect to MCP SSE stream
with httpx.stream(
    "GET",
    "http://localhost:8000/mcp/sse",
    headers={"Authorization": "Bearer your-api-key"},
    timeout=None
) as response:
    for line in response.iter_lines():
        if line.startswith("data:"):
            data = json.loads(line[5:])
            print(f"Received: {data}")
```

### JavaScript Client

```javascript
const eventSource = new EventSource('http://localhost:8000/mcp/sse');

eventSource.addEventListener('server_info', (e) => {
  const data = JSON.parse(e.data);
  console.log('Server info:', data);
});

eventSource.addEventListener('ping', (e) => {
  const data = JSON.parse(e.data);
  console.log('Ping:', data.timestamp);
});

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
};
```

### cURL Client

```bash
# Connect to SSE stream
curl -N -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/mcp/sse

# Get server info
curl http://localhost:8000/mcp/sse/info

# List available tools
curl http://localhost:8000/mcp/sse/tools
```

## 🛠️ Registering Custom Capabilities

### Register a Tool

```python
from core.mcp_server import get_mcp_server, MCPTool

mcp_server = get_mcp_server()

# Register custom tool
mcp_server.register_tool(MCPTool(
    name="analyze_data",
    description="Analyze data and return insights",
    input_schema={
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "description": "Data to analyze"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["statistics", "trends", "anomalies"]
            }
        },
        "required": ["data", "analysis_type"]
    }
))
```

### Register a Resource

```python
from core.mcp_server import get_mcp_server, MCPResource

mcp_server = get_mcp_server()

# Register custom resource
mcp_server.register_resource(MCPResource(
    uri="api://reports/monthly",
    name="Monthly Reports",
    description="Access to monthly report data",
    mime_type="application/json"
))
```

### Register a Prompt

```python
from core.mcp_server import get_mcp_server, MCPPrompt

mcp_server = get_mcp_server()

# Register custom prompt
mcp_server.register_prompt(MCPPrompt(
    name="generate_report",
    description="Generate a comprehensive report",
    arguments=[
        {
            "name": "report_type",
            "description": "Type of report to generate",
            "required": True
        },
        {
            "name": "date_range",
            "description": "Date range for the report",
            "required": False
        }
    ]
))
```

## 🔐 Security

### Authentication

When `MCP_REQUIRE_AUTH=true`, clients must provide an API key:

```bash
# Environment variable
MCP_API_KEY=your-secret-api-key

# Client request
curl -H "Authorization: Bearer your-secret-api-key" \
  http://localhost:8000/mcp/sse
```

### Best Practices

1. **Always use authentication in production**:
   ```bash
   MCP_REQUIRE_AUTH=true
   MCP_API_KEY=<strong-random-key>
   ```

2. **Use HTTPS in production** to encrypt SSE traffic

3. **Rotate API keys regularly**

4. **Monitor SSE connections** for unusual activity

5. **Rate limit SSE connections** if needed

## 📊 Monitoring

### Connection Logging

The MCP server logs all connections and disconnections:

```
INFO: MCP SSE connection established from 127.0.0.1
INFO: MCP SSE client disconnected
```

### Health Check

Check if MCP is enabled and healthy:

```bash
curl http://localhost:8000/mcp/sse/info
```

### Metrics

Monitor:
- Active SSE connections
- Event throughput
- Connection duration
- Error rates

## 🐛 Troubleshooting

### SSE Connection Issues

**Problem**: Connection drops frequently

**Solution**:
```bash
# Increase ping interval
MCP_SSE_PING_INTERVAL=60

# Adjust retry interval
MCP_SSE_RETRY=30000
```

### Authentication Failures

**Problem**: 401 Unauthorized errors

**Solution**:
- Verify `MCP_API_KEY` matches client key
- Check `Authorization` header format: `Bearer <key>`
- Ensure `MCP_REQUIRE_AUTH=true` if authentication is needed

### Server Not Starting

**Problem**: MCP server doesn't initialize

**Solution**:
```bash
# Check if MCP is enabled
MCP_ENABLED=true

# Verify dependencies are installed
uv add sse-starlette mcp

# Check application logs for errors
```

## 🔄 SSE Event Format

Events follow the SSE specification:

```
event: server_info
data: {"name":"FastAPI MCP Server","version":"0.1.0"}
retry: 15000

event: ping
data: {"timestamp":"2025-10-29T10:00:00.000000"}

```

## 📚 MCP Protocol

This implementation follows the Model Context Protocol specification:

- Protocol Version: `2024-11-05`
- Transport: Server-Sent Events (SSE)
- Capabilities: Tools, Resources, Prompts

For more details, see the [MCP Specification](https://modelcontextprotocol.io/).

## 🎯 Use Cases

1. **AI Model Integration**: Share context with AI models in real-time
2. **Live Data Streaming**: Stream updates to AI applications
3. **Tool Discovery**: Allow AI models to discover available tools
4. **Resource Access**: Provide AI models access to resources
5. **Prompt Management**: Manage and share prompts with AI systems

## 📝 Configuration Summary

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENABLED` | `false` | Enable MCP server |
| `MCP_ENDPOINT` | `/mcp/sse` | SSE endpoint path |
| `MCP_SERVER_NAME` | `FastAPI MCP Server` | Server name |
| `MCP_SERVER_VERSION` | `0.1.0` | Server version |
| `MCP_SSE_RETRY` | `15000` | Retry interval (ms) |
| `MCP_SSE_PING_INTERVAL` | `30` | Ping interval (seconds) |
| `MCP_REQUIRE_AUTH` | `false` | Require authentication |
| `MCP_API_KEY` | `None` | API key |
| `MCP_ENABLE_TOOLS` | `true` | Enable tools |
| `MCP_ENABLE_RESOURCES` | `true` | Enable resources |
| `MCP_ENABLE_PROMPTS` | `true` | Enable prompts |

---

**Last Updated**: October 29, 2025

For more information, see:
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)

