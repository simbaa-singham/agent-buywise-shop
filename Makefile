# agent-buywise-shop - root entry points. Each command is defined in its module's Makefile;
# these short names just delegate (run `make -C <module> help` for a module's own commands).

.PHONY: help up down ps logs migrate flyway-info k data-tools data agent-dev test ingest contracts contracts-check

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

up: ## [deploy] Start Postgres, Redis, Keycloak, LiteLLM
	@$(MAKE) --no-print-directory -C deploy up
down: ## [deploy] Stop the stack (data is kept)
	@$(MAKE) --no-print-directory -C deploy down
ps: ## [deploy] Show stack status
	@$(MAKE) --no-print-directory -C deploy ps
logs: ## [deploy] Follow stack logs
	@$(MAKE) --no-print-directory -C deploy logs
migrate: ## [services] Apply schema migrations (Flyway)
	@$(MAKE) --no-print-directory -C services migrate
flyway-info: ## [services] Show applied / pending migrations
	@$(MAKE) --no-print-directory -C services flyway-info
k: ## [deploy] Measure the LLM hardware factor k
	@$(MAKE) --no-print-directory -C deploy k
data-tools: ## [data] Create the data-generation virtualenv
	@$(MAKE) --no-print-directory -C data tools
data: ## [data] Regenerate catalog, seed data, knowledge docs, eval sets
	@$(MAKE) --no-print-directory -C data generate
agent-dev: ## [agent] Create agent/.venv with dev tools
	@$(MAKE) --no-print-directory -C agent dev
test: ## [agent] Run tests and lint
	@$(MAKE) --no-print-directory -C agent test
ingest: ## [agent] RAG ingestion (phase 3)
	@$(MAKE) --no-print-directory -C agent ingest
contracts: ## [ui] Regenerate contract types (TypeScript + Python)
	@$(MAKE) --no-print-directory -C ui contracts
contracts-check: ## [ui] Fail if generated contract types are out of date
	@$(MAKE) --no-print-directory -C ui contracts-check
