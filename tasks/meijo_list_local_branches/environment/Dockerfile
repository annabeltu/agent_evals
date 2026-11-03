FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && python -m pip install --no-cache-dir pytest==9.1.1

WORKDIR /app/repo

RUN git init --initial-branch=main \
    && git config user.name "Task Author" \
    && git config user.email "task-author@example.com" \
    && git commit --allow-empty -m "Initialize branch practice repository" \
    && git branch branch1 \
    && git branch branch2 \
    && git branch branch3 \
    && git update-ref refs/remotes/origin/remote1 HEAD \
    && git update-ref refs/remotes/origin/remote2 HEAD
