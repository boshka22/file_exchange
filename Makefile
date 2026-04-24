install-test-deps:
	docker exec -it backend sh -c "uv pip install --system aiosqlite httpx pytest pytest-asyncio pytest-mock"

test:
	docker exec -it backend pytest

test-v:
	docker exec -it backend pytest -v

up:
	docker compose -f docker-compose.dev.yml up

down:
	docker compose -f docker-compose.dev.yml down

migrate:
	docker exec -it backend alembic upgrade head
