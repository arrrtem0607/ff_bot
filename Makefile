
all:
	docker compose --env-file .env up -d



migrations:
	alembic revision --autogenerate


