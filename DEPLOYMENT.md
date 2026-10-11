# 🌐 Deploying Digital Risk Shield & Creating a Live Backend Link

This guide explains how to deploy the **Digital Risk Shield** backend online and obtain a public live link (`https://...`) that can be accessed from any browser or connected to any frontend.

---

## 🚀 Option 1: Free Cloud Deployment via Render (Recommended)

Render offers free web service hosting directly from your GitHub repository.

### Step 1: Push your latest code to GitHub
Make sure all configuration files (`requirements.txt`, `render.yaml`, `Procfile`) are pushed to your GitHub repository:
```bash
git add .
git commit -m "Add deployment configs and live backend link support"
git push origin main
```
*(Or simply double-click `upload_to_github.bat`)*

### Step 2: Create a Web Service on Render
1. Open [https://render.com](https://render.com) and sign in (using GitHub).
2. Click **New +** in the top navigation bar and select **Web Service**.
3. Select your repository: `rohithsai-smp/Risk-Detection` (or connect your GitHub account if first time).
4. Fill in the deployment parameters (or let `render.yaml` configure them automatically):
   - **Name:** `digital-risk-shield` (or any custom name)
   - **Region:** Choose closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
5. Click **Deploy Web Service**.

### Step 3: Your Live Backend Link Is Ready!
Once the build completes (usually takes ~1-2 minutes), Render will display your public HTTPS link:
```
https://<your-service-name>.onrender.com
```

### 🔗 Available Live Endpoints on Your Link:
- **Interactive SOC Dashboard:** `https://<your-service-name>.onrender.com/`
- **Interactive Swagger API Docs:** `https://<your-service-name>.onrender.com/docs`
- **OpenAPI 3.0 Specification:** `https://<your-service-name>.onrender.com/openapi.json`
- **API Health Check:** `https://<your-service-name>.onrender.com/api/health`
- **Analyze Name Endpoint:** `https://<your-service-name>.onrender.com/api/analyze-name`
- **Threat Intelligence Feed:** `https://<your-service-name>.onrender.com/api/threats`

---

## 🚂 Option 2: Deploy on Railway (Alternative)

Railway provides 1-click deployments with automatic Docker/Procfile detection.

1. Go to [https://railway.app](https://railway.app) and log in with GitHub.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select `rohithsai-smp/Risk-Detection`.
4. Railway will automatically detect the included `Procfile` / `Dockerfile` and `requirements.txt`.
5. Under service settings, click **Generate Domain**.
6. You will instantly get a live link: `https://<app-name>.up.railway.app`.

---

## 💻 Option 3: Local Backend Link

To run the backend locally on your computer:
```bash
python run.py
```
Or directly using Uvicorn:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Local access links:
- **Dashboard UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Schema:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🔌 Linking Frontend to a Remote Backend

If you host the frontend dashboard separately (e.g. on GitHub Pages, Vercel, or open `index.html` locally):
1. Navigate to **Settings** in the dashboard sidebar.
2. In the **Backend API Connection Link** card, enter your live deployed backend URL:
   `https://<your-service-name>.onrender.com`
3. Click **Save Link** and **Test Ping**.
4. The dashboard will instantly route all scans, analyzers, brand queries, and takedown notices to your live cloud backend!
