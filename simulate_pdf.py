from ui.pdf_generator import generate_pdf
import os

results_list = [
    {
        "pipe_id": "PIPE_001",
        "final_defect": "CRACK",
        "explanation": "Linear crack detected due to gradient > 25.",
        "affected_percentage": 5.4,
        "total_pixels": 10000,
        "suspicious_pixels": 540
    },
    {
        "pipe_id": "PIPE_002",
        "final_defect": "NORMAL",
        "explanation": "No significant defects found.",
        "affected_percentage": 0.0,
        "total_pixels": 10000,
        "suspicious_pixels": 0
    },
    {
        "pipe_id": "PIPE_003",
        "final_defect": "INVALID",
        "explanation": "Digital Wallpaper detected.",
        "affected_percentage": 0.0,
        "total_pixels": 10000,
        "suspicious_pixels": 0
    }
]

try:
    path = generate_pdf(results_list)
    print(f"PDF Generated at: {os.path.abspath(path)}")
    print(f"File Size: {os.path.getsize(path)} bytes")
except Exception as e:
    print(f"Error: {e}")
