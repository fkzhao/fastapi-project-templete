# MCP SSE Server Quick Reference

## 🚀 Quick Start

### Enable MCP Server

```bash
# In .env file
MCP_ENABLED=true
```

### Test Connection

```bash
# Check server info
curl http://localhost:8000/mcp/sse/info

# Connect to SSE stream
curl -N http://localhost:8000/mcp/sse
```

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENABLED` | `false` | Enable/disable MCP server |
| `MCP_ENDPOINT` | `/mcp/sse` | SSE endpoint path |
| `MCP_SERVER_NAME` | `FastAPI MCP Server` | Server name |
| `MCP_SSE_PING_INTERVAL` | `30` | Ping interval (seconds) |
| `MCP_REQUIRE_AUTH` | `false` | Require authentication |
| `MCP_API_KEY` | `None` | API key for auth |
| `MCP_ENABLE_TOOLS` | `true` | Enable tools |
| `MCP_ENABLE_RESOURCES` | `true` | Enable resources |
| `MCP_ENABLE_PROMPTS` | `true` | Enable prompts |

## 📡 Endpoints

### Server Info
```bash
GET /mcp/sse/info
```

### SSE Stream
```bash
GET /mcp/sse
Authorization: Bearer <api-key>  # if auth enabled
```

### List Tools
```bash
GET /mcp/sse/tools
```

### List Resources
```bash
GET /mcp/sse/resources
```

### List Prompts
```bash
GET /mcp/sse/prompts
```

## 🔐 Security Setup

### Development (No Auth)
```bash
MCP_ENABLED=true
MCP_REQUIRE_AUTH=false
```

### Production (With Auth)
```bash
MCP_ENABLED=true
MCP_REQUIRE_AUTH=true
MCP_API_KEY=your-secret-key-here
```

## 🧪 Testing

### Python Client
```python
import httpx
import json

with httpx.stream("GET", "http://localhost:8000/mcp/sse") as r:
    for line in r.iter_lines():
        if line.startswith("data:"):
            print(json.loads(line[5:]))
```

### JavaScript Client
```javascript
const es = new EventSource('http://localhost:8000/mcp/sse');
es.addEventListener('server_info', (e) => {
    console.log('Info:', JSON.parse(e.data));
});
```

### cURL Test
```bash
# Stream events
curl -N http://localhost:8000/mcp/sse

# With authentication
curl -N -H "Authorization: Bearer your-key" \
  http://localhost:8000/mcp/sse
```

## 🛠️ Custom Capabilities

### Register Tool
```python
from core.mcp_server import get_mcp_server, MCPTool

mcp_server = get_mcp_server()
mcp_server.register_tool(MCPTool(
    name="my_tool",
    description="My custom tool",
    input_schema={"type": "object", "properties": {...}}
))
```

### Register Resource
```python
from core.mcp_server import MCPResource

mcp_server.register_resource(MCPResource(
    uri="api://my/resource",
    name="My Resource",
    description="Custom resource"
))
```

## 📚 Full Documentation

See [MCP_SSE_SERVER.md](MCP_SSE_SERVER.md) for complete documentation.

