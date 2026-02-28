# 🚀 Deployment Instructions

## Quick Deploy Options

### 1. **Streamlit Cloud** (Recommended - 2 minutes)
Best for: Quick, free hosting with minimal setup

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Deploy diet planner"
git push origin main

# 2. Go to https://streamlit.io/cloud
# 3. Click "New app" → Select your repo → Deploy
# Done! Your app is live at: https://yourusername-dietplanner.streamlit.app
```

---

### 2. **Local Testing** (Before Deployment)
```bash
cd "c:\CODING\Projects\diet planner"

# Install dependencies
pip install -r backend/requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Open: http://localhost:8501

---

### 3. **Docker** (5 minutes)
```bash
# Build image
docker build -t diet-planner .

# Run container
docker run -p 8501:8501 diet-planner

# Push to Docker Hub
docker tag diet-planner yourname/diet-planner
docker push yourname/diet-planner
```

---

### 4. **Heroku** (10 minutes)
```bash
# 1. Download Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create your-diet-planner

# 4. Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

### 5. **Azure App Service** (15 minutes)
```bash
# Install Azure CLI, then:
az webapp up --name diet-planner --runtime PYTHON:3.10
```

---

## Environment Setup

### Windows (CMD)
```cmd
cd c:\CODING\Projects\diet planner
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
streamlit run streamlit_app.py
```

### Mac/Linux (Terminal)
```bash
cd ~/CODING/Projects/diet_planner
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
streamlit run streamlit_app.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Models not found | Run from project root: `cd "c:\...\diet planner"` |
| Port 8501 in use | `streamlit run streamlit_app.py --server.port 8502` |
| Import errors | `pip install --upgrade -r backend/requirements.txt` |
| Slow loading | Wait for model cache (first load ~2-3s) |

---

## Success Checklist

- [x] Streamlit app created (`streamlit_app.py`)
- [x] Dependencies updated (`requirements.txt`)
- [x] Streamlit config added (`.streamlit/config.toml`)
- [x] Deployment files ready (`Dockerfile`, `Procfile`)
- [x] Deployment guide written (`DEPLOYMENT_GUIDE.md`)

**Your app is ready to deploy!** 🎉

Next step: Choose a deployment option above and follow the instructions.
