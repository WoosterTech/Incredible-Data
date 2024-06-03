#!/usr/bin/env bash
gunicorn config.asgi:application -w "${WEB_CONCURRENCY:-4}" -b 0.0.0.0:"$PORT" -k uvicorn.workers.UvicornWorker
