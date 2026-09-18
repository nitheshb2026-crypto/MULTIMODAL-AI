from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database.db import search_patients, get_patient_by_id, get_patient_full_profile, create_patient, get_patient_by_ap
from backend.schemas.patient import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("", response_model=List[PatientResponse])
def list_patients(
    query: Optional[str] = Query(None, description="Search by name or AP Number"),
    ap_number: Optional[str] = Query(None, description="Exact or partial AP Number"),
    min_age: Optional[int] = Query(None, description="Minimum age filter"),
    max_age: Optional[int] = Query(None, description="Maximum age filter"),
    gender: Optional[str] = Query(None, description="Gender filter: Male, Female, Other")
):
    results = search_patients(
        query=query,
        ap_number=ap_number,
        min_age=min_age,
        max_age=max_age,
        gender=gender
    )
    return results

@router.post("", response_model=PatientResponse, status_code=201)
def register_patient(payload: PatientCreate):
    existing = get_patient_by_ap(payload.ap_number)
    if existing:
        raise HTTPException(status_code=400, detail=f"Patient with AP Number '{payload.ap_number}' already exists.")
    
    patient_id = create_patient(
        ap_number=payload.ap_number,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        blood_group=payload.blood_group or "O+",
        phone=payload.phone or "",
        notes=payload.notes or ""
    )
    new_patient = get_patient_by_id(patient_id)
    if not new_patient:
        raise HTTPException(status_code=500, detail="Failed to retrieve registered patient.")
    return new_patient

@router.get("/{patient_id}")
def get_patient_profile(patient_id: int):
    profile = get_patient_full_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found.")
    return profile
