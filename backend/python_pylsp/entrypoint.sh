#!/bin/sh
set -e

echo "Starting Python LSP Server on $PYLSP_HOST:$PYLSP_PORT..."

# Disable check-parent-process as it can cause issues in Docker
exec python -m pylsp --tcp --host "$PYLSP_HOST" --port "$PYLSP_PORT" --verbose