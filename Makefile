PY := data/tools/.venv/bin/python

.PHONY: data-tools data

# Create the data-generation virtualenv (ADR-033 / ADR-039 tooling)
data-tools:
	python3 -m venv data/tools/.venv && $(PY) -m pip install -q -r data/tools/requirements.txt

# Regenerate all seed data, knowledge documents and eval sets (deterministic)
data:
	$(PY) data/tools/build_catalog.py
	$(PY) data/tools/generate_seed.py
	cd data/tools && .venv/bin/python build_documents.py
	$(PY) data/tools/build_evals.py
