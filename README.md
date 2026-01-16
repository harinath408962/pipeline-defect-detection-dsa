# Pipeline Defect Detection System (DSA Based)

## Project Overview
This project detects defects in pipeline images using 
pure Data Structures and Algorithms (DSA).

The system analyzes pixel-level data to identify:
- Crack
- Corrosion
- Damp

No Machine Learning is used.

---

## Technologies Used
- Python
- Pillow (for image processing)
- Data Structures (DFS, Stack, Priority Queue)

---

## How to Run the Project

1. Install Python 3
2. Install required library:
   pip install pillow
3. Run the system:
   python main.py

---

## Defect Detection Logic

- Crack → detected using global linear continuity
- Corrosion → detected using rust color dominance
- Damp → detected using dark intensity pixels

---

## Output
For each image, the system prints:
- Pipe ID
- Final detected defect
- Maintenance priority order
