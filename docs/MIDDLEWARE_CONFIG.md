# Middleware Configuration Guide

This guide explains how to configure middleware using environment variables and the centralized configuration system.

## 📋 Overview

All middleware in this application is controlled through a centralized configuration system located in `src/core/middleware_config.py`. This allows you to:

- ✅ Enable/disable any middleware
- ✅ Configure middleware parameters
- ✅ Use environment variables for different environments
- ✅ Maintain default values for quick setup

## 🔧 Configuration Methods

### Method 1: Environment Variables (Recommended)

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.middleware.example .env

# Edit with your settings
nano .env
```

### Method 2: System Environment Variables

```bash
export MIDDLEWARE_CORS_ENABLED=true
export MIDDLEWARE_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
```

### Method 3: Docker Environment

In `docker-compose.yaml`:

```yaml
services:
  app:
    environment:
      - MIDDLEWARE_CORS_ENABLED=true
      - MIDDLEWARE_CORS_ORIGINS=http://localhost:3000
      - MIDDLEWARE_RATE_LIMIT_ENABLED=true
```

### Method 4: Modify Default Values

Edit `src/core/middleware_config.py` to change default values.

## ⚙️ Available Configuration Options

### CORS Middleware

```bash
MIDDLEWARE_CORS_ENABLED=true                    # Enable/disable CORS
MIDDLEWARE_CORS_ORIGINS=http://localhost:3000   # Comma-separated list
MIDDLEWARE_CORS_CREDENTIALS=true                # Allow credentials
MIDDLEWARE_CORS_METHODS=*                       # Allowed methods
MIDDLEWARE_CORS_HEADERS=*                       # Allowed headers
MIDDLEWARE_CORS_MAX_AGE=600                     # Preflight cache duration
```

**Example**:
```bash
# Production CORS settings
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MIDDLEWARE_CORS_CREDENTIALS=true
```

---

### Security Headers Middleware

```bash
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true   # Enable security headers
MIDDLEWARE_SECURITY_HSTS_ENABLED=false     # Enable HSTS (HTTPS only!)
MIDDLEWARE_SECURITY_HSTS_MAX_AGE=31536000  # HSTS duration (1 year)
```

**⚠️ Important**: Only enable HSTS in production with valid HTTPS!

**Example**:
```bash
# Production security settings
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_MAX_AGE=31536000
```

---

### Request ID Middleware

```bash
MIDDLEWARE_REQUEST_ID_ENABLED=true  # Add unique ID to each request
```

**Headers Added**:
- Response: `X-Request-ID`

---

### Process Time Middleware

```bash
MIDDLEWARE_PROCESS_TIME_ENABLED=true  # Measure processing time
```

**Headers Added**:
- Response: `X-Process-Time: 45.23ms`

---

### Request Logging Middleware

```bash
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true  # Log all requests
```

**Logs Include**:
- Request method, path, URL
- Client IP and User-Agent
- Response status and processing time
- Exceptions with stack traces

---

### Audit Log Middleware

```bash
MIDDLEWARE_AUDIT_LOG_ENABLED=true                          # Enable audit logging
MIDDLEWARE_AUDIT_LOG_METHODS=POST,PUT,DELETE,PATCH        # Methods to audit
MIDDLEWARE_AUDIT_LOG_EXCLUDE_PATHS=/health,/docs,/redoc   # Paths to exclude
```

**Example**:
```bash
# Audit all modifications
MIDDLEWARE_AUDIT_LOG_ENABLED=true
MIDDLEWARE_AUDIT_LOG_METHODS=POST,PUT,DELETE,PATCH
MIDDLEWARE_AUDIT_LOG_EXCLUDE_PATHS=/health,/metrics,/docs
```

---

### Rate Limiting Middleware

```bash
MIDDLEWARE_RATE_LIMIT_ENABLED=false        # Enable rate limiting
MIDDLEWARE_RATE_LIMIT_PER_MINUTE=60       # Requests per minute
MIDDLEWARE_RATE_LIMIT_PER_HOUR=1000       # Requests per hour
```

**⚠️ Note**: Uses in-memory storage. For production, consider Redis-based rate limiting.

**Example**:
```bash
# Enable rate limiting for production
MIDDLEWARE_RATE_LIMIT_ENABLED=true
MIDDLEWARE_RATE_LIMIT_PER_MINUTE=100
MIDDLEWARE_RATE_LIMIT_PER_HOUR=5000
```

---

### GZip Compression Middleware

```bash
MIDDLEWARE_GZIP_ENABLED=true         # Enable compression
MIDDLEWARE_GZIP_MINIMUM_SIZE=1000    # Minimum size to compress (bytes)
```

**Example**:
```bash
# Compress all responses > 500 bytes
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_GZIP_MINIMUM_SIZE=500
```

---

### Trusted Host Middleware

```bash
MIDDLEWARE_TRUSTED_HOST_ENABLED=false                    # Enable host validation
MIDDLEWARE_TRUSTED_HOST_ALLOWED=localhost,yourdomain.com # Allowed hosts
```

**⚠️ Important**: Enable in production to prevent Host header attacks!

**Example**:
```bash
# Production host validation
MIDDLEWARE_TRUSTED_HOST_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ALLOWED=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

## 📊 Environment-Specific Configurations

