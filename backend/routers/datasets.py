from fastapi import APIRouter, Depends
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
