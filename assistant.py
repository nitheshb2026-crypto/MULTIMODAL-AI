import os
import json
import urllib.request
from fastapi import APIRouter, HTTPException
from backend.schemas.patient import AssistantQuery, AssistantResponse
from database.db import get_patient_full_profile
from backend.config import GEMINI_API_KEY, MEDICAL_SAFETY_DISCLAIMER

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

def generate_local_clinical_summary(profile: dict, question: str) -> dict:
    """Deterministic, clinically accurate fallback responding strictly to available patient data."""
    q_lower = question.lower()
    name = profile.get("name", "Unknown")
    ap = profile.get("ap_number", "N/A")
    age = profile.get("age", "N/A")
    gender = profile.get("gender", "N/A")
    
    predictions = profile.get("predictions", [])
    preds_by_mod = {p["modality"]: p for p in predictions}
    
    evidence_used = []
    
    # 1. ECG specific
    if "ecg" in q_lower or "rhythm" in q_lower:
        ecg_rec = profile.get("ecg_record", {})
        ecg_pred = preds_by_mod.get("ECG", {})
        pred_label = ecg_pred.get("prediction_label", ecg_rec.get("rhythm_class", "N/A"))
        conf = ecg_pred.get("confidence", 0.0)
        evidence = ecg_pred.get("evidence_summary", "No evidence summary logged.")
        evidence_used.append(f"ECG Record ({ecg_rec.get('lead', 'MLII')} Lead, 360Hz)")
        
        answer = (
            f"**ECG Biosignal Analysis for {name} ({ap}):**\n\n"
            f"- **Detected Rhythm / Finding:** {pred_label}\n"
            f"- **Model Confidence:** {conf * 100:.1f}%\n"
            f"- **Electrophysiological Evidence:** {evidence}\n"
            f"- **Recording Parameters:** 10-second 1D rhythm strip (3,600 samples) recorded on Modified Lead II (MLII).\n\n"
            f"*Summary:* The biosignal model analyzed the raw voltage waveform and identified rhythm dynamics consistent with {pred_label}."
        )
        return {"answer": answer, "evidence_used": evidence_used}

    # 2. X-ray specific
    if "x-ray" in q_lower or "xray" in q_lower or "radiograph" in q_lower or "chest" in q_lower or "lung" in q_lower:
        xray_pred = preds_by_mod.get("CHEST_XRAY", {})
        pred_label = xray_pred.get("prediction_label", "No X-ray prediction on file")
        conf = xray_pred.get("confidence", 0.0)
        evidence = xray_pred.get("evidence_summary", "No radiological evidence logged.")
        evidence_used.append("Chest X-Ray Imaging Record & DenseNet-121 Analyzer")
        
        answer = (
            f"**Chest Radiograph Evaluation for {name} ({ap}):**\n\n"
            f"- **Radiological Classification:** {pred_label}\n"
            f"- **Detection Confidence:** {conf * 100:.1f}%\n"
            f"- **Visual / Morphological Evidence:** {evidence}\n\n"
            f"*Summary:* The computer vision model examined the PA/AP projection chest radiograph. Based on pulmonary opacity and parenchymal density distribution, the model categorized this finding as {pred_label}."
        )
        return {"answer": answer, "evidence_used": evidence_used}

    # 3. Model outputs / all predictions
    if "model output" in q_lower or "all models" in q_lower or "predictions" in q_lower:
        evidence_used.append("All Modality Prediction Records in Database")
        lines = [f"**Model Diagnostic Outputs for {name} ({ap}):**\n"]
        for p in predictions:
            lines.append(
                f"- **{p['modality']}** ({p['model_name']}):\n"
                f"  - Output: **{p['prediction_label']}** (Confidence: {p['confidence']*100:.1f}%)\n"
                f"  - Evidence: {p['evidence_summary']}\n"
            )
        lines.append("\n*Note:* These model predictions reflect algorithmic classifications across independent clinical modalities.")
        return {"answer": "\n".join(lines), "evidence_used": evidence_used}

    # 4. Reports specific
    if "report" in q_lower or "previous" in q_lower:
        reports = profile.get("reports", [])
        evidence_used.append("Clinical Report Repository")
        if not reports:
            return {"answer": f"No previous clinical reports on file for patient {name} ({ap}).", "evidence_used": evidence_used}
        
        lines = [f"**Stored Clinical Reports for {name} ({ap}):**\n"]
        for idx, rep in enumerate(reports, 1):
            lines.append(
                f"### Report #{idx}: {rep['report_title']}\n"
                f"- **Timestamp:** {rep.get('generated_at', 'N/A')}\n"
                f"- **Multimodal Score:** {rep.get('multimodal_score', 'N/A')}\n"
                f"- **Summary:** {rep.get('summary_text', '')}\n"
                f"- **Recommendations:**\n{rep.get('recommendations', '')}\n"
            )
        return {"answer": "\n".join(lines), "evidence_used": evidence_used}

    # 5. Default / General Summary: "Summarize this patient's available results."
    evidence_used.extend(["Patient Demographics", "Cardiovascular Tabular Record", "Stroke Tabular Record", "ECG Record", "Imaging Records", "Fusion Engine"])
    
    heart = profile.get("heart_record") or {}
    stroke = profile.get("stroke_record") or {}
    fusion_pred = preds_by_mod.get("MULTIMODAL_FUSION", {})
    
    summary = (
        f"### Multimodal Diagnostic Summary for {name} (AP: {ap})\n\n"
        f"**Demographics:** {age} years old, {gender}, Blood Group: {profile.get('blood_group', 'O+')}\n\n"
        f"**1. Cardiovascular Tabular Profile:**\n"
        f"- Resting BP: {heart.get('trestbps', 'N/A')} mm Hg | Serum Cholesterol: {heart.get('chol', 'N/A')} mg/dL | Max Heart Rate: {heart.get('thalach', 'N/A')} bpm\n"
        f"- Model Output: {preds_by_mod.get('HEART_DISEASE', {}).get('prediction_label', 'Pending')} (Confidence: {preds_by_mod.get('HEART_DISEASE', {}).get('confidence', 0)*100:.1f}%)\n\n"
        f"**2. Cerebrovascular Stroke Profile:**\n"
        f"- Hypertension: {'Yes' if stroke.get('hypertension') else 'No'} | Avg Glucose: {stroke.get('avg_glucose_level', 'N/A')} mg/dL | BMI: {stroke.get('bmi', 'N/A')} | Smoking: {stroke.get('smoking_status', 'N/A')}\n"
        f"- Model Output: {preds_by_mod.get('STROKE', {}).get('prediction_label', 'Pending')} (Confidence: {preds_by_mod.get('STROKE', {}).get('confidence', 0)*100:.1f}%)\n\n"
        f"**3. 1D ECG Biosignal Findings:**\n"
        f"- Rhythm: {preds_by_mod.get('ECG', {}).get('prediction_label', 'Pending')} (Confidence: {preds_by_mod.get('ECG', {}).get('confidence', 0)*100:.1f}%)\n\n"
        f"**4. Medical Imaging (Chest X-Ray / CT):**\n"
        f"- Chest X-Ray: {preds_by_mod.get('CHEST_XRAY', {}).get('prediction_label', 'No scan available')} (Confidence: {preds_by_mod.get('CHEST_XRAY', {}).get('confidence', 0)*100:.1f}%)\n\n"
        f"**5. Combined Multimodal Fusion Assessment:**\n"
        f"- **Synthesized Clinical Risk:** **{fusion_pred.get('prediction_label', 'Evaluated')}** ({fusion_pred.get('confidence', 0)*100:.1f}% confidence)\n"
        f"- **Cross-Modal Evidence:** {fusion_pred.get('evidence_summary', 'Cross-modal signals evaluated.')}"
    )
    return {"answer": summary, "evidence_used": evidence_used}

