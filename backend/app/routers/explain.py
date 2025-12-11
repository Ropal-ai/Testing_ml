from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import os as _os

# You can use OpenAI or another LLM. This file demonstrates using OpenAI API if available.
# If you don't have an API key, the endpoint will return rule-based explanation.

try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

router = APIRouter()

class ExplainRequest(BaseModel):
    permissions: list

def rules_explain(permissions):
    explanations = []
    for p in permissions:
        explanations.append(f"- {p}: {PERM_EXPLAIN.get(p, 'Permission detected. Review before install.')}")
    return "\n".join(explanations)

# simple permission meanings; extend as you like
PERM_EXPLAIN = {
    "READ_SMS": "Can read your SMS messages (privacy risk).",
    "SEND_SMS": "Can send SMS messages (cost/data abuse).",
    "RECORD_AUDIO": "Can record audio via microphone.",
    "ACCESS_FINE_LOCATION": "Can access GPS location (track you).",
    "READ_CONTACTS": "Can read your contacts (data leakage).",
    "WRITE_EXTERNAL_STORAGE": "Can modify files on external storage.",
}

@router.post("/")
def explain(req: ExplainRequest):
    perms = req.permissions or []
    if len(perms) == 0:
        raise HTTPException(status_code=400, detail="No permissions provided")

    # Prefer LLM explanation when key and package present
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = (
            "You are a cybersecurity expert. Explain in simple language "
            "the risks of the following Android permissions and give a final advice.\n\n"
            f"Permissions:\n{perms}\n\nFormat:\n1) Summary\n2) Risks\n3) Recommendation"
        )
        try:
            resp = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role":"user","content":prompt}],
                max_tokens=400
            )
            text = resp['choices'][0]['message']['content']
            return {"explanation": text, "source": "openai"}
        except Exception as e:
            # fallback to rules
            pass

    # simple rule-based fallback
    return {"explanation": rules_explain(perms), "source": "rules"}
