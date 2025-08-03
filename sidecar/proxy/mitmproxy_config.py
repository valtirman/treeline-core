from mitmproxy import http
import json
import uuid
import requests

SCORING_API = "http://scorer:8000/score"
RISK_THRESHOLD = 80  # block anything at or above this score

class TreelineInterceptor:
    def request(self, flow: http.HTTPFlow):
        if "openai.com" in flow.request.pretty_host or "anthropic.com" in flow.request.pretty_host:
            flow.request.headers["X-Treeline-Request-ID"] = str(uuid.uuid4())

    def response(self, flow: http.HTTPFlow):
        if "openai.com" in flow.request.pretty_host or "anthropic.com" in flow.request.pretty_host:
            try:
                payload = {
                    "request": {
                        "method": flow.request.method,
                        "url": flow.request.pretty_url,
                        "headers": dict(flow.request.headers),
                        "body": flow.request.get_text()
                    },
                    "response": {
                        "status_code": flow.response.status_code,
                        "headers": dict(flow.response.headers),
                        "body": flow.response.get_text()
                    }
                }
                result = requests.post(SCORING_API, json=payload, timeout=2)
                score = result.json().get("score", 0)

                if score >= RISK_THRESHOLD:
                    flow.response.set_text("[Treeline Sidecar] ⚠️ Response blocked due to high risk score.")
                    flow.response.status_code = 403

            except Exception as e:
                print(f"[⚠️ Treeline] Scoring or enforcement failed: {e}")

addons = [TreelineInterceptor()]
