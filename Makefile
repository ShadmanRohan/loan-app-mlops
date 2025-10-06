.PHONY: up down up-monitoring lint test
up:
	docker compose -f infrastructure/docker-compose.yml up -d --build
down:
	docker compose -f infrastructure/docker-compose.yml down
up-monitoring:
	docker compose -f infrastructure/docker-compose.yml -f infrastructure/docker-compose.monitoring.yml up -d --build
lint:
	python -m ruff . || true
test:
	pytest -q || true
