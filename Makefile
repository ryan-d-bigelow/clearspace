HOST=127.0.0.1
PORT=8000
IMAGE_NAME=task-tracker:local

.PHONY: install dev test lint format check build docker-build docker-run precommit clean

install:
	uv sync --dev

dev:
	HOST=$(HOST) PORT=$(PORT) uv run uvicorn app:app --reload --host $(HOST) --port $(PORT)

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run ruff format .

check: lint test

build:
	uv run python -m build

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm -p 8000:8000 $(IMAGE_NAME)

precommit:
	uv run pre-commit install

clean:
	rm -rf .pytest_cache .ruff_cache .coverage build dist htmlcov *.egg-info tasks.db
