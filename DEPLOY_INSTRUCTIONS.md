# How to Deploy to Render 🚀

## Prerequisite
You must have this code on your **GitHub**.
If you haven't pushed it yet, run these commands in your terminal:
```bash
git add .
git commit -m "Ready for Render"
git push origin main
```

## Step 1: Create New Web Service
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **"New +"** -> **"Web Service"**.
3.  Connect your GitHub account and select this repository (`Face-Authentication-Attendance`).

## Step 2: Configure Settings
Fill in these details exactly:

*   **Name**: `face-auth-app` (or anything you like)
*   **Region**: `Singapore` (or `Frankfurt` - nearest to you)
*   **Branch**: `main`
*   **Runtime**: `Python 3`
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `streamlit run app.py`

## Step 3: Advanced (Crucial for OpenCV)
1.  Scroll down to **"Advanced"**.
2.  Click **"Add Environment Variable"**:
    *   Key: `PYTHON_VERSION`
    *   Value: `3.9.12` (Or `3.10.0` - improves stability)

## Step 4: Deploy
1.  Click **"Create Web Service"**.
2.  wait 3-5 minutes.
3.  You will see a URL (e.g., `https://face-auth-app.onrender.com`).
4.  **Done!** Send that link to your company/recruiter. 

## Troubleshooting
*   If it fails with `libGL.so.1 not found`, it means `packages.txt` wasn't read. Ensure `packages.txt` exists in the root (I created it for you).
