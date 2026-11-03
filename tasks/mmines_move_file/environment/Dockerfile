FROM python:3.12-slim-bookworm
RUN python -m pip install --no-cache-dir pytest==9.1.1
WORKDIR /app
COPY run.sh /app/run.sh
COPY solution/solve.sh /app/solution/solve.sh
