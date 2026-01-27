.PHONY: help build up down logs clean test docs benchmark

help:
	@echo "Model Compilation Project - Available Commands:"
	@echo "  make build       - Build Docker containers"
	@echo "  make up          - Start services in development mode"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View container logs"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make docs        - Generate documentation"
	@echo "  make benchmark   - Run benchmarks"
	@echo "  make shell       - Open shell in container"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "Services started. API available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f model-compilation

clean:
	docker-compose down -v
	rm -rf data/models/* data/binaries/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage .pytest_cache/

test:
	docker-compose exec model-compilation pytest

docs:
	docker-compose exec model-compilation python scripts/generate_docs.py

benchmark:
	docker-compose exec model-compilation python scripts/run_benchmark.py

shell:
	docker-compose exec model-compilation /bin/bash
