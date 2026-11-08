FROM python:3.12-slim-bookworm

RUN python -m pip install --no-cache-dir pytest==9.1.1

WORKDIR /app

COPY exporter.py /app/exporter.py
COPY .agents/skills /app/.agents/skills