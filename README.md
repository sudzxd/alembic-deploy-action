# Alembic Deploy Action

GitHub Action for safe Alembic database migrations with dry-run preview, validation, and approval workflows.

## Features

- **Dry-Run Mode**: Preview SQL before executing
- **Safety Analysis**: Detect dangerous operations (DROP, ALTER, TRUNCATE)
- **Multiple Databases**: PostgreSQL, MySQL, SQLite support
- **Approval Workflows**: Integrate with GitHub Environments
- **Clear Output**: Structured, readable migration logs
- **Flexible Commands**: Support all Alembic operations

## Quick Start

### Basic Usage

```yaml
- uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
```

### Production-Safe Workflow

```yaml
name: Database Migration

on:
  push:
    branches: [main]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Preview Migration
        uses: sudzxd/alembic-deploy-action@v1
        with:
          database-url: ${{ secrets.DATABASE_URL }}
          dry-run: true
          analyze-safety: true

  apply:
    needs: preview
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Apply Migration
        uses: sudzxd/alembic-deploy-action@v1
        with:
          database-url: ${{ secrets.DATABASE_URL }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `database-url` | Database connection string | Yes | - |
| `command` | Alembic command (upgrade/downgrade/current/history/show) | No | `upgrade` |
| `revision` | Target revision | No | `head` |
| `dry-run` | Show SQL without executing | No | `false` |
| `alembic-config` | Path to alembic.ini | No | `alembic.ini` |
| `working-directory` | Working directory | No | `.` |
| `analyze-safety` | Analyze for dangerous operations | No | `true` |
| `fail-on-danger` | Fail if dangerous operations detected | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `migration-status` | Status: success, failed, skipped, dry-run |
| `current-revision` | Current database revision |
| `target-revision` | Target revision |
| `sql-preview` | Generated SQL (dry-run only) |
| `warnings` | Safety warnings |
| `is-safe` | Whether migration is safe (true/false) |

## Examples

### With Safety Checks

```yaml
- name: Preview Migration
  id: preview
  uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
    dry-run: true
    analyze-safety: true

- name: Check Safety
  run: |
    if [ "${{ steps.preview.outputs.is-safe }}" != "true" ]; then
      echo "Dangerous operations detected:"
      echo "${{ steps.preview.outputs.warnings }}"
      exit 1
    fi
```

### Multi-Environment Deployment

```yaml
jobs:
  staging:
    runs-on: ubuntu-latest
    steps:
      - uses: sudzxd/alembic-deploy-action@v1
        with:
          database-url: ${{ secrets.STAGING_DATABASE_URL }}

  production:
    needs: staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: sudzxd/alembic-deploy-action@v1
        with:
          database-url: ${{ secrets.PRODUCTION_DATABASE_URL }}
```

### Downgrade Example

```yaml
- uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
    command: downgrade
    revision: -1
```

## Safety Features

The action detects and warns about:

- `DROP TABLE` - Data loss
- `DROP COLUMN` - Data loss
- `ALTER COLUMN TYPE` - May fail or lock table
- `TRUNCATE` - All data deleted
- `DROP INDEX` - Performance impact

## Database Connection Strings

### PostgreSQL
```
postgresql://user:password@host:5432/database
```

### MySQL
```
mysql+pymysql://user:password@host:3306/database
```

### SQLite
```
sqlite:///path/to/database.db
```

## Requirements

Your repository must have:
- `alembic.ini` configuration file
- `alembic/` directory with migration scripts
- Valid database connection (accessible from GitHub Actions runner)

## License

MIT - see [LICENSE](./LICENSE)

## Contributing

Contributions are welcome. Please open an issue or pull request.
