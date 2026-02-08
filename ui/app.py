import sys
import os

# ---------- PATH FIX (VERY IMPORTANT) ----------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ---------- IMPORTS ----------
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd

from core.image_logic import process_image_logic
from ui.pdf_generator import generate_pdf

# ---------- STREAMLIT CONFIG ----------
st.set_page_config(
    page_title="Pipeline Defect Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS (LIGHT THEME FORCE) ----------
st.markdown("""
<style>
    /* Force Light Background */
    .stApp {
        background-color: #F8F9FA;
        color: #000000;
    }
    /* Headers */
    h1, h2, h3 {
        color: #2C3E50 !important;
    }
    /* Cards/Containers */
    .stImage {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 5px;
        background: white;
    }
    .css-1r6slb0 {
        background-color: white;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if 'processed_data' not in st.session_state:
    st.session_state['processed_data'] = []

if 'uploaded_file_names' not in st.session_state:
    st.session_state['uploaded_file_names'] = set()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🔧 Settings")
    
    st.subheader("Data Management")
    # 1. Reset Button
    if st.button("🔄 Reset / Clear All", type="primary"):
        st.session_state['processed_data'] = []
        st.session_state['uploaded_file_names'] = set()
        st.rerun()

    st.markdown("---")
    
    st.subheader("Reporting")
    # 2. PDF Download
    if st.session_state['processed_data']:
        try:
            pdf_path = generate_pdf(st.session_state['processed_data'])
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=f,
                    file_name="Pipeline_Analysis_Report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"PDF Error: {e}")
    else:
        st.info("Upload images to generate report.")

# ---------- MAIN UI ----------
st.title("Pipeline Defect Detection System")
st.write("Upload pipe images below for automated DSA-based defect analysis.")

# FILE UPLOAD (Top of Page)
uploaded_files = st.file_uploader(
    "📂 Upload Images (JPG, PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    new_files = [f for f in uploaded_files if f.name not in st.session_state['uploaded_file_names']]
    
    if new_files:
        with st.spinner(f"Processing {len(new_files)} new images..."):
            pipe_count = len(st.session_state['processed_data']) + 1
            
            for file in new_files:
                try:
                    img = Image.open(file).convert("RGB")
                    pixels = np.array(img)
                    height, width, _ = pixels.shape
                    pipe_id = f"PIPE_{pipe_count:03d}"
                    
                    # Process
                    result = process_image_logic(pixels, width, height, pipe_id)
                    
                    # Add metadata
                    result['file_name'] = file.name
                    result['image_obj'] = img
                    result['pipe_id'] = pipe_id
                    
                    st.session_state['processed_data'].append(result)
                    st.session_state['uploaded_file_names'].add(file.name)
                    pipe_count += 1
                    
                except Exception as e:
                    st.error(f"Error processing {file.name}: {e}")
        
        # Rerun to update view immediately
        st.rerun()

st.markdown("---")

# DISPLAY RESULTS (Linear Layout)
if st.session_state['processed_data']:
    st.header("🔍 Analysis Results")
    
    # SORTING LOGIC: Local Sort
    def calculate_priority(res):
        status = res.get('final_defect', 'NORMAL')
        affected = res.get('affected_percentage', 0)
        
        # Severity Map
        severity = 0
        if status == "CRACK": severity = 10
        elif status == "CORROSION": severity = 5
        elif status == "DAMP": severity = 2
        elif status == "NORMAL" or status == "HEALTHY": severity = 1
        elif status == "INVALID": severity = 0
        
        # Score = Severity * 1000 + Affected %
        return (severity * 1000) + affected

    # Sort by calculated priority desc
    sorted_results = sorted(
        st.session_state['processed_data'],
        key=calculate_priority,
        reverse=True
    )
            
    # DISPLAY LOOP (Input Order)
    # User requested: "image uploading part should be considered as the way the user inputs"
    # So we display images in the order they were processed/uploaded.
    for result in st.session_state['processed_data']:
        with st.container():
            c1, c2 = st.columns([1, 2])
            
            # Image Column
            with c1:
                st.image(result['image_obj'], caption=f"{result['pipe_id']} - {result['file_name']}", use_container_width=True)
            
            # Details Column
            with c2:
                st.subheader(f"{result['pipe_id']} ({result['final_defect']})")
                
                # Status Badge
                final_defect = result["final_defect"]
                if final_defect == "CRACK":
                    st.error("🔴 Critical: Crack Detected")
                elif final_defect == "CORROSION":
                    st.warning("🟠 Warning: Corrosion Detected")
                elif final_defect == "DAMP":
                    st.warning("🟡 Warning: Dampness/Algae")
                elif final_defect == "INVALID":
                     st.error("⚠️ Invalid Image")
                else:
                    st.success("🟢 Normal / Healthy")
                
                st.write(f"**Explanation:** {result.get('explanation', 'No details.')}")
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Suspicious Pixels", result["suspicious_pixels"])
                m2.metric("Affected Area", f"{result['affected_percentage']}%")
                m3.metric("Status", final_defect)
                
                # Binary Map DIRECT (No Expander)
                if final_defect != "INVALID":
                     st.caption("Binary Defect Map")
                     binary_sample = result["binary_sample"]
                     ascii_view = "\n".join(" ".join(str(c) for c in r) for r in binary_sample)
                     st.code(ascii_view, language="text")
        
        st.markdown("---")

    # TABULAR CONTENT (Bottom)
    st.header("📊 Tabular Summary")
    
    # Create DataFrame
    table_data = []
    # FIX: Use sorted_results instead of original processed_data
    for res in sorted_results:
        table_data.append({
            "Pipe ID": res['pipe_id'],
            "File Name": res['file_name'],
            "Status": res['final_defect'],
            "Affected %": res['affected_percentage'],
            "Suspicious Pixels": res['suspicious_pixels'],
            "Explanation": res['explanation']
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df)


else:
    st.info("Awaiting uploads...")
