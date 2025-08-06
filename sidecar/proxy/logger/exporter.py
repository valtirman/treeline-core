import json
import os
from datetime import datetime

LOG_PATH = os.environ.get("TREELINE_LOG_PATH", "telemetry.log")

def emit_span(user_id, model, prompt, risk, sensitivity):
    span = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "model": model,
        "prompt": prompt,
        "risk": risk,
        "sensitivity": sensitivity
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(span) + "\n")
