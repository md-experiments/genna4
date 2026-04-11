from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import csv
import uuid
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import verify_token, db

router = APIRouter()


# ── helpers ──────────────────────────────────────────────────────────────────

def _user_datasets_ref(user_id: str):
    return db.collection("users").document(user_id).collection("datasets")


def _save_dataset(user_id: str, name: str, rows: List[Dict[str, Any]]) -> dict:
    """Create a dataset doc and batch-write its rows. Returns metadata dict."""
    dataset_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    metadata = {
        "id": dataset_id,
        "name": name,
        "row_count": len(rows),
        "owner_uid": user_id,
        "created_at": now,
    }

    dataset_ref = _user_datasets_ref(user_id).document(dataset_id)
    dataset_ref.set(metadata)

    # Batch-write rows (Firestore batch limit is 500)
    rows_ref = dataset_ref.collection("rows")
    for i in range(0, len(rows), 500):
        batch = db.batch()
        for row in rows[i : i + 500]:
            row_id = str(uuid.uuid4())
            batch.set(rows_ref.document(row_id), {"id": row_id, **row})
        batch.commit()

    return metadata


# ── endpoints ────────────────────────────────────────────────────────────────

@router.get("/")
def get_datasets(token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    docs = _user_datasets_ref(user_id).order_by("created_at", direction="DESCENDING").stream()
    return {"datasets": [doc.to_dict() for doc in docs]}


@router.get("/{dataset_id}/rows")
def get_dataset_rows(dataset_id: str, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    dataset_ref = _user_datasets_ref(user_id).document(dataset_id)
    if not dataset_ref.get().exists:
        raise HTTPException(status_code=404, detail="Dataset not found")
    rows = [doc.to_dict() for doc in dataset_ref.collection("rows").stream()]
    return {"rows": rows}


class ManualDataset(BaseModel):
    name: str
    rows: List[Dict[str, Any]]


@router.post("/create")
def create_dataset(dataset: ManualDataset, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    if not dataset.name.strip():
        raise HTTPException(status_code=400, detail="Dataset name is required")
    metadata = _save_dataset(user_id, dataset.name.strip(), dataset.rows)
    return {"message": "Success", "row_count": len(dataset.rows), "metadata": metadata}


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    content = await file.read()
    filename = file.filename.lower()
    rows = []

    if filename.endswith(".json"):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                rows = data.get("data", [data])
            else:
                rows = [{"content": str(data)}]
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file.")

    elif filename.endswith(".csv"):
        try:
            text_content = content.decode("utf-8-sig")
            reader = csv.DictReader(text_content.splitlines())
            rows = [row for row in reader]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid CSV file.")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .json or .csv")

    metadata = _save_dataset(user_id, file.filename, rows)
    return {"message": "Success", "row_count": len(rows), "metadata": metadata}


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    dataset_ref = _user_datasets_ref(user_id).document(dataset_id)
    if not dataset_ref.get().exists:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Delete all rows in the subcollection first
    rows_ref = dataset_ref.collection("rows")
    for i, doc in enumerate(rows_ref.stream()):
        if i % 500 == 0:
            batch = db.batch()
        batch.delete(doc.reference)
        if (i + 1) % 500 == 0:
            batch.commit()
    try:
        batch.commit()
    except UnboundLocalError:
        pass  # no rows existed

    dataset_ref.delete()
    return {"message": "Dataset deleted"}
