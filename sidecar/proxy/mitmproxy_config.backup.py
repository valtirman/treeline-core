from mitmproxy import http
import requests
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger.exporter import emit_span

class TreelineInterceptor:
    def request(self, flow: http.HTTPFlow) -> None:
        # Health check passthrough
        if flow.request.path == "/healthz":
            flow.response = http.Response.make(
                200, b"ok", {"Content-Type": "text/plain"}
            )
            return

        if flow.request.method == "POST" and "application/json" in flow.request.headers.get("content-type", ""):
            content = flow.request.get_text()
            try:
                score = requests.post("http://scorer:8000/score", json={
                    "request": {"body": content},
                    "response": {"body": ""}
                }).json()

                flow.request.headers["X-Treeline-Risk"] = str(score["score"])
                flow.request.headers["X-Treeline-Sensitivity"] = "TBD"

                emit_span(
                    user_id=flow.request.headers.get("X-User-Id", "anon"),
                    model=flow.request.headers.get("X-Model", "unknown"),
                    prompt=content,
                    risk=str(score["score"]),
                    sensitivity="TBD"
                )

                # BLOCK if score ≥ 80
                if score["score"] >= 80:
                    flow.response = http.Response.make(
                        403,
                        b"LLM request blocked by Treeline: high-risk content",
                        {"Content-Type": "text/plain"}
                    )
            except Exception as e:
                flow.request.headers["X-Treeline-Error"] = "scoring-failed"

addons = [TreelineInterceptor()]
