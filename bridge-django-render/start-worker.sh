#!/usr/bin/env bash
celery -A bridge.service.django_celery worker -l INFO --concurrency="${TASK_CONCURRENCY:-4}"
