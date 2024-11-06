all: test

test:
	@echo "Running tests..."
	pytest -v -s --cov ./unfazed/test_contrib/test_admin --cov-report term-missing

