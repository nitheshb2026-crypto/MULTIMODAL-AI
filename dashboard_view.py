import os
import json
import streamlit as st
from database.db import get_patient_full_profile
from backend.routes.inference import run_multimodal_analysis
from frontend.components.ecg_viewer import render_ecg_section
from frontend.components.imaging_viewer import render_imaging_section
from frontend.components.ai_assistant import render_ai_assistant_section

def get_risk_badge(prediction_label: str) -> str:
    label_lower = prediction_label.lower()
    if "high" in label_lower or "critical" in label_lower:
        return f'<span class="badge-critical">⚠️ {prediction_label}</span>'
    elif "moderate" in label_lower or "vascular" in label_lower or "respiratory" in label_lower:
        return f'<span class="badge-moderate">⚡ {prediction_label}</span>'
    else:
        return f'<span class="badge-low">✅ {prediction_label}</span>'

def render_patient_dashboard(patient_id: int, base_dir: str):
    patient = get_patient_full_profile(patient_id)
    if not patient:
        st.error("Patient profile not found.")
        if st.button("← Return to Patient Search"):
            st.session_state["selected_patient_id"] = None
            st.rerun()
        return

    # Top Navigation / Return bar
    nav_c1, nav_c2 = st.columns([1, 4])
    with nav_c1:
        if st.button("← Switch Patient", use_container_width=True):
            st.session_state["selected_patient_id"] = None
            st.rerun()
    with nav_c2:
        st.caption(f"Active Patient: **{patient['name']}** | Database Record ID: #{patient['id']}")

    # Patient Demographics Banner
    st.markdown(f"""
    <div class="patient-banner">
        <div>
            <div class="patient-name-tag">{patient['name']}</div>
            <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 4px;">
                <strong>Age:</strong> {patient['age']} yrs &nbsp;|&nbsp; 
                <strong>Gender:</strong> {patient['gender']} &nbsp;|&nbsp; 
                <strong>Blood Group:</strong> {patient.get('blood_group', 'O+')} &nbsp;|&nbsp; 
                <strong>Contact:</strong> {patient.get('phone', 'N/A')}
            </div>
            <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 6px; font-style: italic;">
                "{patient.get('notes', 'No clinical history remarks recorded.')}"
            </div>
        </div>
        <div style="text-align: right;">
            <div class="patient-ap-badge">{patient['ap_number']}</div>
            <div style="color: #64748b; font-size: 0.75rem; margin-top: 6px;">Admitted: {str(patient.get('created_at', ''))[:10]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Toolbar required by specifications:
    # Analyze Patient, View ECG, View X-ray, View Tabular Data, Generate Report, Ask AI Assistant
    st.markdown("##### ⚡ Quick Clinical Actions:")
    btn_c1, btn_c2, btn_c3, btn_c4, btn_c5, btn_c6 = st.columns(6)
    
    with btn_c1:
        if st.button("🔄 Analyze Patient", use_container_width=True, type="primary"):
            with st.spinner("Executing multimodal analysis pipeline across tabular, ECG, and imaging models..."):
                res = run_multimodal_analysis(patient_id)
                st.success("Multimodal analysis successfully updated!")
                st.rerun()
                
    active_tab_idx = st.session_state.get("active_tab", 0)
    with btn_c2:
        if st.button("🫀 View ECG", use_container_width=True):
            st.session_state["active_tab"] = 2
            st.rerun()
    with btn_c3:
        if st.button("🩻 View X-ray", use_container_width=True):
            st.session_state["active_tab"] = 3
            st.rerun()
    with btn_c4:
        if st.button("📊 View Tabular Data", use_container_width=True):
            st.session_state["active_tab"] = 1
            st.rerun()
    with btn_c5:
        if st.button("📑 Generate Report", use_container_width=True):
            st.session_state["active_tab"] = 4
            st.rerun()
    with btn_c6:
        if st.button("🤖 Ask AI Assistant", use_container_width=True):
            st.session_state["active_tab"] = 5
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # COMBINED MULTIMODAL SUMMARY CARD
    preds = patient.get("predictions", [])
    pred_map = {p["modality"]: p for p in preds}
    fusion_pred = pred_map.get("MULTIMODAL_FUSION", {})

    with st.container():
        st.markdown("### 🌐 Multimodal Fusion Diagnostic Summary")
        f_col1, f_col2, f_col3 = st.columns([1.5, 2, 1.5])
        
        with f_col1:
            fusion_label = fusion_pred.get("prediction_label", "Pending Multimodal Analysis")
            badge_html = get_risk_badge(fusion_label)
            st.markdown(f"**Overall Clinical Synthesis:**<br>{badge_html}", unsafe_allow_html=True)
            st.metric("Fusion Confidence Score", f"{fusion_pred.get('confidence', 0.0) * 100:.1f}%")
            st.caption(f"Model: `{fusion_pred.get('model_name', 'Cross-Attention Fusion Engine')}`")
            
        with f_col2:
            st.markdown("**Cross-Modality Evidence Synthesized:**")
            st.info(fusion_pred.get("evidence_summary", "Run 'Analyze Patient' to synthesize findings."))
            
        with f_col3:
            st.markdown("**Uploaded Medical Assets:**")
            st.write(f"- 📊 **Tabular**: Heart & Stroke sets")
            ecg_status = "Available" if patient.get("ecg_record") else "None"
            st.write(f"- 🫀 **1D ECG**: {ecg_status}")
            xrays = [i for i in patient.get("imaging_records", []) if i.get("modality") == "CHEST_XRAY"]
            cts = [i for i in patient.get("imaging_records", []) if i.get("modality") == "CT_SCAN"]
            st.write(f"- 🩻 **Chest X-Rays**: {len(xrays)} file(s)")
            st.write(f"- 🧬 **CT Slices**: {len(cts)} file(s)")
            st.caption(f"Last analyzed: {fusion_pred.get('timestamp', 'N/A')}")

    st.divider()

    # Detailed Modality Workspace Tabs
    tab_titles = [
        "🌐 Unified Overview",
        "📊 Tabular ML (Heart & Stroke)",
        "🫀 1D ECG Biosignal",
        "🩻 Radiological Imaging",
        "📑 Patient Clinical Report",
        "🤖 Gemini AI Assistant"
    ]
    
    current_tab = st.session_state.get("active_tab", 0)
    tabs = st.tabs(tab_titles)

    # -------------------------------------------------------------
    # TAB 0: Unified Overview
    # -------------------------------------------------------------
    with tabs[0]:
        st.markdown("#### Modality Predictions & Model Evidence Breakdown")
        
        # Grid of cards for each model
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            # Heart Disease Model Card
            h_pred = pred_map.get("HEART_DISEASE", {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Heart Disease Tabular Model</div>
                <div style="margin: 6px 0;">{get_risk_badge(h_pred.get('prediction_label', 'Pending'))}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px;">
                    <strong>Confidence:</strong> {h_pred.get('confidence', 0.0)*100:.1f}%<br>
                    <strong>Model:</strong> <code>{h_pred.get('model_name', 'CardioNet Random Forest')}</code><br>
                    <strong>Evidence:</strong> {h_pred.get('evidence_summary', 'Awaiting data')}
                </div>
                <div class="metric-sub">Timestamp: {h_pred.get('timestamp', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Stroke Model Card
            s_pred = pred_map.get("STROKE", {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Stroke Risk Tabular Model</div>
                <div style="margin: 6px 0;">{get_risk_badge(s_pred.get('prediction_label', 'Pending'))}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px;">
                    <strong>Confidence:</strong> {s_pred.get('confidence', 0.0)*100:.1f}%<br>
                    <strong>Model:</strong> <code>{s_pred.get('model_name', 'NeuroRisk XGBoost')}</code><br>
                    <strong>Evidence:</strong> {s_pred.get('evidence_summary', 'Awaiting data')}
                </div>
                <div class="metric-sub">Timestamp: {s_pred.get('timestamp', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

        with c_m2:
            # ECG Model Card
            e_pred = pred_map.get("ECG", {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">1D ECG Rhythm Model (Lead MLII)</div>
                <div style="margin: 6px 0;">{get_risk_badge(e_pred.get('prediction_label', 'Pending'))}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px;">
                    <strong>Confidence:</strong> {e_pred.get('confidence', 0.0)*100:.1f}%<br>
                    <strong>Model:</strong> <code>{e_pred.get('model_name', '1D-CNN RhythmNet')}</code><br>
                    <strong>Evidence:</strong> {e_pred.get('evidence_summary', 'Awaiting signal')}
                </div>
                <div class="metric-sub">Timestamp: {e_pred.get('timestamp', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chest X-Ray Model Card
            x_pred = pred_map.get("CHEST_XRAY", {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Chest Radiograph Model</div>
                <div style="margin: 6px 0;">{get_risk_badge(x_pred.get('prediction_label', 'Pending'))}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px;">
                    <strong>Confidence:</strong> {x_pred.get('confidence', 0.0)*100:.1f}%<br>
                    <strong>Model:</strong> <code>{x_pred.get('model_name', 'DenseNet-121 Radiograph Analyzer')}</code><br>
                    <strong>Evidence:</strong> {x_pred.get('evidence_summary', 'Awaiting radiograph')}
                </div>
                <div class="metric-sub">Timestamp: {x_pred.get('timestamp', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 1: Tabular Clinical Data (Heart & Stroke)
    # -------------------------------------------------------------
    with tabs[1]:
        st.markdown("### 📊 Tabular Clinical Diagnostic Measurements")
        
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("#### Cardiovascular Metrics (`heart.csv` schema)")
            heart = patient.get("heart_record")
            if heart:
                m1, m2, m3 = st.columns(3)
                m1.metric("Resting BP", f"{heart.get('trestbps')} mm Hg", delta="Normal: <120", delta_color="inverse" if heart.get('trestbps', 0) > 130 else "normal")
                m2.metric("Cholesterol", f"{heart.get('chol')} mg/dL", delta="Normal: <200", delta_color="inverse" if heart.get('chol', 0) > 230 else "normal")
                m3.metric("Max Heart Rate", f"{heart.get('thalach')} bpm")
                
                m4, m5, m6 = st.columns(3)
                m4.metric("Chest Pain Type", f"Type {heart.get('cp')}")
                m5.metric("ST Depression", f"{heart.get('oldpeak')} mm")
                m6.metric("Fluoroscopy Vessels", f"{heart.get('ca')} colored")
                
                with st.expander("View Full Heart Diagnostic Vector"):
                    st.json(heart)
            else:
                st.info("No cardiovascular tabular record on file.")

        with t_col2:
            st.markdown("#### Cerebrovascular Stroke Metrics (`stroke_prediction.csv`)")
            stroke = patient.get("stroke_record")
            if stroke:
                s1, s2, s3 = st.columns(3)
                s1.metric("Blood Glucose", f"{stroke.get('avg_glucose_level')} mg/dL", delta="Normal: 70-100", delta_color="inverse" if stroke.get('avg_glucose_level', 0) > 125 else "normal")
                s2.metric("Body Mass Index", f"{stroke.get('bmi')}", delta="Normal: 18.5-24.9", delta_color="inverse" if stroke.get('bmi', 0) > 28 else "normal")
                s3.metric("Hypertension", "Yes" if stroke.get('hypertension') else "No")
                
                s4, s5, s6 = st.columns(3)
                s4.metric("Smoking Status", stroke.get('smoking_status', 'N/A').title())
                s5.metric("Work Environment", stroke.get('work_type', 'N/A'))
                s6.metric("Residence", stroke.get('residence_type', 'N/A'))
                
                with st.expander("View Full Stroke Risk Vector"):
                    st.json(stroke)
            else:
                st.info("No stroke tabular record on file.")

    # -------------------------------------------------------------
    # TAB 2: 1D ECG Biosignal
    # -------------------------------------------------------------
    with tabs[2]:
        render_ecg_section(patient, base_dir)

    # -------------------------------------------------------------
    # TAB 3: Radiological Imaging
    # -------------------------------------------------------------
    with tabs[3]:
        render_imaging_section(patient, base_dir)

    # -------------------------------------------------------------
    # TAB 4: Patient Clinical Report
    # -------------------------------------------------------------
    with tabs[4]:
        st.markdown("### 📑 Official Multimodal Clinical Diagnostic Report")
        reports = patient.get("reports", [])
        if not reports:
            st.info("No generated report available. Click '🔄 Analyze Patient' to generate a synthesized report.")
        else:
            rep = reports[0]
            st.markdown(f"#### {rep['report_title']}")
            st.caption(f"Generated at: `{rep.get('generated_at')}` | Patient Identifier: `{patient['ap_number']}`")
            
            st.markdown(f"""
            <div style="background: #0f172a; padding: 1.5rem; border-radius: 8px; border: 1px solid #334155; margin: 1rem 0;">
                <h5 style="color: #38bdf8; margin-bottom: 0.5rem;">Diagnostic Multimodal Synthesis</h5>
                <p style="color: #e2e8f0; line-height: 1.6;">{rep['summary_text']}</p>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;">
                    <strong style="color: #f59e0b;">Actionable Clinical Recommendations:</strong>
                    <p style="color: #cbd5e1; white-space: pre-line; margin-top: 0.5rem;">{rep.get('recommendations', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Print / Download report text
            st.download_button(
                label="📥 Download Clinical Summary (TXT)",
                data=f"{rep['report_title']}\nPatient: {patient['name']} ({patient['ap_number']})\nAge/Sex: {patient['age']} {patient['gender']}\n\nSummary:\n{rep['summary_text']}\n\nRecommendations:\n{rep.get('recommendations', '')}",
                file_name=f"Clinical_Report_{patient['ap_number']}.txt",
                mime="text/plain"
            )

    # -------------------------------------------------------------
    # TAB 5: Gemini AI Assistant
    # -------------------------------------------------------------
    with tabs[5]:
        render_ai_assistant_section(patient)
