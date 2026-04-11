from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import generate_response

router = APIRouter()

class InferenceRequest(BaseModel):
    provider: str
    model: str
    prompt: str
    system: str = None
    temperature: float = 0.7

@router.post("/")
async def run_inference(
    req: InferenceRequest,
    x_openrouter_key: str = Header(None),
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None)
):
    try:
        response_text = await generate_response(
            provider=req.provider,
            model=req.model,
            prompt=req.prompt,
            system=req.system,
            temp=req.temperature,
            openrouter_key=x_openrouter_key,
            openai_key=x_openai_key,
            anthropic_key=x_anthropic_key
        )
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
