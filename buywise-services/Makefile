# services module: buywise-services (Spring Boot modular monolith). Migrations live in src/main/resources/db/migration.
.PHONY: help migrate flyway-info build run

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

migrate: ## Apply this module's migrations (runs Flyway from the deploy stack)
	$(MAKE) -C ../deploy migrate

flyway-info: ## Show applied / pending migrations
	$(MAKE) -C ../deploy flyway-info

build: ## Compile, run tests (incl. module boundary check)
	./gradlew build

run: ## Start the services app on http://localhost:8081
	./gradlew bootRun
