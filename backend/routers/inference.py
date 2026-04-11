from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def run_inference():
    return {}
