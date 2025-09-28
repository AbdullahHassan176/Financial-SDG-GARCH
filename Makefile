# NF-GARCH Results Build Makefile

.PHONY: help build clean install test lint

# Default target
help:
	@echo "NF-GARCH Results Build System"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build Excel consolidation and interactive dashboard"
	@echo "  clean          - Clean build artifacts"
	@echo "  install        - Install required Python packages"
	@echo "  test           - Run unit tests"
	@echo "  lint           - Run code linting"
	@echo "  collection     - Run only results collection"
	@echo "  dashboard      - Run only dashboard build"
	@echo "  serve          - Serve dashboard locally"
	@echo ""

# Main build target
build:
	@echo "Building NF-GARCH results consolidation and dashboard..."
	python tools/build_results.py

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf artifacts/
	rm -rf docs/data/
	rm -rf docs/plots/
	rm -f docs/index.html
	rm -f docs/notes.md

# Install dependencies
install:
	@echo "Installing required packages..."
	pip install pandas numpy openpyxl plotly jinja2 pyyaml

# Run unit tests
test:
	@echo "Running unit tests..."
	python -m pytest tests/ -v

# Run linting
lint:
	@echo "Running code linting..."
	python -m flake8 tools/ --max-line-length=100
	python -m mypy tools/ --ignore-missing-imports

# Run only results collection
collection:
	@echo "Running results collection..."
	python tools/build_results.py --collection-only

# Run only dashboard build
dashboard:
	@echo "Building dashboard..."
	python tools/build_results.py --dashboard-only

# Serve dashboard locally
serve:
	@echo "Serving dashboard locally..."
	@echo "Open http://localhost:8000 in your browser"
	cd docs && python -m http.server 8000

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	mkdir -p artifacts docs/data docs/plots tests
	@echo "Development environment ready!"

# Full pipeline (collection + dashboard)
full: clean build

# Quick test build
quick: collection dashboard
