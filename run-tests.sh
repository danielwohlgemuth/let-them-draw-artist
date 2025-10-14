#!/bin/sh
uv run coverage run --source=src -m pytest tests/
uv run coverage html -d coverage_report