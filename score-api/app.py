from flask import Flask, request, jsonify
import yaml
import re

app = Flask(__name__)

with open("policy.yaml", "r") as f:
    policies = yaml.safe_load(f)

@app.route("/score", methods=["POST"])
def score():
    data = request.json
    content = data.get("content", "")
    matches = []

    # Default risk baseline
    final_risk = "low"
    final_sensitivity = "none"
    final_action = "allow"

    risk_levels = {"low": 1, "medium": 2, "high": 3}
    action_priority = {"allow": 1, "flag": 2, "block": 3}

    for rule in policies.get("rules", []):
        if re.search(rule["pattern"], content, re.IGNORECASE):
            matches.append(rule["name"])
            if risk_levels[rule["risk"]] > risk_levels[final_risk]:
                final_risk = rule["risk"]
            if action_priority[rule["action"]] > action_priority[final_action]:
                final_action = rule["action"]
            if rule["sensitivity"] != "none":
                final_sensitivity = rule["sensitivity"]

    return jsonify({
        "risk": final_risk,
        "sensitivity": final_sensitivity,
        "action": final_action,
        "matches": matches
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070)
