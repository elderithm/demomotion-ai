.PHONY: install dev-api dev-web test build compose-up compose-down compose-logs compose-build compose-clean

install:
	pnpm install
	cd services/api && python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e '.[dev]'
	cd services/api && . .venv/bin/activate && python -m playwright install chromium

dev-api:
	cd services/api && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

dev-web:
	pnpm --filter @demomotion/web dev

compose-up:
	docker compose up --build

compose-build:
	docker compose build

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f

compose-clean:
	docker compose down -v --remove-orphans

test:
	cd services/api && . .venv/bin/activate && pytest

build:
	pnpm --filter @demomotion/web build
	cd services/api && . .venv/bin/activate && python -m compileall app
