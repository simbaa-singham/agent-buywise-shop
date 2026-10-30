# deploy module: local stack (Docker Compose) and runtime tooling. Run from repo root via `make <target>` or here.
COMPOSE := docker compose -f compose/compose.yaml --env-file compose/.env

.PHONY: help env up down ps logs migrate flyway-info k demo-user

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

env: ## Create compose/.env from the example (local secrets, git-ignored)
	@test -f compose/.env || cp compose/.env.example compose/.env

up: env ## Start Postgres, Redis, Keycloak, LiteLLM and wait until healthy (Ollama runs on the host)
	$(COMPOSE) up -d --wait postgres redis keycloak litellm

down: ## Stop the stack (data is kept)
	$(COMPOSE) down

ps: ## Show stack status
	$(COMPOSE) ps

logs: ## Follow stack logs
	$(COMPOSE) logs -f

migrate: env ## Apply buywise-services schema migrations with Flyway
	$(COMPOSE) run --rm flyway

flyway-info: env ## Show which migrations are applied / pending (changes nothing)
	$(COMPOSE) run --rm flyway info

k: ## Measure the LLM hardware factor k and write local/scale.yaml
	python3 scripts/benchmark_k.py

demo-user: env ## Local only: Keycloak client secret + demo customer login (username demo)
	./compose/keycloak/add-demo-user.sh
