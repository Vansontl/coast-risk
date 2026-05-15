#!/bin/sh
set -e

mkdir -p "$STORAGE_DIR" "$MODEL_DIR" "$REPORT_DIR" "$UPLOAD_DIR" "$STORAGE_DIR/templates"

if [ -d /app/bootstrap_templates ]; then
  cp -n /app/bootstrap_templates/* "$STORAGE_DIR/templates/" 2>/dev/null || true
fi

exec "$@"
