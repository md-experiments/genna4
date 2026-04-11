from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import verify_token, db

router = APIRouter()


def _annotations_ref(user_id: str, dataset_id: str):
    return (
        db.collection("users")
        .document(user_id)
        .collection("datasets")
        .document(dataset_id)
        .collection("annotations")
    )


@router.get("/")
def get_annotations(dataset_id: str, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    docs = _annotations_ref(user_id, dataset_id).stream()
    return {"annotations": [doc.to_dict() for doc in docs]}


class AnnotationCreate(BaseModel):
    dataset_id: str
    row_id: str
    model_config_id: Optional[str] = None
    response_text: str


@router.post("/")
def create_annotation(payload: AnnotationCreate, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    annotation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": annotation_id,
        "dataset_id": payload.dataset_id,
        "row_id": payload.row_id,
        "model_config_id": payload.model_config_id,
        "annotator_user_id": user_id,
        "response_text": payload.response_text,
        "thumbs_up": None,
        "feedback_text": None,
        "created_at": now,
    }

    _annotations_ref(user_id, payload.dataset_id).document(annotation_id).set(doc)
    return {"annotation": doc}


class AnnotationFeedback(BaseModel):
    thumbs_up: Optional[bool] = None
    feedback_text: Optional[str] = None


@router.patch("/{dataset_id}/{annotation_id}")
def update_annotation(
    dataset_id: str,
    annotation_id: str,
    payload: AnnotationFeedback,
    token: dict = Depends(verify_token),
):
    user_id = token.get("uid")
    ref = _annotations_ref(user_id, dataset_id).document(annotation_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Annotation not found")

    update = {}
    if payload.thumbs_up is not None:
        update["thumbs_up"] = payload.thumbs_up
    if payload.feedback_text is not None:
        update["feedback_text"] = payload.feedback_text

    if update:
        ref.update(update)

    return {"message": "Updated"}
