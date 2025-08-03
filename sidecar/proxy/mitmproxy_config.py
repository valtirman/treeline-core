from mitmproxy import http
import requests
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger.exporter import emit_span

class TreelineInterceptor:
    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.method == "POST" and "application/json" in flow.request.headers.get("content-type", ""):
            content = flow.request.get_text()
            try:
                score = requests.post("http://score-api:7070/score", json={"content": content}).json()
                flow.request.headers["X-Treeline-Risk"] = score["risk"]
                flow.request.headers["X-Treeline-Sensitivity"] = score["sensitivity"]

                # Emit span
                emit_span(
                    user_id=flow.request.headers.get("X-User-Id", "anon"),
                    model=flow.request.headers.get("X-Model", "unknown"),
                    prompt=content,
                    risk=score["risk"],
                    sensitivity=score["sensitivity"]
                )

                if score["action"] == "block":
                    flow.response = http.HTTPResponse.make(
                        403, b"LLM response redacted by Treeline", {"Content-Type": "text/plain"}
                    )
            except Exception as e:
                flow.request.headers["X-Treeline-Error"] = "scoring-failed"

addons = [TreelineInterceptor()]
