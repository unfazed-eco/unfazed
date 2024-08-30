SHELL := /bin/bash
app_list = 

all: test

init:
	poetry config virtualenvs.create false --local
	poetry update

test:
	mypy --ignore-missing-imports --check-untyped-defs $(app_list)
	ruff check $(app_list)
	pytest -v --cov $(app_list) --cov-report term-missing

run:
	python manage.py runserver 0:3001
