from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import verify_token
from services.ai_service import generate_response
from services.disagreement import compute_disagreement

router = APIRouter()


class InferenceRequest(BaseModel):
    provider: str
    model: str
    prompt: str
    system: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024


class ModelSpec(BaseModel):
    provider: str
    model: str
    system: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024


class BatchInferenceRequest(BaseModel):
    models: List[ModelSpec]
    rows: List[dict]   # each row is a free-form dict; the "prompt" field is used as the user prompt
    prompt_column: str = "content"  # which column to use as the user prompt


@router.post("/")
async def run_inference(
    req: InferenceRequest,
    token: dict = Depends(verify_token),
    x_openrouter_key: str = Header(None),
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
):
    try:
        response_text = await generate_response(
            provider=req.provider,
            model=req.model,
            prompt=req.prompt,
            system=req.system,
            temp=req.temperature,
            max_tokens=req.max_tokens,
            openrouter_key=x_openrouter_key,
            openai_key=x_openai_key,
            anthropic_key=x_anthropic_key,
        )
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def run_batch_inference(
    req: BatchInferenceRequest,
    token: dict = Depends(verify_token),
    x_openrouter_key: str = Header(None),
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
):
    """
    Run each model against every row concurrently.
    Returns per-row results with model outputs and a disagreement score.
    """
    async def infer_one(model: ModelSpec, prompt: str) -> str:
        try:
            return await generate_response(
                provider=model.provider,
                model=model.model,
                prompt=prompt,
                system=model.system,
                temp=model.temperature,
                max_tokens=model.max_tokens,
                openrouter_key=x_openrouter_key,
                openai_key=x_openai_key,
                anthropic_key=x_anthropic_key,
            )
        except Exception as e:
            return f"[Error: {e}]"

    results = []
    for row in req.rows:
        prompt = str(row.get(req.prompt_column, ""))
        # Run all models in parallel for this row
        outputs = await asyncio.gather(*[infer_one(m, prompt) for m in req.models])
        model_results = [
            {"model": m.model, "provider": m.provider, "output": out}
            for m, out in zip(req.models, outputs)
        ]
        disagreement = compute_disagreement([r["output"] for r in model_results])
        results.append({
            "row": row,
            "model_outputs": model_results,
            "disagreement": disagreement,
        })

    return {"results": results}
