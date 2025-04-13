format:
	isort app/ && isort tests/
	black app/ && black tests/
	isort main.py && black main.py

run:
	cp env.example .env && docker compose down --remove-orphans && docker compose up -d --build

shutdown:
	docker compose down

test:
	docker compose exec api pytest tests/

enter-app:
	docker compose exec api bash

enter-db:
	docker compose exec db bash

enter-test-db:
	docker compose exec db-test bash

migrate-db:
	docker compose exec api alembic upgrade head
