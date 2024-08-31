FROM python:3.12.3-bullseye


COPY . /src
WORKDIR /src/backend

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
