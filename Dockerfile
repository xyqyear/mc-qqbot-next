ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-alpine AS poetry-base

ARG POETRY_VERSION=1.8.4

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    apk del \
        gcc \
        musl-dev \
        libffi-dev

FROM poetry-base AS app-env

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev && \
    poetry install --no-interaction --no-cache --no-root --only main && \
    apk del \
        gcc \
        musl-dev \
        libffi-dev

FROM python:${PYTHON_VERSION}-alpine AS app

ENV PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT="prod" \
    HOST="0.0.0.0" \
    PORT="8080" \
    LOCALSTORE_DATA_DIR="/data"

RUN apk add --no-cache \
        docker \
        docker-cli-compose

WORKDIR /app

COPY --from=app-env /app/.venv /app/.venv

COPY . /app

RUN mkdir -p /data

EXPOSE 8080

CMD ["python3", "main.py"]
