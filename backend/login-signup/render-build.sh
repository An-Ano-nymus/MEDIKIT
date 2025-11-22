#!/usr/bin/env bash
set -euo pipefail

apt-get update
apt-get install -y tesseract-ocr poppler-utils

npm ci
