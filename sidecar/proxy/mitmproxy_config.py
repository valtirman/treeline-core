from mitmproxy import http
import json

def request(flow: http.HTTPFlow) -> None:
    if flow.request.path == "/healthz":
        flow.response = http.Response.make(
            200,
            json.dumps({"status": "ok"}),
            {"Content-Type": "application/json"}
        )
        return

