from flask import Flask, request, jsonify
import yaml

app = Flask(__name__)

with open("policy.yaml", "r") as f:
    policies = yaml.safe_load(f)

@app.route("/score", methods=["POST"])
def score():
    data = request.json
    response = {
        "risk": "medium",
        "sensitivity": "pii",
        "action": "allow"
    }
    for rule in policies.get("rules", []):
        if rule["match"] in data.get("content", ""):
            response["risk"] = rule["risk"]
            response["sensitivity"] = rule["sensitivity"]
            response["action"] = rule["action"]
            break
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070)
