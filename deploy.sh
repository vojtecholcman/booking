#!/bin/bash
set -e

PROJ="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJ"

echo "==> git pull"
git pull

echo "==> pip install"
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "==> restart"
systemctl restart korova-chata

echo "==> cekam na start..."
sleep 2
systemctl is-active --quiet korova-chata && echo "OK — korova-chata bezi" || { echo "CHYBA — service nesla spustit"; systemctl status korova-chata --no-pager; exit 1; }
