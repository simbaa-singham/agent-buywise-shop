# agent module: buywise-agent (Python).
# Python environment managed by uv (ADR-042): pyproject.toml + uv.lock, Python version in .python-version.
.PHONY: help dev lock test lint ingest run turn

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

ingest: ## Load help articles and policies into pgvector (md, txt, html, pdf, docx)
	uv run --locked python -m buywise_agent.rag.ingest

run: ## Start the agent API on http://localhost:8000
	uv run --locked uvicorn buywise_agent.api:app --port 8000

turn: ## One chat turn from the terminal: make turn Q="Is the iPhone 18 Pro in stock in Austin?" [C=cu-demo]
	uv run --locked python tests/turn.py "$(Q)" $(or $(C),-)
