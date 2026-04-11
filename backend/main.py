from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import datasets, annotations, inference

app = FastAPI(title="Genna API", description="Backend for Genna Annotation System")

# Enable CORS for the frontend
# In production the frontend Caddy proxy forwards requests internally, so the
# browser never makes a cross-origin call and CORS is not needed.  This list
# covers local development only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["Annotations"])
app.include_router(inference.router, prefix="/api/inference", tags=["Inference"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
