# agent module: buywise-agent (Python).
# Python environment managed by uv (ADR-042): pyproject.toml + uv.lock, Python version in .python-version.
.PHONY: help dev lock test lint ingest

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

dev: ## Create .venv with dev tools (codegen, tests, lint) exactly as pinned in uv.lock
	uv sync --locked

lock: ## Re-resolve uv.lock after changing dependencies in pyproject.toml (add --upgrade via ARGS=--upgrade)
	uv lock $(ARGS)

test: ## Run tests and lint
	uv run --locked pytest -q
	uv run --locked ruff check .

lint: ## Lint only
	uv run --locked ruff check .

ingest: ## RAG ingestion (phase 3, ADR-039)
	@echo "ingest arrives in phase 3"; exit 1
