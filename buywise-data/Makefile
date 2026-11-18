# buywise-data module: knowledge documents, eval sets and the generators (tools/) that also write the seed data in buywise-db.
# Python environment managed by uv (ADR-042): tools/pyproject.toml + tools/uv.lock.
UV := uv run --project tools --locked

.PHONY: help tools generate

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

tools: ## Create the data-generation environment (tools/.venv) from tools/uv.lock
	uv sync --project tools --locked

generate: ## Regenerate catalog, seed data, knowledge docs and eval sets (deterministic content)
	$(UV) python tools/build_catalog.py
	$(UV) python tools/generate_seed.py
	cd tools && uv run --locked python build_documents.py
	$(UV) python tools/build_evals.py
