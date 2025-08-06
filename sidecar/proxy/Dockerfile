# Dockerfile (sidecar/proxy/Dockerfile)
FROM python:3.10-slim

WORKDIR /app

# Install mitmproxy and requests
RUN pip install mitmproxy requests

# Copy config and logger directory
COPY mitmproxy_config.py /app/mitmproxy_config.py
COPY logger /app/logger
HEALTHCHECK CMD curl -f http://localhost:8080/healthz || exit 1
CMD ["mitmdump", "-s", "/app/mitmproxy_config.py", "--set", "block_global=false", "--mode", "regular"]

