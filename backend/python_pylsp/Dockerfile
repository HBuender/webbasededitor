FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    netcat-traditional \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python LSP Server and useful plugins
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    'python-lsp-server[all]' \
    pylsp-mypy \
    pylsp-rope \
    python-lsp-black==1.3.0 \
    python-lsp-isort \
    python-lsp-ruff \
    jedi>=0.17.2 \
    rope \
    pyflakes \
    mccabe \
    pycodestyle \
    black==23.3.0 \
    mypy \
    isort \
    ruff

# Copy configuration files
COPY pylsp_config.json /app/pylsp_config.json
COPY healthcheck.sh /app/healthcheck.sh
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/healthcheck.sh /app/entrypoint.sh

# Create workspace directory and add a pyproject.toml file for Black configuration
RUN mkdir -p /app/workspace
COPY pyproject.toml /app/workspace/pyproject.toml

# Environment variables
ENV PYLSP_PORT=3000
ENV PYLSP_HOST=0.0.0.0
ENV PYLSP_CHECK_PARENT_PROCESS=false

# Expose the port
EXPOSE 3000

# Set up health check
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD /app/healthcheck.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]