# mcp module: buywise-mcp - one process, one MCP server per domain under /mcp/{domain} (ADR-031).
.PHONY: help dev run smoke test snapshots test-integration

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

dev: ## Create .venv exactly as pinned in uv.lock
	uv sync --locked

run: ## Start MCP servers on http://localhost:8090/mcp/{catalog,inventory,orders} (needs services on 8081)
	uv run --locked uvicorn buywise_mcp.app:app --port 8090

smoke: ## Call each tool once over HTTP (needs services and MCP running)
	uv run --locked python tests/smoke.py

test: ## Tool contract snapshots + lint (fast, no services needed)
	uv run --locked pytest
	uv run --locked ruff check .

snapshots: ## Rewrite tests/snapshots after an INTENDED tool change - then review the git diff
	SNAPSHOT_UPDATE=1 uv run --locked pytest tests/test_snapshots.py

test-integration: ## Every tool against real Postgres + buywise-services in containers (needs Docker)
	$(MAKE) -C ../buywise-services image
	uv run --locked pytest -m integration
