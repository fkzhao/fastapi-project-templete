# Documentation

This directory contains project documentation and API specifications.

## 📚 Contents

### API Documentation
- **API Specifications**: OpenAPI/Swagger specifications
- **Postman Collections**: API testing collections
- **API Examples**: Request/response examples

### Architecture
- **Architecture Diagrams**: System design and architecture docs
- **Database Schema**: ER diagrams and schema documentation
- **Flow Diagrams**: User flows and business process diagrams

### Development
- **Development Guide**: Setup and development instructions
- **Coding Standards**: Project coding conventions
- **Contributing Guide**: How to contribute to the project

### Deployment
- **Deployment Guide**: Production deployment instructions
- **Infrastructure**: Infrastructure as Code documentation
- **Monitoring**: Monitoring and alerting setup

## 🚀 Quick Links

Main documentation files in project root:
- [README.md](../README.md) - Project overview and quick start
- [ALEMBIC_README.md](ALEMBIC_README.md) - Database migrations guide
- [SCHEMAS_README.md](SCHEMAS_README.md) - Pydantic schemas guide
- [DOCKER_README.md](DOCKER_README.md) - Docker deployment guide

## 📝 Auto-Generated Docs

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Generating Documentation

### API Documentation
FastAPI generates docs automatically from your code:
```python
@app.get("/users/{user_id}", summary="Get user by ID")
async def get_user(user_id: int):
    """
    Retrieve a user by their ID.
    
    - **user_id**: The ID of the user to retrieve
    """
    return {"user_id": user_id}
```

### Database Schema
Generate ER diagrams using tools like:
```bash
# Using SchemaSpy
docker run --rm -v "$PWD:/output" schemaspy/schemaspy:latest

# Using SQLAlchemy
python scripts/generate_schema_diagram.py
```

### Code Documentation
Generate code docs using Sphinx:
```bash
pip install sphinx sphinx-rtd-theme
sphinx-quickstart
sphinx-build -b html docs/source docs/build
```

## 📖 Documentation Standards

### Docstrings
Use Google-style docstrings:
```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When value is invalid
    """
    pass
```

### API Endpoints
Document all endpoints with:
- Summary and description
- Request parameters
- Request body schema
- Response schema
- Status codes
- Examples

### Code Comments
- Explain **why**, not **what**
- Keep comments up-to-date
- Remove commented-out code
- Use TODO/FIXME/NOTE tags

## 🔍 Documentation Tools

Recommended tools:
- **Swagger UI**: Interactive API documentation
- **ReDoc**: Clean API documentation
- **MkDocs**: Project documentation site
- **Sphinx**: Python code documentation
- **draw.io**: Diagrams and flowcharts
- **Mermaid**: Markdown-based diagrams

## 📦 External Documentation

Links to external resources:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## 🤝 Contributing to Docs

When adding new features:
1. Update relevant README files
2. Add docstrings to code
3. Update API examples if needed
4. Create diagrams for complex features
5. Update changelog

---

**Keep documentation up-to-date with code changes!** 📝

