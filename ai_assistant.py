import streamlit as st
import json
import requests
from backend.routes.assistant import generate_local_clinical_summary, call_gemini_api
from backend.config import MEDICAL_SAFETY_DISCLAIMER, GEMINI_API_KEY

def render_ai_assistant_section(patient: dict):
    st.markdown("### 🤖 Gemini Multimodal AI Clinical Assistant")
    
    # Prominent medical disclaimer banner
    st.markdown(f"""
    <div class="disclaimer-box">
        {MEDICAL_SAFETY_DISCLAIMER}
    </div>
    """, unsafe_allow_html=True)
    
    # Optional API key configuration
    with st.expander("🔑 Gemini API Configuration (Optional)"):
        user_key = st.text_input("Enter Google Gemini API Key", value=st.session_state.get("gemini_key", ""), type="password", key="key_input")
        if user_key:
            st.session_state["gemini_key"] = user_key
        st.caption("If an API key is provided, queries will be processed by Google Gemini 1.5 with clinical grounding instructions. Otherwise, the verified local clinical summarizer engine is used.")

    # Preset quick query buttons specified in requirements
    st.markdown("**Suggested Clinical Inquiries:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    q_col4, q_col5, q_col6 = st.columns(3)
    
    prompt_to_submit = None
    if q_col1.button("📋 Summarize this patient's available results.", use_container_width=True):
        prompt_to_submit = "Summarize this patient's available results."
    if q_col2.button("🫀 What did the ECG model detect?", use_container_width=True):
        prompt_to_submit = "What did the ECG model detect?"
    if q_col3.button("📊 What are the model outputs for this patient?", use_container_width=True):
        prompt_to_submit = "What are the model outputs for this patient?"
    if q_col4.button("🩻 Explain the X-ray model result.", use_container_width=True):
        prompt_to_submit = "Explain the X-ray model result."
    if q_col5.button("📑 Show the patient's previous reports.", use_container_width=True):
        prompt_to_submit = "Show the patient's previous reports."
    if q_col6.button("🩸 Assess stroke vs cardiovascular risk.", use_container_width=True):
        prompt_to_submit = "Assess stroke vs cardiovascular risk."

    # Initialize chat history in session state
    chat_key = f"chat_history_{patient['id']}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {
                "role": "assistant",
                "content": f"Hello! I am your Multimodal AI Health Assistant for patient **{patient['name']}** (`{patient['ap_number']}`). Ask me to summarize test results, explain model outputs, or review cardiovascular, ECG, and radiograph findings."
            }
        ]

    # Display chat history
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_query = st.chat_input("Ask a clinical question about this patient...")
    final_query = prompt_to_submit or user_query

    if final_query:
        st.session_state[chat_key].append({"role": "user", "content": final_query})
        with st.chat_message("user"):
            st.markdown(final_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing patient records and generating clinical summary..."):
                api_key = st.session_state.get("gemini_key", "") or GEMINI_API_KEY
                
                if api_key and api_key.strip():
                    response_text = call_gemini_api(api_key.strip(), patient, final_query)
                else:
                    res = generate_local_clinical_summary(patient, final_query)
                    response_text = res["answer"]
                
                st.markdown(response_text)
                st.session_state[chat_key].append({"role": "assistant", "content": response_text})
                
                # Show citations/evidence used
                with st.expander("📚 Evidence & Models Used for this Response"):
                    st.write("- **Active Modalities Evaluated:** Tabular Heart Disease, Tabular Stroke, 1D Lead MLII ECG, Chest Radiograph")
                    st.write(f"- **Patient AP Identifier:** `{patient['ap_number']}`")
                    st.write("- **Grounding Policy:** Non-diagnostic, evidence-bound explanation.")
