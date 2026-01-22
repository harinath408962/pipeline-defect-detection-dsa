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
            # BINARY DEFECT MAP (CENTER)
            # ============================
            st.subheader("Binary Defect Map (Center Sample)")

            binary_sample = result["binary_sample"]

            ascii_view = "\n".join(
                " ".join(str(cell) for cell in row[:20])
                for row in binary_sample
            )

            st.code(ascii_view)

            # ============================
            # MATRIX SUMMARY (FROM LOGIC)
            # ============================
            st.subheader("Matrix Summary")
            st.write("Total Pixels:", result["total_pixels"])
            st.write("Suspicious Pixels:", result["suspicious_pixels"])
            st.write(
                "Affected Percentage:",
                result["affected_percentage"],
                "%"
            )

            # ============================
            # FINAL RESULT
            # ============================
            st.success(
                f"Detected Defect: {result['final_defect']}"
            )

        except Exception as e:
            st.error("Error while processing this image")
            st.exception(e)

        pipe_count += 1
