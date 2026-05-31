#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright Chromium browser..."
python -m playwright install chromium --with-deps

echo "Build complete."
