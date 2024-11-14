FROM python:3.9.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install curl (может понадобиться для healthcheck)
RUN apt-get update \
 && apt-get install -y curl --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Dependencies
COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY ./app ./app

# Используем переменную окружения PORT
CMD uvicorn app.main:tinder_app --host 0.0.0.0 --port $PORT
