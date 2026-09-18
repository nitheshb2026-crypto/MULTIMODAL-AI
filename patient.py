from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PatientCreate(BaseModel):
    ap_number: str = Field(..., description="Unique Patient / AP Number e.g. AP-1006")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, le=130, description="Age in years")
    gender: str = Field(..., description="Gender (Male, Female, Other)")
    blood_group: Optional[str] = "O+"
    phone: Optional[str] = ""
    notes: Optional[str] = ""

class PatientResponse(BaseModel):
    id: int
    ap_number: str
    name: str
    age: int
    gender: str
    blood_group: Optional[str] = "O+"
    phone: Optional[str] = ""
    notes: Optional[str] = ""
    created_at: Optional[str] = ""

class TabularHeartRecord(BaseModel):
    age: Optional[int] = None
    sex: Optional[int] = None
    cp: Optional[int] = None
    trestbps: Optional[int] = None
    chol: Optional[int] = None
    fbs: Optional[int] = None
    restecg: Optional[int] = None
    thalach: Optional[int] = None
    exang: Optional[int] = None
    oldpeak: Optional[float] = None
    slope: Optional[int] = None
    ca: Optional[int] = None
    thal: Optional[int] = None
    target: Optional[int] = None

class TabularStrokeRecord(BaseModel):
    hypertension: Optional[int] = None
    heart_disease: Optional[int] = None
    ever_married: Optional[str] = None
    work_type: Optional[str] = None
    residence_type: Optional[str] = None
    avg_glucose_level: Optional[float] = None
    bmi: Optional[float] = None
    smoking_status: Optional[str] = None
    stroke: Optional[int] = None

class ModelPrediction(BaseModel):
    modality: str
    model_name: str
    prediction_label: str
    confidence: float
    evidence_summary: str
    probabilities: Optional[Dict[str, float]] = None
    timestamp: Optional[str] = None

class AssistantQuery(BaseModel):
    patient_id: int
    question: str
    gemini_api_key: Optional[str] = None

class AssistantResponse(BaseModel):
    patient_id: int
    question: str
    answer: str
    evidence_used: List[str]
    disclaimer: str
