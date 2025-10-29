# MCP SSE Server - Quick Usage Guide

## 🔴 Common Error: 405 Method Not Allowed

If you see this error:
```
127.0.0.1:55033 - "POST /mcp/sse HTTP/1.1" 405
```

**Problem**: You're using POST method, but MCP SSE requires GET.

**Solution**: Use GET method for Server-Sent Events connection.

## ✅ Correct Usage

### 1. Enable MCP Server

In `.env` file:
```bash
MCP_ENABLED=true
```

### 2. Connect with GET Method

#### Using cURL
```bash
# Correct - use GET
curl -N http://localhost:8000/mcp/sse

# With authentication
curl -N -H "Authorization: Bearer your-api-key" http://localhost:8000/mcp/sse
```

#### Using Python
```python
import httpx

# Correct - streaming GET request
with httpx.stream("GET", "http://localhost:8000/mcp/sse") as response:
    for line in response.iter_lines():
        if line.startswith("data:"):
            print(line)
```

#### Using JavaScript
```javascript
// Correct - EventSource uses GET automatically
const eventSource = new EventSource('http://localhost:8000/mcp/sse');

eventSource.addEventListener('server_info', (e) => {
    console.log('Server info:', JSON.parse(e.data));
});

eventSource.addEventListener('ping', (e) => {
    console.log('Ping:', JSON.parse(e.data));
});
```

### 3. Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/sse` | SSE stream connection ✅ |
| GET | `/mcp/sse/info` | Server information |
| GET | `/mcp/sse/tools` | List available tools |
| GET | `/mcp/sse/resources` | List available resources |
| GET | `/mcp/sse/prompts` | List available prompts |
| POST | `/mcp/sse` | ❌ Not allowed - returns error |

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

See full documentation: [docs/MCP_SSE_SERVER.md](./docs/MCP_SSE_SERVER.md)

