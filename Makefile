all: test

test:
	@echo "Running tests..."
	uv run pytest -v -s --cov ./unfazed --cov-report term-missing

format:
	@echo "Formatting code..."
	uv run ruff format tests/ unfazed/
	uv run ruff check tests/ unfazed/  --fix
	uv run mypy --check-untyped-defs --explicit-package-bases tests/ unfazed/

publish:
	@echo "Publishing package..."
	uv build
	uv publish


docs:
	uv run mkdocs build