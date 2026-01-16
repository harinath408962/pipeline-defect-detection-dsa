import streamlit as st
import sys
import os
from PIL import Image
import traceback

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(
    page_title="Pipeline Defect Detection System",
    layout="wide"
)

st.title("🛢️ Pipeline Defect Detection System (DSA Based)")
st.write("Upload pipeline images to detect **Corrosion / Crack**")

# ---- FILE UPLOADER ----
uploaded_files = st.file_uploader(
    "Upload Pipe Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ---- STOP EARLY IF NO FILES ----
if not uploaded_files:
    st.info("⬆️ Upload one or more pipeline images to start analysis.")
    st.stop()

# ---- IMPORT LOGIC SAFELY ----
try:
    from core.image_logic import process_image_logic
except Exception as e:
    st.error("❌ Failed to import processing logic")
    st.code(traceback.format_exc())
    st.stop()

# ---- PROCESS EACH IMAGE ----
for idx, file in enumerate(uploaded_files, start=1):
    st.divider()
    st.subheader(f"PIPE_{idx:03d}")

    try:
        image = Image.open(file).convert("RGB")
        st.image(image, caption=file.name, width=350)

        # Convert image to pixels
        pixels = image.load()
        width, height = image.size

        # Run main logic
        result = process_image_logic(
            pixels=pixels,
            width=width,
            height=height,
            pipe_id=f"PIPE_{idx:03d}"
        )

        # ---- DISPLAY RESULTS ----
        st.markdown("### 🔲 Binary Defect Map (Center Sample)")
        st.code(result["binary_sample"])

        st.markdown("### 📊 Matrix Summary")
        st.write(f"**Total Pixels:** {result['total_pixels']}")
        st.write(f"**Suspicious Pixels:** {result['suspicious_pixels']}")
        st.write(f"**Affected Percentage:** {result['affected_percentage']}%")

        st.success(f"✅ Detected Defect: **{result['final_defect']}**")

    except Exception:
        st.error("❌ Error while processing this image")
        st.code(traceback.format_exc())
