FROM python:3.12-slim-bookworm
# The verifier uses openssl to make a self-signed certificate like the campus proxy's.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir pytest==9.1.1
WORKDIR /app
COPY fetcher.py /app/fetcher.py
