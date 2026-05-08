PY ?= python
PIP ?= $(PY) -m pip
PORT ?= 5000

.PHONY: help install dev test lint format run repl index docs docker clean

help: ## Show this help
	@awk 'BEGIN{FS=":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install runtime dependencies
	$(PIP) install -r requirements.txt

dev: ## Install dev dependencies
	$(PIP) install -e ".[dev]"

test: ## Run the pytest suite
	$(PY) -m pytest -q

lint: ## Run ruff
	$(PY) -m ruff check src tests cli.py app.py scripts

format: ## Format with black + ruff fixes
	$(PY) -m black --line-length 100 src tests cli.py app.py scripts
	$(PY) -m ruff check --fix src tests cli.py app.py scripts

run: ## Start the Flask app
	PORT=$(PORT) FLASK_DEBUG=1 $(PY) app.py

repl: ## Launch the CLI in REPL mode
	$(PY) cli.py

index: ## (Re)build the on-disk index
	$(PY) scripts/build_index.py

docs: ## Regenerate every PDF document and SVG diagram is rasterised
	$(PY) scripts/build_docs.py

docker: ## Build the production Docker image
	docker build -t nlp-search-engine:latest .

clean: ## Remove build / cache artifacts
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
	rm -rf index_data
