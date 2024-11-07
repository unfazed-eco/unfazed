all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed/contrib/admin --cov-report term-missing

