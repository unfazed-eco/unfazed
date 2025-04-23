FROM python:3.12-bullseye

COPY . /src
WORKDIR /src/backend

RUN pip3 install uv
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
RUN uv sync
