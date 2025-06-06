# syntax=docker/dockerfile:1

# Use an official Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy poetry files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Collect static files (optional, needed for prod deployments with whitenoise or similar)
RUN python manage.py collectstatic --noinput

# Port gunicorn will listen on
EXPOSE 8000

# Gunicorn command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
