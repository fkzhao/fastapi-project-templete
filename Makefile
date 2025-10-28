.PHONY: help build build-prod up down restart logs shell test clean prune migrate migrate-create migrate-downgrade migrate-history

# Default target
help:
	@echo "FastAPI Docker Commands"
	@echo "======================="
	@echo "build         - Build Docker image for development"
	@echo "build-prod    - Build Docker image for production"
	@echo "up            - Start all services"
	@echo "down          - Stop all services"
	@echo "restart       - Restart all services"
	@echo "logs          - View logs (follow mode)"
	@echo "shell         - Access container shell"
	@echo "test          - Run tests inside container"
	@echo "clean         - Remove containers and volumes"
	@echo "prune         - Clean up Docker system"
	@echo "ps            - List running containers"
	@echo "health        - Check application health"
	@echo ""
	@echo "Database Migration Commands"
	@echo "==========================="
	@echo "migrate       - Apply all pending migrations"
	@echo "migrate-create - Create a new migration"
	@echo "migrate-down  - Rollback last migration"
	@echo "migrate-history - Show migration history"

# Build development image
build:
	@echo "Building development image..."
	docker-compose build

# Build production image
build-prod:
	@echo "Building production image..."
	docker build -f Dockerfile.production -t fastapi-app:production .

# Start services
up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Services started. Check status with 'make ps'"

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Access container shell
shell:
	docker-compose exec fastapi-app /bin/bash

# Run tests
test:
	docker-compose exec fastapi-app pytest

# List running containers
ps:
	docker-compose ps

# Check health
health:
	@curl -f http://localhost:8000/health && echo "\n✓ Application is healthy" || echo "\n✗ Application is not healthy"

# Clean up
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "Cleanup complete"

# Prune Docker system
prune:
	@echo "Cleaning up Docker system..."
	docker system prune -af --volumes
	@echo "Docker system cleaned"

# Rebuild and restart
rebuild: down build up

# Production deployment
deploy-prod: build-prod
	@echo "Deploying production image..."
	docker run -d \
		-p 8000:8000 \
		--name fastapi-app-prod \
		--restart unless-stopped \
		fastapi-app:production

# Database migration commands
migrate:
	@echo "Applying migrations..."
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	@echo "Rolling back last migration..."
	alembic downgrade -1

migrate-history:
	@echo "Migration history:"
	alembic history --verbose

migrate-current:
	@echo "Current migration:"
	alembic current

