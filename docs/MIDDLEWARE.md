# Middleware Documentation

This document explains all middleware used in the FastAPI application.

## 📚 Available Middleware

### 1. CORS Middleware
**Purpose**: Enable Cross-Origin Resource Sharing  
**File**: `src/core/middleware/cors.py`  
**Order**: First (executed last)

Allows web applications from different origins to access your API.

**Configuration**:
```python
# Environment variable
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"

# Or in cors.py
ALLOW_ORIGINS = ["http://localhost:3000"]
ALLOW_CREDENTIALS = True
ALLOW_METHODS = ["*"]
ALLOW_HEADERS = ["*"]
```

**Headers Added**:
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Credentials`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

---

### 2. Security Headers Middleware
**Purpose**: Add security-related HTTP headers  
**File**: `src/core/middleware/security.py`  
**Order**: Second

Protects against common web vulnerabilities.

**Headers Added**:
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Content-Security-Policy` - Controls resource loading
- `Referrer-Policy` - Controls referrer information
- `Permissions-Policy` - Controls browser features

**Production Note**: Uncomment HSTS header when using HTTPS:
```python
response.headers["Strict-Transport-Security"] = "max-age=31536000"
```

---

### 3. Request ID Middleware
**Purpose**: Add unique identifier to each request  
**File**: `src/core/middleware/request_id.py`  
**Order**: Third

Generates or accepts a unique request ID for tracing.

**Headers**:
- Request: `X-Request-ID` (optional, will be generated if not provided)
- Response: `X-Request-ID` (always added)

**Usage in Route**:
```python
@app.get("/example")
async def example(request: Request):
    request_id = request.state.request_id
    return {"request_id": request_id}
```

---

### 4. Process Time Middleware
**Purpose**: Measure request processing time  
**File**: `src/core/middleware/timing.py`  
**Order**: Fourth

Adds processing time to response headers.

**Headers Added**:
- `X-Process-Time: 123.45ms`

Useful for:
- Performance monitoring
- API optimization
- Identifying slow endpoints

---

### 5. Request Logging Middleware
**Purpose**: Log all HTTP requests and responses  
**File**: `src/core/middleware/log.py`  
**Order**: Fifth

Logs detailed information about each request.

**Logged Information**:
- Request method, path, URL
- Query parameters
- Client IP and User-Agent
- Response status code
- Processing time
- Exceptions and stack traces

**Log Format**:
```
INFO: Request started: GET /user/123
INFO: Request completed: GET /user/123 - 200 (45.23ms)
ERROR: Request processing exception: POST /user - ValueError: Invalid data
```

---

### 6. Audit Log Middleware
**Purpose**: Audit trail for API operations  
**File**: `src/core/middleware/audit.py`  
**Order**: Sixth

Tracks create, update, delete operations for compliance.

**Configuration**:
```python
app.add_middleware(
    AuditLogMiddleware,
    methods=["POST", "PUT", "DELETE", "PATCH"],
    exclude_paths=["/health", "/docs"]
)
```

**Logged Data**:
- User information (if authenticated)
- Request arguments
- Response body
- Operation metadata
- Timestamp and processing time

**Storage**: Currently logs to logger, can be extended to database.

---

### 7. Rate Limiting Middleware (Optional)
**Purpose**: Limit requests per client  
**File**: `src/core/middleware/rate_limit.py`  
**Order**: Seventh

Prevents abuse by limiting request rates.

**Configuration**:
```python
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000
)
```

**Response Headers**:
- `X-RateLimit-Limit-Minute: 60`
- `X-RateLimit-Remaining-Minute: 55`
- `X-RateLimit-Limit-Hour: 1000`
- `X-RateLimit-Remaining-Hour: 950`

**Rate Limit Exceeded**:
```json
{
  "detail": "Rate limit exceeded. Too many requests per minute."
}
```
Status Code: `429 Too Many Requests`

**Production Note**: Use Redis-based rate limiting for distributed systems.

---

### 8. GZip Compression Middleware
**Purpose**: Compress large responses  
**File**: Built-in FastAPI middleware  
**Order**: Eighth

Reduces bandwidth usage by compressing responses.

**Configuration**:
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

Only compresses responses larger than minimum_size (bytes).

---

### 9. Trusted Host Middleware (Production)
**Purpose**: Validate Host header  
**File**: Built-in FastAPI middleware  
**Order**: Last (commented out by default)

Protects against Host header attacks.

**Configuration**:
```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.yourdomain.com"]
)
```

**Enable in Production** to prevent:
- Host header injection
- Cache poisoning
- Password reset poisoning

---

## 🔄 Middleware Execution Order

Middleware is executed in **LIFO order** (Last In, First Out):

```
Request Flow:
Client → CORS → Security → RequestID → Timing → Logging → Audit → RateLimit → GZip → Handler

Response Flow:
Handler → GZip → RateLimit → Audit → Logging → Timing → RequestID → Security → CORS → Client
```

## 🎯 Best Practices

### 1. Enable Only What You Need
Comment out middleware you don't need to improve performance:
```python
# app.add_middleware(RateLimitMiddleware)  # Disabled for development
```

### 2. Configure for Environment
Use environment variables for configuration:
```python
import os

ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true"
if ENABLE_RATE_LIMIT:
    app.add_middleware(RateLimitMiddleware)
```

### 3. Monitor Performance
Use Process Time headers to identify slow middleware:
```bash
curl -i http://localhost:8000/api/endpoint
# Look for: X-Process-Time: 123.45ms
```

### 4. Security in Production
Enable security middleware in production:
```python
# Production only
if os.getenv("ENV") == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
    # Enable HSTS in SecurityHeadersMiddleware
```

### 5. Customize for Your Needs
Extend or modify middleware:
```python
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Your custom logic here
        response = await call_next(request)
        return response
```

## 📊 Monitoring

### View Request IDs
```bash
curl -i http://localhost:8000/health
# Response includes: X-Request-ID: 123e4567-e89b-12d3-a456-426614174000
```

### Check Processing Time
```bash
curl -i http://localhost:8000/user/1
# Response includes: X-Process-Time: 45.23ms
```

### Check Rate Limits
```bash
curl -i http://localhost:8000/api/endpoint
# Response includes:
# X-RateLimit-Remaining-Minute: 55
# X-RateLimit-Remaining-Hour: 995
```

## 🔧 Troubleshooting

### CORS Issues
If getting CORS errors:
1. Check `CORS_ORIGINS` environment variable
2. Verify origin is in allowed list
3. Check browser console for specific error

### Rate Limit False Positives
If rate limiting is too aggressive:
1. Increase limits in middleware configuration
2. Exempt specific paths
3. Use Redis for accurate distributed rate limiting

### Performance Issues
If middleware causes slowdown:
1. Check `X-Process-Time` headers
2. Disable non-essential middleware
3. Optimize custom middleware logic
4. Use async operations

### Logging Issues
If logs are not appearing:
1. Check logging configuration
2. Verify LogContext is properly initialized
3. Check log level settings

## 📚 References

- [Starlette Middleware](https://www.starlette.io/middleware/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)

---

**Last Updated**: October 28, 2025

