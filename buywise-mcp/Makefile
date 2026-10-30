# mcp module: buywise-mcp - one process, one MCP server per domain under /mcp/{domain} (ADR-031).
.PHONY: help dev run smoke

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

dev: ## Create .venv exactly as pinned in uv.lock
	uv sync --locked

run: ## Start MCP servers on http://localhost:8090/mcp/{catalog,inventory,orders} (needs services on 8081)
	uv run --locked uvicorn buywise_mcp.app:app --port 8090

smoke: ## Call each tool once over HTTP (needs services and MCP running)
	uv run --locked python tests/smoke.py
