.PHONY: install lint lint-fix format typecheck test test-cov check pre-commit clean

# Install dependencies with uv
install:
	uv venv
	uv pip install -e ".[dev]"

# Run linter
lint:
	uv run ruff check src tests

# Auto-fix lint issues
lint-fix:
	uv run ruff check --fix src tests

# Run formatter
format:
	uv run ruff format src tests

# Run type checker
typecheck:
	uv run pyright src tests

# Run tests
test:
	uv run pytest tests/unit -v

# Run tests with coverage
test-cov:
	uv run pytest tests/unit --cov=src --cov-report=html --cov-report=term

# Run all checks (used by CI and pre-commit)
check: lint typecheck test

# Install pre-commit hooks
pre-commit:
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

# Run pre-commit on all files
pre-commit-all:
	uv run pre-commit run --all-files

# Clean build artifacts
clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
