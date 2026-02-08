from ui.pdf_generator import generate_pdf
import os
from PIL import Image
import numpy as np

# Create dummy images
img1 = Image.new('RGB', (100, 100), color = 'red')
img2 = Image.new('RGB', (100, 100), color = 'green')

results_list = [
    {
        "pipe_id": "PIPE_001",
        "final_defect": "CRACK",
        "explanation": "Linear crack detected due to gradient > 25.",
        "affected_percentage": 5.4,
        "total_pixels": 10000,
        "suspicious_pixels": 540,
        "image_obj": img1
    },
    {
        "pipe_id": "PIPE_002",
        "final_defect": "NORMAL",
        "explanation": "No significant defects found.",
        "affected_percentage": 0.0,
        "total_pixels": 10000,
        "suspicious_pixels": 0,
        "image_obj": img2
    }
]

try:
    path = generate_pdf(results_list)
    print(f"PDF Generated at: {os.path.abspath(path)}")
    print(f"File Size: {os.path.getsize(path)} bytes")
except Exception as e:
    print(f"Error: {e}")
