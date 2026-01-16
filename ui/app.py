import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from PIL import Image
from core.image_logic import process_image_logic
from defect_detection import rgb_to_binary_map
from region_analysis import dfs
from classification import classify_local
from severity_priority import add_to_priority
from input_module import load_image




st.set_page_config(page_title="Pipeline Defect Detection", layout="wide")
st.title("Pipeline Defect Detection System (DSA Based)")

uploaded_files = st.file_uploader(
    "Upload Pipe Images",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

pipe_count = 1

if uploaded_files:
    for file in uploaded_files:
        st.divider()
        pipe_id = f"PIPE_{pipe_count:03d}"
        st.header(pipe_id)

        img = Image.open(file).convert("RGB")
        st.image(img, caption=file.name, width=350)

        pixels = img.load()
        width, height = img.size

        try:
            result = process_image_logic(pixels, width, height, pipe_id)

            st.subheader("Binary Defect Map (Center Sample)")
            binary_map = result["binary_sample"]

            center = len(binary_map)//2
            sample = binary_map[center-5:center+5]

            ascii_view = "\n".join(
                " ".join(str(c) for c in row[:20])
                for row in sample
            )

            st.code(ascii_view)

            st.subheader("Matrix Summary")
            st.write("Total Pixels:", result["total_pixels"])
            st.write("Suspicious Pixels:", result["suspicious_pixels"])
            st.write("Affected Percentage:", result["affected_percentage"], "%")

            st.success(f"Detected Defect: {result['final_defect']}")

        except Exception as e:
            st.error("Error while processing this image")
            st.exception(e)

        pipe_count += 1
