# FastAPI Project Template

A production-ready FastAPI project template with modern Python development practices, Docker support, and comprehensive examples.

## 🚀 Features

- **FastAPI Framework**: High-performance async web framework
- **SQLAlchemy ORM**: Database models with Alembic migrations
- **Alembic Migrations**: Full database schema versioning and migration support
- **Pydantic Schemas**: Request/response validation and serialization
- **Admin Panel**: SQLAdmin integration for easy data management
- **Multiple Database Support**: Configure multiple database connections
- **Docker Ready**: Complete Docker and docker-compose setup
- **Type Hints**: Full type annotation throughout the codebase
- **Testing**: Pytest configuration and examples
- **Modular Architecture**: Clean separation of concerns

## 📁 Project Structure

```
.
├── src/
│   ├── admin/              # Admin panel views
│   ├── core/               # Core functionality (database, middleware, etc.)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic schemas for validation
│   ├── router/             # API route handlers
│   ├── services/           # Business logic layer
│   ├── utils/              # Utility functions
│   ├── app_factory.py      # Application factory
│   └── main.py             # Application entry point
├── test/                   # Test files
├── Dockerfile              # Docker image definition
├── docker-compose.yaml     # Multi-container orchestration
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## 🛠️ Quick Start

### Local Development

1. **Install dependencies** (using uv):
   ```bash
   pip install uv
   uv sync
   ```

2. **Run the application**:
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Run database migrations**:
   ```bash
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Admin Panel: http://localhost:8000/admin
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Or use the Makefile**:
   ```bash
   make build    # Build image
   make up       # Start services
   make logs     # View logs
   make down     # Stop services
   ```

3. **Or use the build script**:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

See [DOCKER_README.md](DOCKER_README.md) for detailed Docker instructions.

## 📚 Documentation

- [Alembic Migrations](ALEMBIC_README.md) - Database migration guide
- [Schemas Documentation](SCHEMAS_README.md) - Pydantic schemas guide
- [Docker Documentation](DOCKER_README.md) - Docker deployment guide

## 🎯 API Endpoints

### User Management
- `POST /user/` - Create a new user
- `GET /user/{user_id}` - Get user by ID
- `PUT /user/{user_id}` - Update user
- `DELETE /user/{user_id}` - Delete user
- `GET /user/` - List users with pagination

### Product Management
- `POST /product/` - Create a new product
- `GET /product/{product_id}` - Get product by ID
- `PUT /product/{product_id}` - Update product
- `DELETE /product/{product_id}` - Delete product
- `GET /product/` - List products with pagination

### Admin Panel
- `/admin` - Admin dashboard (default credentials: admin/123456)

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL_DEFAULT=sqlite:///./data/database.db
DATABASE_URL_ANALYTICS=sqlite:///./data/analytics.db

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password

# Application
DEBUG=false
LOG_LEVEL=INFO
```

### Database Configuration

Multiple databases are supported. Configure in `src/core/database.py`:

```python
DATABASES = ["default", "analytics"]
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

## 📦 Dependencies

Main dependencies:
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM
- Alembic - Database migrations
- Pydantic - Data validation
- SQLAdmin - Admin panel
- pytest - Testing framework

See `pyproject.toml` for complete list.

## 🏗️ Architecture

### Models (SQLAlchemy)
Database table definitions in `src/models/`

### Schemas (Pydantic)
Request/response validation in `src/schemas/`

### Routers
API endpoints in `src/router/`

### Services
Business logic in `src/services/`

### Core
- Database connections
- Middleware
- Exception handlers
- Configuration

## 🔐 Security Features

- Non-root Docker user
- Environment variable configuration
- Admin authentication
- CORS middleware ready
- Input validation with Pydantic
- SQL injection prevention with ORM

## 📈 Production Ready

- Health check endpoint
- Docker multi-stage builds
- Logging configuration
- Error handling
- Database connection pooling
- Automatic API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAdmin](https://aminalaee.dev/sqladmin/)

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/fkzhao/fastapi-project-templete/issues

---

**Happy Coding! 🚀**

