from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import auth
import os

try:
    firebase_admin.get_app()
except ValueError:
    try:
        firebase_admin.initialize_app()
    except Exception as e:
        print("Warning: Firebase not fully initialized:", e)

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed")
