FROM python:3.12-slim-bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir pytest==9.1.1
RUN git config --global user.name "Mason" \
    && git config --global user.email "mason@example.com" \
    && git config --global init.defaultBranch main
WORKDIR /app
COPY README.md check_setup.py /app/
COPY weather /app/weather
# The eval repo ignores .env files, so the fake key is stored as `dotenv`.
COPY dotenv /app/.env
RUN printf '.env\n__pycache__/\n' > .gitignore \
    && git init -q \
    && git add -A \
    && git commit -q -m "Initial weather client"
