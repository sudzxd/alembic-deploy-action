# Alembic Deploy Action

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Alembic%20Deploy%20Action-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEZPfsVJ61jbxaF0cRQRcRJ9hlYn30IHN/+9iquDCOIsblIrOjqKgy5aKoJQj4O3EEtbPwhJbr6Te28CmdSKeqzeqr0YbfVIrTBKakvtOl5dtTkK+v4HfA9PEyBFCY9AGVgCBLaBp1jPAyfAJ/AAdIEG0dNAiyP7+K1qIfMdonZic6+WJoBJvQlvuwDqcXadUuqPA1NKAlexbRTAIMvMOCjTbMwl1LtI/6KWJ5Q6rT6Ht1MA58AX8Apcqqt5r2qhrgAXQC3CZ6i1+KMd9TRu3MvA3aH/fFPnBodb6oe6HM8+lYHrGdRXW8M9bMZtPXUji69lmf5Cmamq7quNLFZXD9Rq7v0Bpc1o/tp0fisAAAAASUVORK5CYII=)](https://github.com/marketplace/actions/alembic-deploy-action)
[![Tests](https://github.com/sudzxd/alembic-deploy-action/actions/workflows/test.yml/badge.svg)](https://github.com/sudzxd/alembic-deploy-action/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/sudzxd/alembic-deploy-action)](https://github.com/sudzxd/alembic-deploy-action/releases)

GitHub Action for safe Alembic database migrations with dry-run preview, validation, and approval workflows.

📦 [View on GitHub Marketplace](https://github.com/marketplace/actions/alembic-deploy-action)

## Features

- **Dry-Run Mode**: Preview SQL before executing
- **Safety Analysis**: Detect dangerous operations (DROP, ALTER, TRUNCATE)
- **Multiple Databases**: PostgreSQL, MySQL, SQLite support
- **Approval Workflows**: Integrate with GitHub Environments
- **Clear Output**: Structured, readable migration logs
- **Flexible Commands**: Support all Alembic operations

## Installation

Add to your GitHub Actions workflow:

```yaml
- uses: sudzxd/alembic-deploy-action@v1  # Recommended: auto-updates to latest v1.x
```

Or pin to a specific version:

```yaml
- uses: sudzxd/alembic-deploy-action@v1.0.0  # Locked to v1.0.0
```

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

## Support

- [Documentation](https://github.com/sudzxd/alembic-deploy-action/blob/master/README.md)
- [Examples](https://github.com/sudzxd/alembic-deploy-action/tree/master/examples)
- [Issues](https://github.com/sudzxd/alembic-deploy-action/issues)
- [Security Policy](https://github.com/sudzxd/alembic-deploy-action/blob/master/SECURITY.md)

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) before submitting PRs.

## Changelog

See [Releases](https://github.com/sudzxd/alembic-deploy-action/releases) for version history.
