.PHONY: lint dc-build test test.cpython test.pypy test.cpython-latest test.pypy-latest


lint:
	@uv run pre-commit run -a
	@uvx ty check

dc-build:
	@COMPOSE_BAKE=1 docker compose build

test: test.cpython test.cpython-latest test.pypy test.pypy-latest

test.cpython: dc-build
	@docker compose run --rm cpython uv run pytest -v

test.cpython-latest: dc-build
	@docker compose run --rm cpython-latest uv run pytest -v

test.pypy: dc-build
	@docker compose run --rm pypy uv run pytest -v

test.pypy-latest: dc-build
	@docker compose run --rm pypy-latest uv run pytest -v
