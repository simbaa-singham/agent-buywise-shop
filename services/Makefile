# services module: buywise-services (Spring Boot, phase 1+). Migrations live in src/main/resources/db/migration.
.PHONY: help migrate flyway-info

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

migrate: ## Apply this module's migrations (runs Flyway from the deploy stack)
	$(MAKE) -C ../deploy migrate

flyway-info: ## Show applied / pending migrations
	$(MAKE) -C ../deploy flyway-info
