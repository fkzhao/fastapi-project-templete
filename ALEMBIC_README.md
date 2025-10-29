# Alembic Database Migrations Guide

This guide explains how to use Alembic for database migrations in this FastAPI project.

## 📋 What is Alembic?

Alembic is a database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes over time
- Apply or rollback schema changes
- Auto-generate migration scripts from model changes
- Maintain database version control

## 🚀 Quick Start

### 1. Create a New Migration

After modifying your models, generate a migration:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add email field to User model"

# Create empty migration (for manual changes)
alembic revision -m "Add custom index"
```

### 2. Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply one migration at a time
alembic upgrade +1

# Apply to specific revision
alembic upgrade <revision_id>
```

### 3. Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### 4. Check Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## 📁 Project Structure

```
.
├── alembic/
│   ├── versions/          # Migration scripts
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Migration script template
│   └── README            # Alembic README
├── alembic.ini           # Alembic configuration
└── src/
    └── models/           # Your SQLAlchemy models
```

## 🔧 Configuration

### Database URL

Set in `alembic.ini`:
```ini
sqlalchemy.url = sqlite:///./database.db
```

Or use environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

### Import Models

All models are imported in `alembic/env.py`:
```python
from models.base import Base
from models.user import User
from models.product import Product

target_metadata = Base.metadata
```

## 📝 Common Workflows

### Adding a New Model

1. Create the model in `src/models/`:
```python
# src/models/order.py
from sqlalchemy import Column, Integer, String
from .base import BaseModel

class Order(BaseModel):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True)
```

2. Import in `alembic/env.py`:
```python
from models.order import Order
```

3. Generate migration:
```bash
alembic revision --autogenerate -m "Add Order model"
```

4. Review the generated migration in `alembic/versions/`

5. Apply migration:
```bash
alembic upgrade head
```

### Modifying an Existing Model

1. Update the model:
```python
# Add a new field
email = Column(String(100), nullable=True)
```

2. Generate migration:
```bash
alembic revision --autogenerate -m "Add email to User"
```

3. Review and apply:
```bash
# Review the migration file
cat alembic/versions/<revision>_add_email_to_user.py

# Apply it
alembic upgrade head
```

### Data Migrations

For complex data transformations, edit the migration manually:

```python
def upgrade():
    # Schema changes
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    
    # Data migration
    conn = op.get_bind()
    conn.execute(
        "UPDATE users SET full_name = name || ' ' || nick_name"
    )

def downgrade():
    op.drop_column('users', 'full_name')
```

## 🐛 Troubleshooting

### Migration Not Detected

If autogenerate doesn't detect your changes:

1. Make sure model is imported in `alembic/env.py`
2. Check that the model inherits from `Base`
3. Verify `target_metadata` is set correctly

### Import Errors

If you get `ModuleNotFoundError`:

1. Check `sys.path` in `alembic/env.py`
2. Ensure all imports use absolute paths from `src`
3. Run from project root directory

### Database Already Has Tables

If tables exist without migrations:

```bash
# Stamp database with current schema (be careful!)
alembic stamp head
```

### Merge Conflicts in Migrations

If multiple developers create migrations:

```bash
# Create merge migration
alembic merge -m "Merge migrations" <rev1> <rev2>
```

## 🔐 Production Best Practices

### 1. Review Migrations

Always review auto-generated migrations:
- Check for unintended changes
- Verify data won't be lost
- Add data migrations if needed

### 2. Test Migrations

Test both upgrade and downgrade:
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test re-upgrade
alembic upgrade head
```

### 3. Backup Before Migrations

```bash
# For SQLite
cp database.db database.db.backup

# For PostgreSQL
pg_dump dbname > backup.sql
```

### 4. Run Migrations in CI/CD

Add to your deployment script:
```bash
#!/bin/bash
# Apply migrations before starting app
alembic upgrade head

# Start application
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Use Transaction Per Migration

In `alembic/env.py`:
```python
def run_migrations_online():
    # ...
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transaction_per_migration=True  # Rollback on error
        )
```

## 📊 Migration Best Practices

### DO ✅

- Create descriptive migration messages
- Review auto-generated migrations
- Test migrations locally first
- Keep migrations small and focused
- Add comments for complex changes
- Version control all migrations
- Backup before production migrations

### DON'T ❌

- Edit applied migrations
- Delete migration files
- Skip reviewing auto-generated code
- Run migrations without backups
- Use raw SQL without fallbacks
- Ignore migration order

## 🔄 Docker Integration

### Dockerfile Update

Add migration step:
```dockerfile
# Copy alembic configuration
COPY alembic.ini ./
COPY alembic ./alembic

# Run migrations on container start
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```yaml
services:
  app:
    build: .
    command: >
      sh -c "alembic upgrade head &&
             uvicorn main:app --host 0.0.0.0 --port 8000"
```

### Separate Migration Service

```yaml
services:
  migrate:
    build: .
    command: alembic upgrade head
    depends_on:
      - postgres
  
  app:
    build: .
    depends_on:
      migrate:
        condition: service_completed_successfully
```

## 📚 Useful Commands Cheat Sheet

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head                    # Apply all
alembic upgrade +1                      # Apply one
alembic upgrade <revision>              # Apply to specific

# Rollback migrations  
alembic downgrade -1                    # Rollback one
alembic downgrade base                  # Rollback all
alembic downgrade <revision>            # Rollback to specific

# Information
alembic current                         # Current revision
alembic history                         # Migration history
alembic history --verbose               # Detailed history
alembic show <revision>                 # Show specific migration

# Branching
alembic branches                        # Show branches
alembic merge <rev1> <rev2>            # Merge branches

# Maintenance
alembic stamp head                      # Mark DB as up to date
alembic stamp <revision>                # Mark at specific revision
alembic check                           # Check if models match DB
```

## 🎯 Example Workflow

Complete example of adding a new field:

```bash
# 1. Update model
# Edit src/models/user.py, add: phone = Column(String(20))

# 2. Generate migration
alembic revision --autogenerate -m "Add phone field to User"

# 3. Review migration
cat alembic/versions/*_add_phone_field_to_user.py

# 4. Apply migration
alembic upgrade head

# 5. Verify
alembic current

# 6. Test rollback (optional)
alembic downgrade -1
alembic upgrade head
```

## 📞 Support

For more information:
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Project Issues](https://github.com/fkzhao/fastapi-project-templete/issues)

---

**Remember**: Always backup your database before running migrations in production! 🛡️

