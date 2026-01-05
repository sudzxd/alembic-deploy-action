---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Description

A clear description of the bug.

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Workflow Configuration

```yaml
- uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
    # ... other inputs
```

## Action Output

```
Paste relevant action logs here
```

## Environment

- Database: (PostgreSQL 14, MySQL 8.0, etc.)
- Alembic version: (from your requirements)
- Action version: (e.g., v1.0.0)

## Additional Context

Any other information that might be helpful.
