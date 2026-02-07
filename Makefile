.PHONY: precommit format lint typecheck check test install sync

# Install dependencies (alias for sync)
install: sync

# Sync dependencies
sync:
	@uv sync --all-extras

# Format code with ruff
format:
	uv run ruff format .
	uv run ruff check --fix . || true

# Lint code with ruff
lint:
	uv run ruff check .

# Type check with mypy
typecheck:
	uv run mypy src

# Run lint and typecheck
check: lint typecheck

# Run tests with pytest
test: sync
	uv run pytest

# Run all precommit checks
precommit: sync format test check
	@echo "✓ All precommit checks passed"
