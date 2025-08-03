from mitmproxy import http
import requests
import json

class TreelineInterceptor:
    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.method == "POST" and "application/json" in flow.request.headers.get("content-type", ""):
            content = flow.request.get_text()
            score = requests.post("http://score-api:7070/score", json={"content": content}).json()
            flow.request.headers["X-Treeline-Risk"] = score["risk"]
            flow.request.headers["X-Treeline-Sensitivity"] = score["sensitivity"]
            if score["action"] == "block":
                flow.response = http.HTTPResponse.make(
                    403, b"LLM response redacted by Treeline", {"Content-Type": "text/plain"}
                )

addons = [TreelineInterceptor()]
