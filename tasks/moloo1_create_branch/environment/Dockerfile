FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir pytest==9.1.1

RUN git config --global user.name "Task Author" \
    && git config --global user.email "author@example.com" \
    && git config --global init.defaultBranch main

WORKDIR /app
COPY README.md /app/README.md
RUN git init \
    && git add README.md \
    && git commit -m "Initial commit"
