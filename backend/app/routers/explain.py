import os
import google.generativeai as genai
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Union

router = APIRouter()

class ExplainRequest(BaseModel):
    permissions: List[Union[str, list]]
    language: str = "English"

@router.post("/")
def explain_with_gemini(req: ExplainRequest):
    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"explanation": "API Key not found.", "source": "error"}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')

    # Simple list of permissions for the prompt
    clean_perms = ", ".join([str(p) for p in req.permissions])

    # Prompt designed for elderly safety
    prompt = (
        f"You are a helpful cybersecurity assistant for elderly people. "
        f"Explain in very simple {req.language} what these Android permissions do "
        f"and if they could be used for a scam or fraud. Be very clear and encouraging. "
        f"\n\nPermissions: {clean_perms}"
    )

    try:
        response = model.generate_content(prompt)
        return {"explanation": response.text, "source": "gemini"}
    except Exception as e:
        return {"explanation": f"Error: {str(e)}", "source": "error"}
