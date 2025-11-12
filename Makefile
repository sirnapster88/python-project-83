install:
	uv sync

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

lint:
	uv run ruff check app.py

test:
	uv run pytest

dev:
	uv run flask --debug --app page_analyzer.app:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app