# agent module: buywise-agent (Python).
.PHONY: help dev test lint ingest

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

dev: ## Create .venv with dev tools (codegen, tests, lint)
	python3 -m venv .venv && .venv/bin/pip install -q --group dev

test: ## Run tests and lint
	.venv/bin/pytest -q
	.venv/bin/ruff check .

lint: ## Lint only
	.venv/bin/ruff check .

ingest: ## RAG ingestion (phase 3, ADR-039)
	@echo "ingest arrives in phase 3"; exit 1
