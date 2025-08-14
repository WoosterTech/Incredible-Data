
ENV_RUN := poetry run
DJANGO_MANAGE := $(ENV_RUN) python manage.py
PYTHON := $(ENV_RUN) python

.PHONY: help runserver migrate makemigrations test pytest-coverage lint format collectstatic shell

help:
	@echo "Common Django project commands:"
	@echo "  make runserver        # Start Django development server"
	@echo "  make migrate          # Apply database migrations"
	@echo "  make makemigrations   # Create new migrations"
	@echo "  make test             # Run all tests"
	@echo "  make pytest-coverage  # Run tests with coverage (HTML report)"
	@echo "  make lint             # Run ruff linting"
	@echo "  make format           # Auto-format code with ruff"
	@echo "  make collectstatic    # Collect static files"
	@echo "  make shell            # Open Django shell"

runserver:
	$(DJANGO_MANAGE) runserver

migrate:
	$(DJANGO_MANAGE) migrate

makemigrations:
	$(DJANGO_MANAGE) makemigrations

test:
	$(ENV_RUN) pytest

coverage:
	$(ENV_RUN) coverage run -m pytest
	$(ENV_RUN) coverage html

lint:
	$(ENV_RUN) ruff check .

format:
	$(ENV_RUN) ruff format .

collectstatic:
	$(DJANGO_MANAGE) collectstatic --noinput

shell:
	$(DJANGO_MANAGE) shell

precommit:
	$(ENV_RUN) pre-commit run

deptrycheck:
	$(ENV_RUN) deptry .
