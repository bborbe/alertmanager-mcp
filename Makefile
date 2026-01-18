.PHONY: precommit format lint typecheck check test install

precommit: format test check
	@echo "All precommit checks passed"

format:
	uv run ruff format .
	uv run ruff check --fix . || true

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck

test:
	uv run pytest

install:
	uv sync --all-extras
