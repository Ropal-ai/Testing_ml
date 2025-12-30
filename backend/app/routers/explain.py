from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Union
import os
import logging

# Setup Logger
logger = logging.getLogger(__name__)

# Check for OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not found. Falling back to rule-based explanations.")

router = APIRouter()

class ExplainRequest(BaseModel):
    permissions: List[Union[str, list]] # Allow flexible input, clean it later
    language: str = "English"

def rules_explain(permissions):
    explanations = []
    for p in permissions:
        # FIX 2: Handle cases where p might accidentally be a list (e.g. ['READ_SMS'])
        if isinstance(p, list):
            p = p[0] if p else "UNKNOWN"
            
        explanations.append(f"- {p}: {PERM_EXPLAIN.get(str(p), 'Permission detected. Review before install.')}")
    return "\n".join(explanations)

# Simple permission meanings
PERM_EXPLAIN = {
    "READ_SMS": "Can read your SMS messages (privacy risk).",
    "SEND_SMS": "Can send SMS messages (cost/data abuse).",
    "RECORD_AUDIO": "Can record audio via microphone.",
    "ACCESS_FINE_LOCATION": "Can access GPS location (track you).",
    "READ_CONTACTS": "Can read your contacts (data leakage).",
    "WRITE_EXTERNAL_STORAGE": "Can modify files on external storage.",
    "READ_EXTERNAL_STORAGE": "Can read files from external storage.",
    "CAMERA": "Can access the camera to take photos/video.",
}

@router.post("/")
def explain(req: ExplainRequest):
    raw_perms = req.permissions or []
    
    # FIX 3: Sanitize the list to ensure it's flat strings
    clean_perms = []
    for p in raw_perms:
        if isinstance(p, list):
            clean_perms.append(str(p[0]))
        else:
            clean_perms.append(str(p))
            
    if len(clean_perms) == 0:
        raise HTTPException(status_code=400, detail="No permissions provided")

    # Prefer LLM explanation
    api_key = os.getenv("OPENAI_API_KEY")
    
    if OPENAI_AVAILABLE and api_key:
        try:
            client = OpenAI(api_key=api_key)
            
            prompt = (
                f"You are a cybersecurity expert. Explain in simple {req.language} language "
                "the risks of the following Android permissions and give a final advice.\n\n"
                f"Permissions:\n{clean_perms}\n\nFormat:\n1) Summary\n2) Risks\n3) Recommendation"
            )
            
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            
            # Access response attributes (not dictionary keys)
            text = resp.choices[0].message.content
            return {"explanation": text, "source": "openai"}
            
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            # fall through to rule-based on error

    # Fallback to rule-based
    return {"explanation": rules_explain(clean_perms), "source": "rules"}