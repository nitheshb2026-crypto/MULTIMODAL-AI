import os
import streamlit as st
from PIL import Image
import numpy as np
import pydicom

def render_imaging_section(patient: dict, base_dir: str):
    imaging_records = patient.get("imaging_records", [])
    if not imaging_records:
        st.info("No radiological images (Chest X-ray / CT) currently linked to this patient.")
        return

    st.markdown("### 🩻 Radiological Imaging: Chest Radiographs & CT Slices")
    
    # Split into Chest X-ray and CT
    xrays = [r for r in imaging_records if r.get("modality") == "CHEST_XRAY"]
    cts = [r for r in imaging_records if r.get("modality") == "CT_SCAN"]
    
    tab_xray, tab_ct = st.tabs([f"Chest X-Rays ({len(xrays)})", f"Computed Tomography / CT ({len(cts)})"])
    
    with tab_xray:
        if not xrays:
            st.info("No Chest X-ray on record for this patient.")
        else:
            for idx, xr in enumerate(xrays, 1):
                col_img, col_info = st.columns([1.2, 1])
                rel_path = xr.get("file_path", "")
                full_path = os.path.join(base_dir, rel_path) if rel_path else ""
                
                with col_img:
                    if full_path and os.path.exists(full_path):
                        try:
                            img = Image.open(full_path)
                            st.image(img, caption=f"Radiograph: {os.path.basename(rel_path)}", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")
                    else:
                        st.warning(f"File not found: {rel_path}")
                        
                with col_info:
                    st.markdown(f"#### Radiograph Findings #{idx}")
                    st.metric("Ground Truth / Status", xr.get("ground_truth", "NORMAL"))
                    st.caption(f"📁 **File:** `{rel_path}`")
                    st.write(f"**Acquisition Date:** {xr.get('recorded_at', 'N/A')}")
                    
                    if xr.get("metadata_json"):
                        import json
                        try:
                            meta = json.loads(xr["metadata_json"])
                            st.json(meta)
                        except:
                            st.write(xr["metadata_json"])
                            
    with tab_ct:
        if not cts:
            st.info("No CT DICOM scans on record for this patient.")
        else:
            for idx, ct_rec in enumerate(cts, 1):
                col_ct_img, col_ct_info = st.columns([1.2, 1])
                rel_path = ct_rec.get("file_path", "")
                full_path = os.path.join(base_dir, rel_path) if rel_path else ""
                
                with col_ct_img:
                    if full_path and os.path.exists(full_path):
                        try:
                            dcm = pydicom.dcmread(full_path)
                            arr = dcm.pixel_array.astype(float)
                            # Normalize to 0-255 for standard display
                            arr_norm = (np.maximum(arr, 0) / arr.max()) * 255.0
                            arr_uint8 = np.uint8(arr_norm)
                            st.image(arr_uint8, caption=f"CT Axial Slice (512x512) - {os.path.basename(rel_path)}", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error reading DICOM file: {str(e)}")
                    else:
                        st.warning(f"CT file not found: {rel_path}")
                        
                with col_ct_info:
                    st.markdown(f"#### Volumetric CT Examination #{idx}")
                    st.metric("Scan Modality", "Computed Tomography (CT)")
                    st.write(f"**Ground Truth Tag:** `{ct_rec.get('ground_truth', 'N/A')}`")
                    st.caption(f"📁 **DICOM File:** `{rel_path}`")
                    
                    if full_path and os.path.exists(full_path):
                        try:
                            dcm = pydicom.dcmread(full_path)
                            st.markdown("**DICOM Metadata Tags:**")
                            st.write(f"- **Patient ID (DICOM):** `{getattr(dcm, 'PatientID', 'N/A')}`")
                            st.write(f"- **Patient Age:** `{getattr(dcm, 'PatientAge', 'N/A')}`")
                            st.write(f"- **Patient Sex:** `{getattr(dcm, 'PatientSex', 'N/A')}`")
                            st.write(f"- **Pixel Spacing:** `{getattr(dcm, 'PixelSpacing', 'N/A')}`")
                            st.write(f"- **Slice Dimensions:** {dcm.Rows} × {dcm.Columns}")
                        except Exception as e:
                            st.caption(f"Metadata parsing error: {e}")
