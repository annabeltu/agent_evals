# Set up the project

## Install dependencies

Run `uv sync --locked` from the repository root to install the dependencies
recorded in the lockfile.

## Run local tests

Run `make test` to execute the host pytest suite. These tests do not require
Docker or model credentials.
