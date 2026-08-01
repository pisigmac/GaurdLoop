.PHONY: help dev build test lint format clean deploy-staging deploy-prod

help:
	@echo "GuardLoop — Available commands:"
	@echo "  make dev          Start local development (docker-compose)"
	@echo "  make build        Build Docker images"
	@echo "  make test         Run all tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make clean        Remove build artifacts"
	@echo "  make deploy-staging  Deploy to staging"
	@echo "  make deploy-prod     Deploy to production"

dev:
	docker-compose up --build

build:
	docker build -t guardloop/backend:latest ./backend
	docker build -t guardloop/frontend:latest ./frontend

test:
	cd backend && pytest -v
	cd frontend && npm test

lint:
	cd backend && ruff check .
	cd frontend && npx next lint

format:
	cd backend && ruff format .
	cd frontend && npx prettier --write .

clean:
	rm -rf backend/__pycache__ backend/.pytest_cache backend/.coverage
	rm -rf frontend/.next frontend/node_modules
	docker-compose down -v

deploy-staging:
	@echo "Deploy to staging via GitHub Actions or:"
	@echo "kubectl apply -f infra/k8s/ -n guardloop-staging"

deploy-prod:
	@echo "Deploy to production via GitHub Actions release or:"
	@echo "kubectl apply -f infra/k8s/ -n guardloop"
