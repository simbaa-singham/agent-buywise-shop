# ui module: buywise-web. Owns the chat contract (ADR-024) used by the web app, the BFF and the agent.
CONTRACTS := web/projects/shared/contracts
AGENT := ../buywise-agent

.PHONY: help contracts contracts-check

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

contracts: ## Regenerate TypeScript and Pydantic types from the JSON Schema
	npm install --silent --no-audit --no-fund && npm run --silent contracts:generate
	uv run --project $(AGENT) --locked datamodel-codegen --input $(CONTRACTS)/schemas/chat-events.schema.json \
	  --input-file-type jsonschema --output $(AGENT)/buywise_agent/contracts/chat_contract.py \
	  --output-model-type pydantic_v2.BaseModel --target-python-version 3.12 --use-annotated \
	  --enum-field-as-literal all --disable-timestamp --use-title-as-name --formatters ruff-format ruff-check \
	  --custom-file-header '# Generated from buywise-web/web/projects/shared/contracts/schemas/chat-events.schema.json - do not edit. Run make contracts.'

contracts-check: contracts ## Fail if generated contract types are out of date (CI drift check)
	git diff --exit-code -- $(CONTRACTS)/generated $(AGENT)/buywise_agent/contracts/chat_contract.py

.PHONY: install build run
install: ## Install web app and BFF packages
	cd web && npm install --no-audit --no-fund
	cd bff && npm install --no-audit --no-fund

build: ## Build the Angular app and the BFF
	cd web && npx ng build customer-web
	cd bff && npx tsc -p tsconfig.json

run: build ## Serve the app + BFF on http://localhost:3000 (needs agent, Redis, Keycloak)
	cd bff && node dist/main.js
