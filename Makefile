# agent-buywise-shop - local development entry points (phase 0, docs/09)
COMPOSE := docker compose -f deploy/compose/compose.yaml --env-file deploy/compose/.env
DATA_PY := data/tools/.venv/bin/python
AGENT_PY := agent/.venv/bin/python
CONTRACTS := ui/web/projects/shared/contracts

.PHONY: help env up down logs ps migrate seed ingest contracts contracts-check k test data-tools data agent-dev

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

env: ## Create deploy/compose/.env from the example (local secrets, git-ignored)
	@test -f deploy/compose/.env || cp deploy/compose/.env.example deploy/compose/.env

up: env ## Start Postgres, Redis, Keycloak, LiteLLM (Ollama runs on the host)
	$(COMPOSE) up -d --wait postgres redis keycloak litellm

down: ## Stop the stack (keeps data volumes)
	$(COMPOSE) down

ps: ## Show stack status
	$(COMPOSE) ps

logs: ## Follow stack logs
	$(COMPOSE) logs -f

migrate: env ## Apply buywise-services schema migrations with Flyway
	$(COMPOSE) run --rm flyway

seed: migrate ## Load data/seed into the services database (seed job, Option B)
	$(DATA_PY) data/tools/seed_db.py

ingest: ## RAG ingestion (phase 3)
	@echo "make ingest arrives in phase 3 (ADR-039)"; exit 1

agent-dev: ## Create agent/.venv with dev tools (codegen, tests, lint)
	cd agent && python3 -m venv .venv && .venv/bin/pip install -q --group dev

contracts: ## Regenerate TypeScript and Pydantic types from the JSON Schema (ADR-024)
	cd $(CONTRACTS) && npm install --silent --no-audit --no-fund && npm run --silent generate
	agent/.venv/bin/datamodel-codegen --input $(CONTRACTS)/schemas/chat-events.schema.json \
	  --input-file-type jsonschema --output agent/buywise_agent/contracts/chat_contract.py \
	  --output-model-type pydantic_v2.BaseModel --target-python-version 3.12 --use-annotated \
	  --enum-field-as-literal all --disable-timestamp --use-title-as-name --formatters black isort \
	  --custom-file-header '# Generated from ui/web/projects/shared/contracts/schemas/chat-events.schema.json - do not edit. Run make contracts.'

contracts-check: contracts ## Fail if generated contract types are out of date (CI drift check)
	git diff --exit-code -- $(CONTRACTS)/generated agent/buywise_agent/contracts/chat_contract.py

k: ## Measure the LLM hardware factor k and write deploy/local/scale.yaml
	$(DATA_PY) deploy/scripts/benchmark_k.py

test: ## Run all tests available so far
	cd agent && .venv/bin/pytest -q
	cd agent && .venv/bin/ruff check .

data-tools: ## Create the data-generation virtualenv
	python3 -m venv data/tools/.venv && $(DATA_PY) -m pip install -q -r data/tools/requirements.txt

data: ## Regenerate catalog, seed data, knowledge docs and eval sets
	$(DATA_PY) data/tools/build_catalog.py
	$(DATA_PY) data/tools/generate_seed.py
	cd data/tools && .venv/bin/python build_documents.py
	$(DATA_PY) data/tools/build_evals.py
