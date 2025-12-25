FROM python:3.12.12-bookworm


COPY . /unfazed
WORKDIR /unfazed

RUN pip3 install uv
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
RUN uv sync --all-extras
