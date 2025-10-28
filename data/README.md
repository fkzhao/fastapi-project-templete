# Data Directory

This directory contains application data files and databases.

## Contents

- **SQLite Databases**: Local database files (*.db, *.sqlite)
- **Uploaded Files**: User-uploaded content
- **Cache Files**: Temporary data and cache
- **Logs**: Application log files (if configured)

## .gitignore

This directory is git-ignored to prevent committing sensitive or large data files to version control.

Only this README is tracked.

## Local Development

For local development, database files will be created here automatically:
- `database.db` - Main application database
- `analytics.db` - Analytics database (if using multiple databases)

## Production

In production:
- Use proper database servers (PostgreSQL, MySQL, etc.)
- Mount this directory as a volume for persistent storage
- Ensure proper backup procedures are in place

## Docker

When using Docker, mount this directory:
```yaml
volumes:
  - ./data:/app/data
```

## Backup

Remember to backup this directory regularly in production:
```bash
# Example backup script
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

---

**Note**: Never commit sensitive data or large files to git!

