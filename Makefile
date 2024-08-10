.PHONY: lint test test.cpython test.pypy


lint:
	@poetry run pre-commit run -a

test: test.pypy test.cpython

test.cpython:
	@docker compose run --rm cpython poetry run pytest

test.pypy:
	@docker compose run --rm --remove-orphans pypy poetry run pytest
