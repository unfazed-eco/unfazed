all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed --cov-report term-missing


