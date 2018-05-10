#!/usr/bin/env bash

# Exit on any error
set -e

echo "Installing/updating requirements"
pipenv install -d

echo "Cleaning .pyc files..."
find . -iname "*.pyc" -delete

echo "Running flake8 to check python style..."
pipenv run flake8 --ignore=F401 microdc/ tests/

echo "Running tests..."
pipenv run python -m pytest tests/

echo "Done!!"
