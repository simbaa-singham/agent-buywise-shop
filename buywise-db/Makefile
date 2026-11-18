# db module: every database script in one place (ADR-046). Run from repo root via `make <target>` or here.
# Uses the Docker stack from deploy/ (make up first).
COMPOSE := docker compose -f ../deploy/compose/compose.yaml --env-file ../deploy/compose/.env
PG := buywise-postgres-1

.PHONY: help migrate flyway-info seed

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

migrate: ## Apply pending migrations to the services and agent databases (Flyway)
	$(COMPOSE) run --rm flyway
	$(COMPOSE) run --rm flyway-agent

flyway-info: ## Show applied / pending migrations for both databases (changes nothing)
	$(COMPOSE) run --rm flyway info
	$(COMPOSE) run --rm flyway-agent info

seed: ## REPLACES the services seed data (catalog, stores, stock, customers, orders, tax) from data/seed
	docker cp ../data/seed $(PG):/tmp/seed
	docker exec -i $(PG) psql -v ON_ERROR_STOP=1 -U postgres -d services < services/seed/01-catalog-inventory.sql
	docker exec -i $(PG) psql -v ON_ERROR_STOP=1 -U postgres -d services < services/seed/02-customers-orders.sql
