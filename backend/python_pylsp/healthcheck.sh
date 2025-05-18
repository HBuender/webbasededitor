#!/bin/sh
set -e

# First check if the process is running
if ! pgrep -f "python -m pylsp" > /dev/null; then
  echo "Python LSP Server process is not running"
  exit 1
fi

# Then check if the port is open
if nc -z localhost "$PYLSP_PORT"; then
  echo "Python LSP Server is running on port $PYLSP_PORT"
  exit 0
else
  echo "Python LSP Server is not available on port $PYLSP_PORT"
  exit 1
fi