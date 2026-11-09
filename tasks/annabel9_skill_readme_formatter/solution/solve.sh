#!/bin/bash
set -euo pipefail

cat > /app/README.md <<'MARKDOWN'
# My Python Project

## Description

A Python project. Built with Python 3.12.

## Installation

Install Python 3.12 and clone this project.

## Usage

Run the project's Python entry point.
MARKDOWN
