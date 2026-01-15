import os
from google import genai
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

    client = genai.Client(api_key=api_key)

    for model in client.models.list():
            print(f"Model: {model.name}")

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
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        return {"explanation": response.text, "source": "gemini-new-sdk"}
    except Exception as e:
        return {"explanation": f"Error: {str(e)}", "source": "error"}
        