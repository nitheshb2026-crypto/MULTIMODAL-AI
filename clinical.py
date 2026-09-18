import os
import io
import json
import scipy.io
import numpy as np
from fastapi import APIRouter, HTTPException
from database.db import get_patient_full_profile, get_connection
from backend.config import BASE_DIR

router = APIRouter(prefix="/api/clinical", tags=["Clinical Data"])

@router.get("/ecg/{patient_id}")
def get_patient_ecg(patient_id: int):
    profile = get_patient_full_profile(patient_id)
    if not profile or not profile.get("ecg_record"):
        raise HTTPException(status_code=404, detail="No ECG record found for this patient.")
    
    ecg_meta = profile["ecg_record"]
    rel_path = ecg_meta["file_path"]
    full_path = os.path.join(BASE_DIR, rel_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"ECG file not found on disk: {rel_path}")
    
    try:
        mat_data = scipy.io.loadmat(full_path)
        val_arr = mat_data.get("val")
        if val_arr is None:
            raise ValueError("No 'val' key found in .mat ECG file.")
        
        # val_arr is shape (1, 3600)
        signal_1d = val_arr.flatten().tolist()
        
        # Subsample or provide 1000 points for smooth interactive plotting
        sampling_rate = ecg_meta.get("sampling_rate", 360)
        total_points = len(signal_1d)
        duration_sec = total_points / sampling_rate
        time_vector = [round(i / sampling_rate, 4) for i in range(total_points)]
        
        return {
            "patient_id": patient_id,
            "rhythm_class": ecg_meta.get("rhythm_class"),
            "lead": ecg_meta.get("lead", "MLII"),
            "sampling_rate": sampling_rate,
            "duration_seconds": duration_sec,
            "total_points": total_points,
            "signal": signal_1d,
            "time_axis": time_vector,
            "file_path": rel_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing ECG .mat file: {str(e)}")

@router.get("/imaging/{patient_id}")
def get_patient_imaging(patient_id: int):
    profile = get_patient_full_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    records = profile.get("imaging_records", [])
    results = []
    for r in records:
        meta = {}
        if r.get("metadata_json"):
            try:
                meta = json.loads(r["metadata_json"])
            except:
                meta = {}
        results.append({
            "id": r["id"],
            "modality": r["modality"],
            "file_path": r["file_path"],
            "ground_truth": r["ground_truth"],
            "metadata": meta,
            "recorded_at": r["recorded_at"]
        })
    return {"patient_id": patient_id, "imaging_records": results}
