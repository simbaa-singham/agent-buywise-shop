# services module: buywise-services (Spring Boot modular monolith). Migrations live in buywise-db/services/01-ddl (ADR-046).
.PHONY: help migrate flyway-info build run image

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

migrate: ## Apply migrations (runs Flyway via buywise-db)
	$(MAKE) -C ../buywise-db migrate

flyway-info: ## Show applied / pending migrations
	$(MAKE) -C ../buywise-db flyway-info

build: ## Compile, run tests (incl. module boundary check)
	./gradlew build

run: ## Start the services app on http://localhost:8081
	./gradlew bootRun

image: ## Build the jar and the container image buywise-services:dev (used by MCP integration tests)
	./gradlew bootJar
	docker build -t buywise-services:dev .
