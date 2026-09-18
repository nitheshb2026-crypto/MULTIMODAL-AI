import streamlit as st
from database.db import search_patients, create_patient, get_patient_by_ap

def render_patient_search_and_registration():
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏥 MULTIMODAL AI HEALTH ASSISTANT</h1>
        <div class="header-subtitle">Clinical Decision Support System integrating Tabular ML, 1D ECG Biosignals, Chest Radiography, and CT Imaging with Gemini AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_search, col_reg = st.tabs(["🔍 Search & Select Patient", "➕ Register New Patient"])
    
    with col_search:
        st.subheader("Patient Registry Lookup")
        
        # Search inputs specified in requirements: Patient Name, Patient/AP Number, Age, Gender
        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.2])
        with c1:
            name_query = st.text_input("Patient Name", placeholder="e.g. John Doe", key="search_name")
        with c2:
            ap_query = st.text_input("Patient / AP Number", placeholder="e.g. AP-1001", key="search_ap")
        with c3:
            age_range = st.slider("Age Range", min_value=0, max_value=100, value=(20, 85), key="search_age")
        with c4:
            gender_select = st.selectbox("Gender", ["All", "Male", "Female", "Other"], key="search_gender")
            
        # Quick-select benchmark demo patient chips
        st.markdown("**Quick-Select Clinical Test Cases:**")
        qc1, qc2, qc3, qc4, qc5 = st.columns(5)
        
        selected_ap = None
        if qc1.button("👤 John Doe\n(AP-1001: AFIB Cardiac)", use_container_width=True):
            selected_ap = "AP-1001"
        if qc2.button("👤 Mary Smith\n(AP-1002: Stroke Risk)", use_container_width=True):
            selected_ap = "AP-1002"
        if qc3.button("👤 David Wilson\n(AP-1003: Pneumonia)", use_container_width=True):
            selected_ap = "AP-1003"
        if qc4.button("👤 Sarah Johnson\n(AP-1004: Normal)", use_container_width=True):
            selected_ap = "AP-1004"
        if qc5.button("👤 Robert Brown\n(AP-1005: Critical)", use_container_width=True):
            selected_ap = "AP-1005"
            
        if selected_ap:
            p = get_patient_by_ap(selected_ap)
            if p:
                st.session_state["selected_patient_id"] = p["id"]
                st.rerun()

        # Execute search query
        patients = search_patients(
            query=name_query if name_query.strip() else None,
            ap_number=ap_query if ap_query.strip() else None,
            min_age=age_range[0],
            max_age=age_range[1],
            gender=gender_select
        )
        
        st.write(f"**Found {len(patients)} Patient Records in SQLite Registry**")
        
        for p in patients:
            with st.container():
                cols = st.columns([1.5, 2, 1, 1, 1.2, 1.5])
                with cols[0]:
                    st.markdown(f"**`{p['ap_number']}`**")
                with cols[1]:
                    st.write(f"**{p['name']}**")
                with cols[2]:
                    st.write(f"{p['age']} yrs")
                with cols[3]:
                    st.write(p['gender'])
                with cols[4]:
                    st.write(f"🩸 {p.get('blood_group', 'O+')}")
                with cols[5]:
                    if st.button("Open Dashboard →", key=f"sel_{p['id']}", use_container_width=True):
                        st.session_state["selected_patient_id"] = p["id"]
                        st.rerun()
                st.divider()

    with col_reg:
        st.subheader("Register New Patient in Clinical Registry")
        st.caption("Add patient demographic record. Real medical files and tabular measurements can then be linked.")
        
        with st.form("new_patient_form", clear_on_submit=True):
            r1, r2 = st.columns(2)
            with r1:
                new_ap = st.text_input("Patient / AP Number *", placeholder="e.g. AP-1006")
                new_name = st.text_input("Full Patient Name *", placeholder="e.g. Alice Walker")
                new_age = st.number_input("Age *", min_value=0, max_value=120, value=45)
            with r2:
                new_gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                new_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                new_phone = st.text_input("Contact Phone", placeholder="+1 (555) 000-0000")
            
            new_notes = st.text_area("Initial Clinical Notes / Symptoms", placeholder="Patient admission notes, baseline vitals, clinical history...")
            
            submitted = st.form_submit_button("Register Patient to Database", use_container_width=True)
            if submitted:
                if not new_ap.strip() or not new_name.strip():
                    st.error("Please provide both Patient Name and AP Number.")
                else:
                    existing = get_patient_by_ap(new_ap)
                    if existing:
                        st.error(f"AP Number '{new_ap}' is already assigned to {existing['name']}.")
                    else:
                        new_id = create_patient(
                            ap_number=new_ap,
                            name=new_name,
                            age=int(new_age),
                            gender=new_gender,
                            blood_group=new_blood,
                            phone=new_phone,
                            notes=new_notes
                        )
                        st.success(f"Patient {new_name} ({new_ap}) successfully registered!")
                        st.session_state["selected_patient_id"] = new_id
                        st.rerun()
