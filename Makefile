all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed --cov-report term-missing

format:
	@echo "Formatting code..."
	ruff format tests/ unfazed/
	ruff check tests/ unfazed/  --fix
	mypy --check-untyped-defs --explicit-package-bases tests/ unfazed/

publish:
	@echo "Publishing package..."
	uv build
	uv publish
