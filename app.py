import os
import sys
import streamlit as st

# Add workspace root to sys.path so backend and database modules can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import init_db
from frontend.components.patient_search import render_patient_search_and_registration
from frontend.components.dashboard_view import render_patient_dashboard

st.set_page_config(
    page_title="Multimodal AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure database tables exist
init_db()

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/medical-heart.png", width=64)
    st.title("Clinical Portal")
    st.caption("College Capstone Project: **Multimodal AI Health Assistant**")
    
    st.divider()
    
    selected_id = st.session_state.get("selected_patient_id")
    if selected_id:
        st.success(f"Active Patient: **#{selected_id}**")
        if st.button("⬅ Switch Patient Record", use_container_width=True):
            st.session_state["selected_patient_id"] = None
            st.rerun()
    else:
        st.info("Select a patient from the search registry to open the clinical dashboard.")
        
    st.divider()
    st.markdown("### Integrated Modalities:")
    st.markdown("""
    - 📊 **Tabular ML**: Heart Disease (`heart.csv`)
    - 🧠 **Tabular ML**: Stroke (`stroke_prediction.csv`)
    - 🫀 **1D Biosignal**: Lead MLII ECG (`.mat`)
    - 🩻 **Radiology**: Chest X-Rays (`.jpeg`)
    - 🧬 **Tomography**: CT Medical Images (`.dcm`)
    - 🤖 **Cognitive AI**: Google Gemini Assistant
    """)
    
    st.divider()
    st.caption("🛡️ *Educational decision support system only. Does not replace physician diagnosis.*")

# Main View router
selected_patient_id = st.session_state.get("selected_patient_id")

if selected_patient_id is None:
    render_patient_search_and_registration()
else:
    render_patient_dashboard(selected_patient_id, BASE_DIR)
