install:
	uv sync

build:
	./build.sh

lint:
	uv run ruff check page_analyzer/app.py

dev:
	uv run flask --debug --app page_analyzer.app:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

render-start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app