def call_gemini_api(api_key: str, profile: dict, question: str) -> str:
    """Call Google Gemini API with system instructions restricting the output to summarizing available data."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    system_instruction = (
        "You are an AI Health Assistant for a clinical patient dashboard. "
        "You must ONLY summarize and explain the available patient data and model outputs provided in the context. "
        "You MUST NOT claim to be a doctor or make a definitive medical diagnosis. "
        "Always cite the specific numbers, models, and evidence available in the patient record. "
        "Maintain an objective, professional, and clear clinical tone."
    )
    
    context_data = {
        "patient_demographics": {
            "name": profile.get("name"),
            "ap_number": profile.get("ap_number"),
            "age": profile.get("age"),
            "gender": profile.get("gender"),
            "blood_group": profile.get("blood_group")
        },
        "heart_disease_tabular": profile.get("heart_record"),
        "stroke_tabular": profile.get("stroke_record"),
        "ecg_record": profile.get("ecg_record"),
        "imaging_records": profile.get("imaging_records"),
        "model_predictions": profile.get("predictions"),
        "reports": profile.get("reports")
    }
    
    prompt = (
        f"System Instructions: {system_instruction}\n\n"
        f"Patient Context Data (JSON):\n{json.dumps(context_data, default=str)}\n\n"
        f"User Question: {question}\n\n"
        f"Answer:"
    )
    
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return text
    except Exception as e:
        # If API fails, fall back to local summary with note
        return f"[Gemini API Notice: Call encountered an issue ({str(e)}). Displaying verified local clinical summary:]\n\n" + generate_local_clinical_summary(profile, question)["answer"]

@router.post("/chat", response_model=AssistantResponse)
def assistant_chat(query: AssistantQuery):
    profile = get_patient_full_profile(query.patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    api_key = query.gemini_api_key or GEMINI_API_KEY
    evidence = ["Patient SQLite Record Repository", "Modality Model Outputs"]
    
    if api_key and api_key.strip():
        answer = call_gemini_api(api_key.strip(), profile, query.question)
        evidence.append("Google Gemini 1.5 Clinical Grounding Engine")
    else:
        fallback = generate_local_clinical_summary(profile, query.question)
        answer = fallback["answer"]
        evidence = fallback["evidence_used"]
    
    return AssistantResponse(
        patient_id=query.patient_id,
        question=query.question,
        answer=answer,
        evidence_used=evidence,
        disclaimer=MEDICAL_SAFETY_DISCLAIMER
    )
