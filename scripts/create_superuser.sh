#!/bin/sh
chmod +x ./scripts/create_superuser.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR" || exit 1

python3 -m src.scripts.create_superuser "$@"
