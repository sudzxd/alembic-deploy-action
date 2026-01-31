# Alembic Deploy Action

[![CI](https://github.com/sudzxd/alembic-deploy-action/actions/workflows/ci.yml/badge.svg)](https://github.com/sudzxd/alembic-deploy-action/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Safe Alembic database migrations with dry-run preview and safety analysis.

## Usage

```yaml
- uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
```

### Dry-Run with Safety Check

```yaml
- uses: sudzxd/alembic-deploy-action@v1
  with:
    database-url: ${{ secrets.DATABASE_URL }}
    dry-run: true
    analyze-safety: true
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `database-url` | Yes | - | Database connection string |
| `command` | No | `upgrade` | Alembic command |
| `revision` | No | `head` | Target revision |
| `dry-run` | No | `false` | Preview SQL without executing |
| `analyze-safety` | No | `true` | Detect dangerous operations |
| `fail-on-danger` | No | `false` | Fail on dangerous operations |

## Outputs

| Output | Description |
|--------|-------------|
| `migration-status` | `success`, `failed`, `dry-run` |
| `is-safe` | `true` / `false` |
| `sql-preview` | Generated SQL (dry-run only) |
| `warnings` | Safety warnings detected |

## Safety Detection

Detects: `DROP TABLE`, `DROP COLUMN`, `ALTER COLUMN TYPE`, `TRUNCATE`, `DROP INDEX`

## License

MIT - see [LICENSE](./LICENSE)

---

[Changelog](./CHANGELOG.md) · [Issues](https://github.com/sudzxd/alembic-deploy-action/issues)
