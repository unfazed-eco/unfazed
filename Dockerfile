FROM python:3.12.3-bullseye


COPY . /unfazed
WORKDIR /unfazed

RUN pip3 install uv
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
