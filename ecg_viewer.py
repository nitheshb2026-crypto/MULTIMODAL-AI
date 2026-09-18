import os
import streamlit as st
import numpy as np
import scipy.io
import plotly.graph_objects as go

def render_ecg_section(patient: dict, base_dir: str):
    ecg_rec = patient.get("ecg_record")
    if not ecg_rec:
        st.info("No ECG record currently attached to this patient.")
        return

    rel_path = ecg_rec.get("file_path", "")
    full_path = os.path.join(base_dir, rel_path) if rel_path else ""
    
    st.markdown("### 🫀 1D Continuous Electrocardiogram (ECG) Analysis")
    
    # Metadata bar
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("ECG Lead", ecg_rec.get("lead", "MLII (Modified Lead II)"))
    with c2:
        st.metric("Sampling Rate", f"{ecg_rec.get('sampling_rate', 360)} Hz")
    with c3:
        st.metric("Rhythm Class", ecg_rec.get("rhythm_class", "Unspecified"))
    with c4:
        st.metric("Duration", "10.0 Seconds (3,600 pts)")
        
    st.caption(f"📁 **Source Raw File:** `{rel_path}`")
    
    # Load raw .mat data
    if full_path and os.path.exists(full_path):
        try:
            mat = scipy.io.loadmat(full_path)
            val = mat.get("val")
            if val is not None:
                signal = val.flatten()
                sr = ecg_rec.get("sampling_rate", 360)
                time_axis = np.arange(len(signal)) / sr
                
                # Plotly hospital monitor styled waveform
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=time_axis,
                    y=signal,
                    mode='lines',
                    name='Lead MLII',
                    line=dict(color='#00ff88', width=1.5)
                ))
                
                fig.update_layout(
                    title=f"10-Second Digital Rhythm Strip — Lead MLII [{ecg_rec.get('rhythm_class')}]",
                    xaxis_title="Time (seconds) — Interactive Zoom/Pan",
                    yaxis_title="Amplitude (ADC Digital Units)",
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#020617",
                    font=dict(color="#94a3b8", family="Inter"),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="#1e293b",
                        zeroline=False,
                        tickmode='linear',
                        tick0=0,
                        dtick=1.0
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="#1e293b",
                        zeroline=False
                    ),
                    height=360,
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Zoom segment helper
                with st.expander("🔍 Magnified Beat Morphology Inspection (2.0s Zoom Window)"):
                    zoom_samples = min(720, len(signal))
                    fig_zoom = go.Figure()
                    fig_zoom.add_trace(go.Scatter(
                        x=time_axis[:zoom_samples],
                        y=signal[:zoom_samples],
                        mode='lines+markers',
                        marker=dict(size=3, color='#38bdf8'),
                        line=dict(color='#38bdf8', width=2),
                        name='Magnified Complex'
                    ))
                    fig_zoom.update_layout(
                        title="P-QRS-T Morphological Analysis Window",
                        xaxis_title="Time (seconds)",
                        yaxis_title="Amplitude",
                        paper_bgcolor="#0f172a",
                        plot_bgcolor="#020617",
                        font=dict(color="#94a3b8"),
                        height=260,
                        margin=dict(l=40, r=20, t=40, b=30)
                    )
                    st.plotly_chart(fig_zoom, use_container_width=True)
                    st.info(f"**Clinical Rhythm Note:** {ecg_rec.get('notes', 'None recorded.')}")
        except Exception as e:
            st.error(f"Error reading ECG .mat file: {str(e)}")
    else:
        st.warning(f"ECG file not found at path: `{full_path}`")
