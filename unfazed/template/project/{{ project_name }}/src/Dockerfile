FROM python:3.12-bullseye

COPY . /src
WORKDIR /src/backend

RUN pip3 install uv
RUN poetry config virtualenvs.create false
RUN uv sync
