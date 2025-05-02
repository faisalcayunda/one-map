# Gunakan image Python yang stabil
FROM python:3.13-slim-bookworm AS base

ENV POETRY_HOME="/opt/poetry" \
    PYTHONPATH=/app \
    PYTHONHASHSEED=0 \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PYTHONWRITEBYTECODE=1 \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    locales \
    locales-all \
    libmagic1 && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-root --no-interaction --no-ansi

RUN apt-get autoremove -y && \
    apt-get purge -y curl git build-essential && \
    apt-get clean -y && \
    rm -rf /root/.cache /var/lib/apt/lists/*

FROM base AS app-image

COPY --from=builder /opt/poetry /opt/poetry
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . /app

EXPOSE 5000
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
