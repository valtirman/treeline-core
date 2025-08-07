from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Interaction(BaseModel):
    request: dict
    response: dict

@app.post("/score")
async def score(interaction: Interaction):
    req_body = interaction.request.get("body", "").lower()
    res_body = interaction.response.get("body", "").lower()
    score = 0

    if "jailbreak" in req_body or "jailbreak" in res_body:
        score = 90
    elif any(term in req_body for term in ["pii", "ssn", "ignore previous"]):
        score = 80
    elif any(term in res_body for term in ["pii", "ssn", "ignore previous"]):
        score = 80

    return {"score": score}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
