FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pytest python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pricing.py /app/pricing.py
COPY report.py /app/report.py
