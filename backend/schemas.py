from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Dataset(BaseModel):
    id: str
    name: str
    row_count: int
    created_at: str

class DatasetRow(BaseModel):
    id: str
    dataset_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class AIModelConfig(BaseModel):
    id: str
    provider: str # "openai", "anthropic", "openrouter"
    model_name: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7

class DisagreementScore(BaseModel):
    has_disagreement: bool
    score: float

class Annotation(BaseModel):
    id: str
    row_id: str
    dataset_id: str
    model_config_id: Optional[str] = None
    annotator_user_id: Optional[str] = None
    response_text: str
    thumbs_up: Optional[bool] = None
    feedback_text: Optional[str] = None
