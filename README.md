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

### Local Development
1. Install Python 3
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run ui/app.py
   ```

### 🚀 Live Deployment
For instructions on how to deploy this app to **Streamlit Community Cloud** (Free), please read [DEPLOYMENT.md](DEPLOYMENT.md).

> **Note**: This app uses Python logic and cannot be hosted on static services like GitHub Pages. You must use a Python-compatible host.

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
