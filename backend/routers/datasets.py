from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import verify_token

router = APIRouter()

@router.get("/")
def get_datasets(token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    # The database path will securely enforce multi-tenancy:
    # return db.collection('users').document(user_id).collection('datasets').get()
    return {"user_id": user_id, "datasets": []}

class ManualDataset(BaseModel):
    name: str
    rows: List[Dict[str, Any]]

@router.post("/create")
def create_dataset(dataset: ManualDataset, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    
    dataset_metadata = {
        "name": dataset.name,
        "row_count": len(dataset.rows),
        "owner_uid": user_id
    }
    
    return {"message": "Success", "row_count": len(dataset.rows), "metadata": dataset_metadata}

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
        
    dataset_metadata = {
        "name": file.filename,
        "row_count": len(rows),
        "owner_uid": user_id
    }
    
    # Example Firestore Integration (stubbed):
    # db.collection('users').document(user_id).collection('datasets').add(dataset_metadata)
    # (then batch write the rows)
    
    return {"message": "Success", "row_count": len(rows), "metadata": dataset_metadata}
