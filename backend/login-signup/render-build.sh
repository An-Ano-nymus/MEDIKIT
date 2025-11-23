#!/usr/bin/env bash
set -euo pipefail

if command -v apt-get >/dev/null 2>&1 && [ -w /var/lib/apt/lists/ ]; then
	echo "Installing OCR binaries via apt..."
	apt-get update
	apt-get install -y tesseract-ocr poppler-utils
else
	echo "Skipping apt install (missing permissions). Falling back to EasyOCR pipeline."
fi

npm ci
