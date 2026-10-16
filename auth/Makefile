.PHONY: setup dev test lint format

setup:
	uv sync

dev:
	uv run uvicorn src.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
