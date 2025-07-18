# Confluence Page API - Makefile

.PHONY: install test test-unit test-integration lint clean coverage dev help

help: ## Show this help message
	@echo "Confluence Page API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -r requirements-test.txt

test: ## Run all tests
	python tests/test_runner.py

test-unit: ## Run unit tests only
	python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	python -m pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	python -m pytest tests/ --cov=api --cov-report=term-missing --cov-report=html:htmlcov

lint: ## Run linting (placeholder - add linting tools as needed)
	@echo "No linting configured yet. Consider adding flake8, black, or ruff."

clean: ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

dev: ## Run development server
	vercel dev

format: ## Format code (placeholder)
	@echo "No code formatting configured yet. Consider adding black or ruff."

check: ## Run all checks (tests, linting, etc.)
	make test
	make lint