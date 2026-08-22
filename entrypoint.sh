#!/bin/bash
RUN_PORT=${PORT:-8080}

exec uvicorn app.main:app --host 0.0.0.0 --port "${RUN_PORT}"
