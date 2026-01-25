#!/bin/bash
set -e

rm -rf dist
mkdir -p dist

rm -rf layer/python/common/python
rm -rf layer/python/flask/python

mkdir -p layer/python/common/python
mkdir -p layer/python/flask/python

echo "Installing common dependencies..."
pip install --no-cache-dir -r requirements.txt -t layer/python/common/python

echo "Installing flask dependencies..."
pip install --no-cache-dir -r requirements_flask.txt -t layer/python/flask/python

echo "Creating zip archives..."
python -m zipfile -c dist/common-layer.zip layer/python/common/python
python -m zipfile -c dist/flask-layer.zip layer/python/flask/python

echo "✅ Layers built: dist/common-layer.zip and dist/flask-layer.zip"