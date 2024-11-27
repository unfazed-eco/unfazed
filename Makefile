all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed/contrib/auth --cov-report term-missing





