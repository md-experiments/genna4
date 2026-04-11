from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import auth, credentials
import os
import json

try:
    firebase_admin.get_app()
except ValueError:
    creds_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    try:
        if creds_env:
            # Load raw JSON from env variable
            cert = json.loads(creds_env)
            cred = credentials.Certificate(cert)
            firebase_admin.initialize_app(cred)
        else:
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
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
