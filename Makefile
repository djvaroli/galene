.PHONY: dev stop logs check test-unit test-integration migrate

# Use the same pinned toolchains locally and in CI; only Docker and Python 3.12 are needed.
dev:
	docker compose up --build -d --wait

stop:
	docker compose down

logs:
	docker compose logs -f --tail=100

migrate:
	docker compose run --build --rm migrate

check:
	docker compose --profile tools run --build --rm --no-deps backend-check
	docker compose --profile tools run --build --rm --no-deps frontend-check

test-unit:
	docker compose --profile tools run --build --rm --no-deps backend-check pytest -q

test-integration:
	python3 scripts/test_integration.py
