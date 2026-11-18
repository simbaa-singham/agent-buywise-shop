# agent-buywise-shop - root entry points. Each command is defined in its module's Makefile;
# these short names just delegate (run `make -C <module> help` for a module's own commands).

.PHONY: help start stop demo-user up down ps logs migrate flyway-info seed k data-tools data agent-dev test ingest contracts contracts-check

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

start: ## Start everything on the Mac (stack, services, MCP, agent, web) -> http://localhost:3000
	@./buywise-deploy/local/run-local.sh
stop: ## Stop the app processes (the Docker stack keeps running)
	@./buywise-deploy/local/stop-local.sh
demo-user: ## [buywise-deploy] Local demo customer login (username demo, password in buywise-deploy/compose/.env)
	@$(MAKE) --no-print-directory -C buywise-deploy demo-user
up: ## [buywise-deploy] Start Postgres, Redis, Keycloak, LiteLLM
	@$(MAKE) --no-print-directory -C buywise-deploy up
down: ## [buywise-deploy] Stop the stack (data is kept)
	@$(MAKE) --no-print-directory -C buywise-deploy down
ps: ## [buywise-deploy] Show stack status
	@$(MAKE) --no-print-directory -C buywise-deploy ps
logs: ## [buywise-deploy] Follow stack logs
	@$(MAKE) --no-print-directory -C buywise-deploy logs
migrate: ## [buywise-db] Apply schema migrations to services + agent databases (Flyway)
	@$(MAKE) --no-print-directory -C buywise-db migrate
flyway-info: ## [buywise-db] Show applied / pending migrations
	@$(MAKE) --no-print-directory -C buywise-db flyway-info
seed: ## [buywise-db] REPLACE services seed data from buywise-db/services/03-data
	@$(MAKE) --no-print-directory -C buywise-db seed
k: ## [buywise-deploy] Measure the LLM hardware factor k
	@$(MAKE) --no-print-directory -C buywise-deploy k
data-tools: ## [buywise-data] Create the data-generation virtualenv
	@$(MAKE) --no-print-directory -C buywise-data tools
data: ## [buywise-data] Regenerate catalog, seed data, knowledge docs, eval sets
	@$(MAKE) --no-print-directory -C buywise-data generate
agent-dev: ## [buywise-agent] Create buywise-agent/.venv with dev tools
	@$(MAKE) --no-print-directory -C buywise-agent dev
test: ## [buywise-agent] Run tests and lint
	@$(MAKE) --no-print-directory -C buywise-agent test
ingest: ## [buywise-agent] Load knowledge documents into pgvector (needs Ollama)
	@$(MAKE) --no-print-directory -C buywise-agent ingest
contracts: ## [buywise-web] Regenerate contract types (TypeScript + Python)
	@$(MAKE) --no-print-directory -C buywise-web contracts
contracts-check: ## [buywise-web] Fail if generated contract types are out of date
	@$(MAKE) --no-print-directory -C buywise-web contracts-check
