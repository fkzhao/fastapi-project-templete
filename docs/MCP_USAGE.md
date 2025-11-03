# MCP SSE Server - Quick Usage Guide

## 🎯 MCP Protocol Support

The MCP SSE server supports two communication methods:

1. **GET** - For Server-Sent Events (SSE) streaming
2. **POST** - For MCP protocol messages (JSON-RPC)

## ✅ Correct Usage

### 1. Enable MCP Server

In `.env` file:
```bash
MCP_ENABLED=true
```

### 2. SSE Streaming (GET Method)

For real-time event streaming:

#### Using cURL
```bash
# Connect to SSE stream
curl -N http://localhost:8000/mcp/sse

# With authentication
curl -N -H "Authorization: Bearer your-api-key" http://localhost:8000/mcp/sse
```

#### Using JavaScript
```javascript
// EventSource uses GET automatically
const eventSource = new EventSource('http://localhost:8000/mcp/sse');

eventSource.addEventListener('server_info', (e) => {
    console.log('Server info:', JSON.parse(e.data));
});

eventSource.addEventListener('ping', (e) => {
    console.log('Ping:', JSON.parse(e.data));
});
```

### 3. MCP Protocol Messages (POST Method)

For MCP JSON-RPC protocol messages:

#### Initialize
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'
```

#### List Tools
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

#### Call Tool
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_user_info",
      "arguments": {
        "user_id": 123
      }
    }
  }'
```

#### List Resources
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "resources/list",
    "params": {}
  }'
```

#### Read Resource
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "resources/read",
    "params": {
      "uri": "api://users/list"
    }
  }'
```

#### List Prompts
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "prompts/list",
    "params": {}
  }'
```

#### Get Prompt
```bash
curl -X POST http://localhost:8000/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "prompts/get",
    "params": {
      "name": "summarize_user",
      "arguments": {
        "user_id": 123
      }
    }
  }'
```

### 4. Python Client Example

```python
import httpx
import json

# For POST requests (MCP protocol)
def call_mcp_method(method, params=None):
    response = httpx.post(
        "http://localhost:8000/mcp/sse",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
    )
    return response.json()

# Initialize
result = call_mcp_method("initialize")
print("Server info:", result)

# List tools
tools = call_mcp_method("tools/list")
print("Available tools:", tools)

# Call a tool
tool_result = call_mcp_method("tools/call", {
    "name": "get_user_info",
    "arguments": {"user_id": 123}
})
print("Tool result:", tool_result)

# For SSE streaming (GET)
with httpx.stream("GET", "http://localhost:8000/mcp/sse") as response:
    for line in response.iter_lines():
        if line.startswith("data:"):
            print(line)
```

### 5. Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/sse` | SSE stream connection ✅ |
| POST | `/mcp/sse` | MCP protocol messages (JSON-RPC) ✅ |
| GET | `/mcp/sse/info` | Server information |
| GET | `/mcp/sse/tools` | List available tools |
| GET | `/mcp/sse/resources` | List available resources |
| GET | `/mcp/sse/prompts` | List available prompts |

## 📋 Supported MCP Methods

| Method | Description | Params |
|--------|-------------|--------|
| `initialize` | Initialize MCP session | None |
| `tools/list` | List available tools | None |
| `tools/call` | Execute a tool | `name`, `arguments` |
| `resources/list` | List available resources | None |
| `resources/read` | Read a resource | `uri` |
| `prompts/list` | List available prompts | None |
| `prompts/get` | Get a prompt | `name`, `arguments` |

## 🔧 Configuration

```bash
# Enable MCP
MCP_ENABLED=true

# Custom endpoint (optional)
MCP_ENDPOINT=/mcp/sse

# Enable authentication (recommended for production)
MCP_REQUIRE_AUTH=true
MCP_API_KEY=your-secret-key

# Features
MCP_ENABLE_TOOLS=true
MCP_ENABLE_RESOURCES=true
MCP_ENABLE_PROMPTS=true
```

## 🐛 Troubleshooting

### Error: POST /mcp/sse returns 405
- **Cause**: Using POST instead of GET
- **Fix**: Use GET method for SSE connections

### Error: Connection closes immediately
- **Cause**: Client not handling SSE correctly
- **Fix**: Use EventSource or streaming GET with proper headers

### Error: 401 Unauthorized
- **Cause**: Authentication required but no API key provided
- **Fix**: Add `Authorization: Bearer <api-key>` header

## 📚 What is Server-Sent Events (SSE)?

SSE is a server push technology that allows a server to push data to clients over HTTP.

**Key Points**:
- Uses GET method (not POST)
- Unidirectional (server → client)
- Automatic reconnection
- Text-based protocol
- Perfect for real-time updates

## 🔗 More Information

See full documentation: [docs/MCP_SSE_SERVER.md](MCP_SSE_SERVER.md)

