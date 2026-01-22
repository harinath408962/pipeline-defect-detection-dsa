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

from core.image_logic import process_image_logic
from severity_priority import clear_priority_queue

# ---------- STREAMLIT CONFIG ----------
st.set_page_config(
    page_title="Pipeline Defect Detection",
    layout="wide"
)

st.title("Pipeline Defect Detection System (DSA Based)")

# ---------- FILE UPLOAD ----------
uploaded_files = st.file_uploader(
    "Upload Pipe Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

pipe_count = 1

# ---------- PROCESS EACH IMAGE ----------
if uploaded_files:
    clear_priority_queue()
    for file in uploaded_files:
        st.divider()

        pipe_id = f"PIPE_{pipe_count:03d}"
        st.header(pipe_id)

        try:
            # ---- LOAD IMAGE ----
            img = Image.open(file).convert("RGB")
            st.image(img, caption=file.name, width=350)

            # ---- CONVERT IMAGE TO NUMPY (H, W, 3) ----
            pixels = np.array(img)
            height, width, _ = pixels.shape

            # ---- RUN CORE LOGIC ----
            result = process_image_logic(
                pixels, width, height, pipe_id
            )

            # ============================
            # UNPACK RESULT
            # ============================
            final_defect = result["final_defect"]
            explanation = result.get("explanation", "Analysis complete.")
            
            # 1. INVALID PIPE WARNING
            if final_defect == "INVALID":
                st.error(f"⚠️ {explanation}")
                st.warning("This image does not appear to be a valid pipe surface.")
                # We stop showing details for invalid pipes to avoid confusion?
                # Or show what we found? Let's show stats but flag red.
            else:
                st.success(f"✅ Pipe Structure Validated: {result.get('explanation', '').split('.')[0]}")


            # ============================
            # BINARY DEFECT MAP (CENTER)
            # ============================
            st.subheader("Binary Defect Map (Center Sample)")
            st.caption("0 = Normal, 1 = Defect Candidate")

            binary_sample = result["binary_sample"]

            ascii_view = "\n".join(
                " ".join(str(cell) for cell in row)
                for row in binary_sample
            )

            st.code(ascii_view, language="text")

            # ============================
            # MATRIX SUMMARY (FROM LOGIC)
            # ============================
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pixels", result["total_pixels"])
            col2.metric("Suspicious Pixels", result["suspicious_pixels"])
            col3.metric("Affected %", f"{result['affected_percentage']}%")

            st.info(f"📋 Analysis Detail: {explanation}")
            
            # ============================
            # FINAL RESULT
            # ============================
            if final_defect == "CRACK":
                st.error(f"🔴 FINAL CLASSIFICATION: {final_defect}")
            elif final_defect == "CORROSION":
                st.warning(f"🟠 FINAL CLASSIFICATION: {final_defect}")
            elif final_defect == "DAMP":
                st.warning(f"🟡 FINAL CLASSIFICATION: {final_defect}")
            elif final_defect == "INVALID":
                st.error(f"❌ CLASSIFICATION: {final_defect}")
            else:
                st.success(f"🟢 FINAL CLASSIFICATION: {final_defect}")
                
            st.markdown("---") 

        except Exception as e:
            st.error("Error while processing this image")
            st.exception(e)

        pipe_count += 1
        
    # ============================
    # GLOBAL PRIORITY QUEUE RANKING
    # ============================
    st.header("Global Severity Ranking (Priority Queue)")
    from severity_priority import get_priority_list
    
    pq = get_priority_list()
    
    if pq:
        ranking_data = [
            {"Rank": i+1, "Pipe ID": pid, "Defect": dtype, "Priority Score": score} 
            for i, (pid, dtype, score) in enumerate(pq)
        ]
        st.table(ranking_data)
    else:
        st.write("No pipes processed yet.")
