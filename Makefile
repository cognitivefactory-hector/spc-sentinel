.PHONY: run up down test lint fmt check

# Serve the app at http://localhost:8000 (the M0 acceptance check).
run up:
	docker compose up --build

down:
	docker compose down

test:
	pytest

lint:
	ruff check .

fmt:
	ruff format .

# Django's own config validation; handy before building the image.
check:
	python manage.py check
