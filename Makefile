# Makefile for Android Log Analyzer

.PHONY: help install install-dev test test-coverage lint format type-check clean build docs gui

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  docs         - Generate documentation"
	@echo "  gui          - Start GUI application"
	@echo "  sample-config - Generate sample configuration file"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

# Testing targets
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=android_log_analyzer --cov-report=html --cov-report=term

test-legacy:
	python -m unittest android_log_analyzer.test_log_analyzer -v

# Code quality targets
lint:
	flake8 android_log_analyzer/ tests/
	@echo "Linting completed successfully!"

format:
	black android_log_analyzer/ tests/
	isort android_log_analyzer/ tests/
	@echo "Code formatting completed!"

type-check:
	mypy android_log_analyzer/
	@echo "Type checking completed!"

# Quality check combination
check: lint type-check test
	@echo "All quality checks passed!"

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned build artifacts!"

build: clean
	python -m build
	@echo "Build completed!"

# Documentation
docs:
	@echo "Documentation generation not yet implemented"

# GUI application
gui:
	cd log_analyzer_gui && npm install && npm start

# Configuration
sample-config:
	python -c "from android_log_analyzer.config import create_sample_config; create_sample_config('sample_config.json')"
	@echo "Sample configuration created: sample_config.json"

# Development setup
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make check' to verify everything is working."

# CI/CD simulation
ci: install-dev lint type-check test
	@echo "CI pipeline simulation completed successfully!"
