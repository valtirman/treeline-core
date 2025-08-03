FROM python:3.10-slim

RUN pip install mitmproxy requests

COPY mitmproxy_config.py /app/mitmproxy_config.py

CMD ["mitmdump", "-p", "8080", "-s", "/app/mitmproxy_config.py"]
