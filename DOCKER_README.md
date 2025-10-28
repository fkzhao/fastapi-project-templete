# Docker Deployment Guide

This guide explains how to build and deploy the FastAPI application using Docker.

## 📋 Prerequisites

- Docker (>= 20.10)
- Docker Compose (>= 2.0)
- bash (for build.sh script)

## 🚀 Quick Start

### 1. Build the Docker Image

Using the build script (recommended):
```bash
chmod +x build.sh
./build.sh
```

Or manually with Docker:
```bash
docker build -t fastapi-app:latest .
```

### 2. Run with Docker Compose

Start all services:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f fastapi-app
```

Stop services:
```bash
docker-compose down
```

### 3. Run Single Container

```bash
docker run -d \
  -p 8000:8000 \
  --name fastapi-app \
  -v $(pwd)/data:/app/data \
  fastapi-app:latest
```

## 🛠️ Build Script Options

The `build.sh` script supports several options:

```bash
# Build with custom tag
./build.sh -t v1.0.0

# Build with custom name
./build.sh -n my-fastapi-app

# Build without cache
./build.sh --no-cache

# Combine options
./build.sh -t v1.0.0 -n my-fastapi-app --no-cache

# Show help
./build.sh --help
```

## 📁 Project Structure

```
.
├── Dockerfile              # Docker image definition
├── docker-compose.yaml     # Multi-container orchestration
├── .dockerignore          # Files to exclude from build
├── build.sh               # Build automation script
└── src/                   # Application source code
```

## 🔧 Configuration

### Environment Variables

Set these in `docker-compose.yaml` or pass them to `docker run`:

```yaml
environment:
  - DATABASE_URL_DEFAULT=sqlite:///./database.db
  - DATABASE_URL_ANALYTICS=sqlite:///./analytics.db
  - PYTHONPATH=/app
```

### Volumes

Data persistence is configured via volumes:

- `./src:/app/src` - Source code (for development)
- `./data:/app/data` - Data files
- `app-data:/app` - Application data

## 🔌 Optional Services

The `docker-compose.yaml` includes commented-out configurations for:

### PostgreSQL Database

Uncomment the postgres service in `docker-compose.yaml`:
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_USER=fastapi
    - POSTGRES_PASSWORD=fastapi123
    - POSTGRES_DB=fastapi_db
  ports:
    - "5432:5432"
```

Then update your environment variables:
```bash
DATABASE_URL_DEFAULT=postgresql://fastapi:fastapi123@postgres:5432/fastapi_db
```

### Redis Cache

Uncomment the redis service in `docker-compose.yaml`:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

### Nginx Reverse Proxy

Uncomment the nginx service and create `nginx.conf`:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
```

## 📊 Monitoring

### Health Check

The container includes a health check endpoint:
```bash
curl http://localhost:8000/health
```

### Container Status

```bash
# Check container health
docker ps

# View detailed container info
docker inspect fastapi-app

# Monitor resource usage
docker stats fastapi-app
```

## 🐛 Troubleshooting

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs fastapi-app

# Last 100 lines
docker-compose logs --tail=100 fastapi-app
```

### Access Container Shell

```bash
docker exec -it fastapi-app /bin/bash
```

### Restart Service

```bash
docker-compose restart fastapi-app
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove images
docker rmi fastapi-app:latest
```

## 🚢 Production Deployment

### 1. Multi-stage Build (Optional)

For smaller images, modify Dockerfile to use multi-stage builds.

### 2. Push to Registry

```bash
# Tag for registry
docker tag fastapi-app:latest myregistry.com/fastapi-app:latest

# Push to registry
docker push myregistry.com/fastapi-app:latest
```

### 3. Deploy to Server

```bash
# On production server
docker pull myregistry.com/fastapi-app:latest
docker-compose up -d
```

### 4. Use Docker Secrets

For production, use Docker secrets for sensitive data:
```bash
echo "my-secret-password" | docker secret create db_password -
```

## 🔐 Security Best Practices

1. **Non-root User**: Container runs as `appuser` (UID 1000)
2. **No Cache**: Sensitive data not cached during build
3. **Environment Variables**: Use for configuration
4. **Secrets Management**: Use Docker secrets or env files
5. **Network Isolation**: Services on private network
6. **Health Checks**: Automatic container health monitoring

## 📈 Performance Optimization

1. **Use .dockerignore**: Reduces build context size
2. **Layer Caching**: Order Dockerfile commands properly
3. **Multi-stage Builds**: Reduce final image size
4. **Volume Mounts**: Fast development with hot reload
5. **Resource Limits**: Set CPU/memory limits in compose

## 🔄 Development Workflow

### Hot Reload Development

Modify `docker-compose.yaml` to enable hot reload:
```yaml
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
volumes:
  - ./src:/app/src:ro
```

### Rebuild After Changes

```bash
# Rebuild specific service
docker-compose build fastapi-app

# Rebuild and restart
docker-compose up -d --build fastapi-app
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Best Practices for Python in Docker](https://docs.docker.com/language/python/build-images/)

## 🆘 Common Issues

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
# Make script executable
chmod +x build.sh

# Fix file permissions
sudo chown -R $USER:$USER .
```

### Out of Disk Space
```bash
# Clean up unused images
docker image prune -a

# Clean up everything
docker system prune -a --volumes
```

---

**Need help?** Open an issue or check the logs with `docker-compose logs -f`

