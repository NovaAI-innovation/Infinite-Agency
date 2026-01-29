# Makefile for Multi-Domain Agency System

.PHONY: help install test test-coverage lint format run-example docker-build docker-run

# Show help message
help:
	@echo "Multi-Domain Agency System Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install          Install dependencies"
	@echo "  make test             Run tests"
	@echo "  make test-coverage    Run tests with coverage"
	@echo "  make lint             Run linting"
	@echo "  make format           Format code"
	@echo "  make run-example      Run example application"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run tests
test:
	python -m pytest test_agency.py -v

# Run tests with coverage
test-coverage:
	python -m pytest --cov=agency test_agency.py --cov-report=term-missing

# Run linting
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check .

# Format code
format:
	black .

# Run example application
run-example:
	python app_example.py

# Build Docker image
docker-build:
	docker build -t agency-system .

# Run Docker container
docker-run: docker-build
	docker run -p 8000:8000 agency-system

# Run security audit
security-audit:
	bandit -r agency/ -f screen
	safety check -r requirements.txt

# Clean up Python cache files
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf *.egg-info