.PHONY: setup up down test populate logs clean

setup:
	docker compose pull
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

test:
	pytest -q

populate:
	docker compose exec fastapi python /app/scripts/populate.py

logs:
	docker compose logs -f

clean:
	docker compose down -v
