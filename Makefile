sync:
	uv sync --all-groups

test:
	uv run pytest -q

integration:
	PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True uv run --extra paddle pytest -m integration -q

coverage:
	uv run pytest --cov=tablecv --cov-report=term-missing

format:
	uv run ruff format .

ruff:
	uv run ruff check . --fix

security:
	uv run bandit -c bandit.yaml -r tablecv

lint:
	uv run pre-commit run --all-files

check-commit:
	uv run ruff format --check .
	uv run ruff check .
	uv run pytest -q
	uv run bandit -c bandit.yaml -r tablecv

build:
	uv build

publish-check: build
	uv run python -m zipfile --test dist/*.whl

install-hooks:
	uv run pre-commit install

pcupdate:
	uv run pre-commit autoupdate

.PHONY: build check-commit coverage format install-hooks integration lint pcupdate publish-check ruff security sync test