### Development (.env.development)

```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=false
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_PROCESS_TIME_ENABLED=true
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true
MIDDLEWARE_AUDIT_LOG_ENABLED=false
MIDDLEWARE_RATE_LIMIT_ENABLED=false
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=false
```

### Production (.env.production)

```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=true
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_PROCESS_TIME_ENABLED=true
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true
MIDDLEWARE_AUDIT_LOG_ENABLED=true
MIDDLEWARE_RATE_LIMIT_ENABLED=true
MIDDLEWARE_RATE_LIMIT_PER_MINUTE=100
MIDDLEWARE_RATE_LIMIT_PER_HOUR=5000
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ALLOWED=yourdomain.com,www.yourdomain.com
```

## 🎯 Common Use Cases

### 1. Disable Middleware for Testing

```bash
# Disable all optional middleware
MIDDLEWARE_AUDIT_LOG_ENABLED=false
MIDDLEWARE_RATE_LIMIT_ENABLED=false
MIDDLEWARE_REQUEST_LOGGING_ENABLED=false
```

### 2. Enable Only Essential Middleware

```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_PROCESS_TIME_ENABLED=false
MIDDLEWARE_REQUEST_LOGGING_ENABLED=false
MIDDLEWARE_AUDIT_LOG_ENABLED=false
MIDDLEWARE_RATE_LIMIT_ENABLED=false
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=false
```

### 3. Maximum Security Configuration

```bash
MIDDLEWARE_CORS_ENABLED=true
MIDDLEWARE_CORS_ORIGINS=https://yourdomain.com
MIDDLEWARE_SECURITY_HEADERS_ENABLED=true
MIDDLEWARE_SECURITY_HSTS_ENABLED=true
MIDDLEWARE_REQUEST_ID_ENABLED=true
MIDDLEWARE_PROCESS_TIME_ENABLED=true
MIDDLEWARE_REQUEST_LOGGING_ENABLED=true
MIDDLEWARE_AUDIT_LOG_ENABLED=true
MIDDLEWARE_RATE_LIMIT_ENABLED=true
MIDDLEWARE_GZIP_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ENABLED=true
MIDDLEWARE_TRUSTED_HOST_ALLOWED=yourdomain.com
```

## 🔍 Verification

### Check Configuration at Startup

When the application starts, it logs the middleware configuration:

```
INFO: Initializing middleware with configuration:
INFO:   CORS: True
INFO:   Security Headers: True
INFO:   Request ID: True
INFO:   Process Time: True
INFO:   Request Logging: True
INFO:   Audit Log: True
INFO:   Rate Limiting: False
INFO:   GZip: True
INFO:   Trusted Host: False
```

### Test Middleware in Runtime

```bash
# Check CORS headers
curl -I -H "Origin: http://localhost:3000" http://localhost:8000/health

# Check Request ID
curl -i http://localhost:8000/health | grep X-Request-ID

# Check Process Time
curl -i http://localhost:8000/health | grep X-Process-Time

# Check Rate Limiting
for i in {1..100}; do curl -i http://localhost:8000/api/endpoint; done
```

## 🐛 Troubleshooting

### Configuration Not Loading

1. Check `.env` file location (must be in project root)
2. Verify environment variable names (must start with `MIDDLEWARE_`)
3. Check for typos in variable names
4. Restart application after changing `.env`

### CORS Not Working

```bash
# Check CORS is enabled
MIDDLEWARE_CORS_ENABLED=true

# Verify your origin is in the list
MIDDLEWARE_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Check browser console for specific CORS error
```

### Rate Limiting Too Aggressive

```bash
# Increase limits
MIDDLEWARE_RATE_LIMIT_PER_MINUTE=200
MIDDLEWARE_RATE_LIMIT_PER_HOUR=10000

# Or disable for specific testing
MIDDLEWARE_RATE_LIMIT_ENABLED=false
```

## 📚 Code Structure

```
src/
├── core/
│   ├── app.py                    # Middleware initialization logic
│   ├── middleware_config.py      # Configuration definitions
│   └── middleware/               # Middleware implementations
│       ├── __init__.py
│       ├── cors.py
│       ├── security.py
│       ├── request_id.py
│       ├── timing.py
│       ├── log.py
│       ├── audit.py
│       ├── rate_limit.py
│       └── ...
├── app_factory.py                # Application factory
└── ...
```

## 🔄 Adding Custom Middleware

To add custom middleware to the configuration system:

1. **Create the middleware** in `src/core/middleware/`
2. **Add configuration** to `MiddlewareConfig` in `middleware_config.py`
3. **Import and register** in `init_middleware()` in `core/app.py`
4. **Document** in this guide

Example:

```python
# In middleware_config.py
class MiddlewareConfig(BaseSettings):
    # ...existing code...
    custom_middleware_enabled: bool = Field(default=False)
    custom_middleware_param: str = Field(default="value")

# In core/app.py
def init_middleware(app: FastAPI):
    # ...existing code...
    if config.custom_middleware_enabled:
        app.add_middleware(
            CustomMiddleware,
            param=config.custom_middleware_param
        )
```

---

**Last Updated**: October 29, 2025

For more details, see:
- [Middleware Documentation](MIDDLEWARE.md)
- [API Documentation](API.md)

