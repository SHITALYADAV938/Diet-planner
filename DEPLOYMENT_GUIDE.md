# 🏋️ AI Diet & Fitness Planner - Streamlit Deployment Guide

## 📋 Overview

This project is a machine learning-powered personalized diet and fitness planning application. The original Flask backend has been converted to **Streamlit**, a modern Python framework for building interactive web apps.

### Features
- **Personalized Fitness Plans**: AI-generated workout routines based on user profile
- **Macro Nutrition Tracking**: Calorie, protein, carbs, and fat recommendations
- **Weekly Feedback Adaptation**: ML models adapt recommendations based on weekly progress
- **Health Risk Monitoring**: Alerts for burnout, sleep deprivation, and overtraining
- **Context-Aware Planning**: Adjustments for exam season, travel, or special situations
- **Fitness Persona Classification**: 4 clusters identifying your fitness archetype

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone/Navigate to Project
```bash
cd "c:\CODING\Projects\diet planner"
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Run the Streamlit App
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501` in your default browser.

---

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Diet Planner Streamlit App"
   git remote add origin https://github.com/YOUR_USERNAME/diet-planner.git
   git push -u origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit https://streamlit.io/cloud
   - Click "New app"
   - Select your GitHub repository: `YOUR_USERNAME/diet-planner`
   - Main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Your app is live!** 🎉
   - Share the URL with others (e.g., `https://yourname-diet-planner.streamlit.app`)

---

### Option 2: Heroku Deployment

1. **Create Heroku Account**
   - Sign up at https://heroku.com

2. **Create `Procfile` in project root**
   ```
   web: streamlit run streamlit_app.py --logger.level=error
   ```

3. **Create `setup.sh` in project root**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [general]\n\
   email = \"your-email@example.com\"\n\
   " > ~/.streamlit/credentials.toml
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   " > ~/.streamlit/config.toml
   ```

4. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

---

### Option 3: Docker Containerization

1. **Create `Dockerfile` in project root**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "streamlit_app.py"]
   ```

2. **Build & Run Docker Image**
   ```bash
   docker build -t diet-planner .
   docker run -p 8501:8501 diet-planner
   ```

3. **Push to Docker Hub** (optional)
   ```bash
   docker tag diet-planner YOUR_USERNAME/diet-planner
   docker push YOUR_USERNAME/diet-planner
   ```

---

### Option 4: Azure App Service

1. **Create Azure account** and install Azure CLI

2. **Create Resource Group**
   ```bash
   az group create --name dietplannerRG --location eastus
   ```

3. **Create App Service Plan**
   ```bash
   az appservice plan create --name dietplannerPlan --resource-group dietplannerRG --sku B1 --is-linux
   ```

4. **Deploy from GitHub**
   ```bash
   az webapp create --resource-group dietplannerRG --plan dietplannerPlan --name dietplanner-app --runtime "PYTHON|3.10"
   az webapp deployment source config-zip --resource-group dietplannerRG --name dietplanner-app --src app.zip
   ```

---

### Option 5: AWS (Elastic Beanstalk)

1. **Install EB CLI**
   ```bash
   pip install awsebcli --upgrade --user
   ```

2. **Initialize & Deploy**
   ```bash
   eb init -p python-3.10 diet-planner --region us-east-1
   eb create diet-planner-env
   eb deploy
   ```

---

## 📁 Project Structure

```
diet planner/
├── streamlit_app.py           # Main Streamlit app
├── backend/
│   ├── app.py                 # Original Flask backend (reference)
│   ├── requirements.txt        # Python dependencies
│   ├── train_models.py        # Model training script
│   └── test_post.py           # API testing
├── models/
│   ├── v3_reg.joblib          # Regression model for macros prediction
│   ├── clf_*.joblib           # Classification models
│   ├── kmeans.joblib          # Clustering model for personas
│   ├── encoders.joblib        # Feature encoders
│   └── clustered_data.csv     # Reference data
├── frontend/
│   ├── index.html             # Original frontend (legacy)
│   ├── main.js
│   └── style.css
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

---

## ⚙️ Configuration

### Streamlit Config (`streamlit_app.py` & `.streamlit/config.toml`)

Key settings:
- **Port**: 8501 (default)
- **Theme**: Custom color scheme
- **Logger Level**: Info
- **Session State**: Persists user inputs across reruns

You can modify `.streamlit/config.toml` for custom styling:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F0F2F6"
secondaryBackgroundColor = "#E8EAED"
textColor = "#262730"

[server]
port = 8501
```

---

## 🔐 Environment Variables

Create a `.env` file for sensitive data (if needed):
```env
LOG_LEVEL=INFO
DEBUG=false
```

Load in your app with:
```python
import os
from dotenv import load_dotenv
load_dotenv()
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

---

## 📊 How to Use

1. **Enter Personal Profile**
   - Age, height, weight, gender
   - Activity level, fitness goals, stress level
   - Diet preferences, budget, living condition
   - Medical conditions, cooking equipment

2. **Generate Plan**
   - Click "Generate Your Plan" button
   - Streamlit displays:
     - Your fitness persona & strategy
     - Weekly workout schedule
     - Daily meal plans
     - Shopping list
     - Macro recommendations

3. **Provide Weekly Feedback** (Tab 3)
   - Current weight, workout completion rate
   - Diet adherence, energy level, sleep consistency
   - Click "Adapt My Plan" - AI updates recommendations

---

## 🧠 AI Model Details

### Models Used:
1. **Regression Model** (`v3_reg.joblib`): Predicts macros & hydration
2. **Classification Models**: Burnout risk, fitness level, diet type, intensity
3. **Clustering Model** (`kmeans.joblib`): Identifies 4 fitness personas
4. **Encoders** (`encoders.joblib`): One-hot encoding for categorical features

### Feature Input (16 features):
- Age, Height, Weight, BMI
- Gender, Activity Level, Fitness Goal
- Workout Time, Sleep Duration, Stress Level
- Diet Preference, Living Condition, Budget
- Medical Conditions, Cooking Equipment
- Context (exam/travel/normal)

---

## 🐛 Troubleshooting

### Models Not Loading
**Error**: `FileNotFoundError: models/v3_reg.joblib`

**Solution**:
```bash
# Ensure you're running from project root
cd "c:\CODING\Projects\diet planner"
streamlit run streamlit_app.py
```

### Port Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Slow Model Loading
**Solution**: Models are cached using `@st.cache_resource`
- First load: ~2-3 seconds
- Subsequent runs: Instant (cached)

### Import Errors
**Solution**:
```bash
pip install --upgrade -r backend/requirements.txt
```

---

## 📈 Performance Tips

1. **Use Streamlit Cloud**: Hosted, no management needed
2. **Cache Heavy Operations**: Already done with `@st.cache_resource`
3. **Optimize Model Size**: Consider model quantization for faster inference
4. **Use CDN for Static Files**: If adding images/assets

---

## 🔄 Continuous Integration/Deployment (CI/CD)

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit
        uses: streamlit/streamlit-cloud-deploy@v1
        with:
          secret: ${{ secrets.STREAMLIT_CLOUD_SECRET }}
```

---

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Deployment Guide**: https://docs.streamlit.io/streamlit-cloud/deploy-your-app
- **Custom Components**: https://streamlit.io/components
- **Community**: https://discuss.streamlit.io

---

## 📞 Support & Feedback

- Report issues: GitHub Issues
- Feature requests: Discussions
- Contact: your-email@example.com

---

## 📄 License

MIT License - See LICENSE file for details

---

**Happy Fitness Planning! 💪🚀**
