.PHONY: install-dev train run test lint format dvc-push dvc-pull

install-dev:
	poetry install --with dev

train:
	poetry run python -m src.ml.train

generate:
	poetry run python -m src.data.generate_data

run:
	poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest -q

lint:
	poetry run black --check src tests
	poetry run flake8 src tests

format:
	poetry run black src tests

dvc-push:
	poetry run dvc push

dvc-pull:
	poetry run dvc pull
