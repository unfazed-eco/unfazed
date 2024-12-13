all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed/contrib/session/ --cov-report term-missing

format:
	@echo "Formatting code..."
	ruff format tests/ unfazed/
	ruff check tests/ unfazed/  --fix
	mypy --check-untyped-defs --explicit-package-bases tests/ unfazed/
