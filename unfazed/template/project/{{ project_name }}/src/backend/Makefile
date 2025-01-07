SHELL := /bin/bash
app_list = 

all: test

test:
	@echo "Running tests..."
	pytest -v --cov $(app_list) --cov-report term-missing

format:
	@echo "Running format..."
	ruff check $(app_list)
	ruff format $(app_list)
	mypy $(app_list)

run:
	python manage.py runserver --host 0.0.0.0 --port 9527
