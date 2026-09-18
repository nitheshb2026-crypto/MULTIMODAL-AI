import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import init_db
from backend.routes.patients import router as patients_router
from backend.routes.clinical import router as clinical_router
from backend.routes.inference import router as inference_router
from backend.routes.assistant import router as assistant_router

app = FastAPI(
    title="Multimodal AI Health Assistant API",
    description="Clinical decision-support API combining Tabular ML, 1D ECG, Chest X-rays, and CT Medical Images with Gemini AI.",
    version="1.0.0"
)

# Enable CORS for local Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount routes
app.include_router(patients_router)
app.include_router(clinical_router)
app.include_router(inference_router)
app.include_router(assistant_router)

# Mount static file directory for data preview if exists
data_dir = os.path.join(BASE_DIR, "data")
if os.path.exists(data_dir):
    app.mount("/static/data", StaticFiles(directory=data_dir), name="data")

@app.get("/")
def root():
    return {
        "system": "Multimodal AI Health Assistant API",
        "status": "online",
        "docs_url": "/docs",
        "modalities": ["Tabular Heart Disease", "Tabular Stroke", "1D ECG (MLII)", "Chest X-Ray", "CT DICOM"],
        "assistant": "Google Gemini 1.5 Clinical Grounding"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
