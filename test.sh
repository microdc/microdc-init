#!/usr/bin/env bash

# Exit on any error
set -e

VENV_NAME=".venv"
if ! [ -e "${VENV_NAME}/bin/activate" ]; then
  echo "Creating virtualenv..."
  virtualenv  -p python3 ${VENV_NAME}
fi

source "${VENV_NAME}/bin/activate"

echo "Installing requirements..."
pip install -q -r requirements.txt -r requirements-tests.txt

echo "Cleaning .pyc files..."
find . -iname "*.pyc" -delete

echo "Running tests..."
python -m pytest tests/

echo "Running flake8..."
flake8 microdc/ tests/

echo "Done!!"
