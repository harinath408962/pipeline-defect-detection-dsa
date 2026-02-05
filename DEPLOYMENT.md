# Deployment Guide

This project is built with **Streamlit** and is designed to be easily deployed to the **Streamlit Community Cloud**.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account.
2.  **Project on GitHub**: This project code must be pushed to a public (or private) GitHub repository.

## Option 1: Streamlit Community Cloud (Recommended)

This is the easiest and free way to host your app.

1.  **Sign Up / Log In**:
    *   Go to [share.streamlit.io](https://share.streamlit.io/).
    *   Sign in with your GitHub account.

2.  **Deploy an App**:
    *   Click the **"New app"** button.
    *   Select **"Use existing repo"**.

3.  **Configure Deployment**:
    *   **Repository**: Select your GitHub repository (e.g., `your-username/pipeline-defect-detection-dsa`).
    *   **Branch**: Select `main` (or `master`).
    *   **Main file path**: Enter `ui/app.py`.
        *   *Note: This is critical because the app is located in the `ui` folder.*

4.  **Advance Settings (Optional)**:
    *   Python version `3.9` or `3.10` works well.
    *   No secrets needed for this app.

5.  **Click "Deploy!"**:
    *   Streamlit will automatically detect `requirements.txt` (which contains `streamlit`, `pillow`, `numpy`) and install dependencies.
    *   Wait a few minutes for the build to finish.

## Option 2: Run Locally

If you want to run it on your own machine or a dedicated server (AWS, Heroku, Render).

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Run the App
Execute the following command from the project root directory:
```bash
streamlit run ui/app.py
```

## Troubleshooting

-   **"Module not found" error**:
    -   Ensure `requirements.txt` is in the root directory.
    -   Streamlit Cloud sometimes needs a reboot if dependencies change.
-   **Path issues**:
    -   The app includes logic to add the root directory to `sys.path`. If you move `ui/app.py` to the root, you might need to adjust imports.
