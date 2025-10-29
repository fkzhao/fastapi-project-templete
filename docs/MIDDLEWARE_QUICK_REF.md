# Middleware Configuration Quick Reference

## 🚀 Quick Start

1. **Copy example configuration**:
   ```bash
   cp .env.middleware.example .env
   ```

2. **Edit configuration**:
   ```bash
   nano .env
   ```

3. **Start application**:
   ```bash
   uvicorn main:app --reload
   ```

## ⚡ Quick Configuration Examples

### Minimal (Development)
```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=http://localhost:3000
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_GZIP_ENABLED=true
```

### Recommended (Production)
```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=https://yourdomain.com
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=true
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true
MIDDLEWARE_AUDIT_LOG_ENABLED=true
MIDDLEWARE_RATE_LIMIT_ENABLED=true
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ALLOWED=yourdomain.com
```

### Maximum Security
```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=https://yourdomain.com
MIDDLEWARE_CORS_CREDENTIALS=false
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=true
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_PROCESS_TIME_ENABLED=true
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true
MIDDLEWARE_AUDIT_LOG_ENABLED=true
MIDDLEWARE_AUDIT_LOG_METHODS=POST,PUT,DELETE,PATCH,GET
MIDDLEWARE_RATE_LIMIT_ENABLED=true
MIDDLEWARE_RATE_LIMIT_PER_MINUTE=30
MIDDLEWARE_RATE_LIMIT_PER_HOUR=500
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ALLOWED=yourdomain.com
```

## 📋 All Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MIDDLEWARE_CORS_ENABLED` | `true` | Enable CORS |
| `MIDDLEWARE_CORS_ORIGINS` | `localhost:3000,...` | Allowed origins (comma-separated) |
| `MIDDLEWARE_CORS_CREDENTIALS` | `true` | Allow credentials |
| `MIDDLEWARE_CORS_METHODS` | `*` | Allowed methods |
| `MIDDLEWARE_CORS_HEADERS` | `*` | Allowed headers |
| `MIDDLEWARE_SECURITY_HEADERS_ENABLED` | `true` | Enable security headers |
| `MIDDLEWARE_SECURITY_HSTS_ENABLED` | `false` | Enable HSTS |
| `MIDDLEWARE_REQUEST_ID_ENABLED` | `true` | Enable request ID |
| `MIDDLEWARE_PROCESS_TIME_ENABLED` | `true` | Enable process time |
| `MIDDLEWARE_REQUEST_LOGGING_ENABLED` | `true` | Enable request logging |
| `MIDDLEWARE_AUDIT_LOG_ENABLED` | `true` | Enable audit logging |
| `MIDDLEWARE_AUDIT_LOG_METHODS` | `POST,PUT,DELETE,PATCH` | Methods to audit |
| `MIDDLEWARE_AUDIT_LOG_EXCLUDE_PATHS` | `/health,/docs,...` | Paths to exclude |
| `MIDDLEWARE_RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `MIDDLEWARE_RATE_LIMIT_PER_MINUTE` | `60` | Requests per minute |
| `MIDDLEWARE_RATE_LIMIT_PER_HOUR` | `1000` | Requests per hour |
| `MIDDLEWARE_GZIP_ENABLED` | `true` | Enable compression |
| `MIDDLEWARE_GZIP_MINIMUM_SIZE` | `1000` | Min size to compress |
| `MIDDLEWARE_TRUSTED_HOST_ENABLED` | `false` | Enable host validation |
| `MIDDLEWARE_TRUSTED_HOST_ALLOWED` | `localhost,127.0.0.1` | Allowed hosts |

## 🔍 Testing Configuration

```bash
# Check if middleware is loaded
curl -i http://localhost:8000/health

# You should see headers like:
# X-Request-ID: abc-123-def
# X-Process-Time: 12.34ms
# Access-Control-Allow-Origin: *
```

## 📚 Full Documentation

See [MIDDLEWARE_CONFIG.md](MIDDLEWARE_CONFIG.md) for complete documentation.

