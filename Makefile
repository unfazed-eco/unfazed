all: test

test:
	@echo "Running tests..."
	pytest -v --cov ./unfazed --cov-report term-missing

format:
	@echo "Formatting code..."
	ruff format tests/ unfazed/
	ruff check tests/ unfazed/  --fix
	mypy --check-untyped-defs --explicit-package-bases unfazed/cache/
