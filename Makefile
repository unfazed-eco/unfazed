all: test

test:
	@echo "Running tests..."
	pytest -v --cov ./unfazed --cov-report term-missing
