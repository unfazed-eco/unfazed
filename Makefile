all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed/cache --cov-report term-missing

