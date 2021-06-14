FROM python:3.7-slim

# Install poetry
RUN pip install poetry

COPY . /src
WORKDIR /src

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
