# Installation Guide - Fresh Machine Setup

Complete step-by-step guide to install and run the AI-Powered Intelligent Logistics Optimization System on a fresh machine.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version` or `python3 --version`

2. **Node.js 16 or higher** (includes npm)
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **Git** (optional, for cloning)
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

---

## 🚀 Installation Steps

### Step 1: Get the Project Files

**Option A: If you have the project folder**
```bash
# Navigate to the project directory
cd path/to/logistics-ai-system
```

**Option B: If cloning from repository**
```bash
git clone <repository-url>
cd logistics-ai-system
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- scikit-learn (machine learning)
- XGBoost (ML models)
- pandas, numpy (data processing)
- kagglehub (dataset download)
- Other dependencies

**Expected time:** 2-5 minutes

#### 2.4 Train ML Models
```bash
python train.py
```

This will:
- Download the Supply Chain dataset from Kaggle (~10KB)
- Process and engineer features
- Train 3 ML models (ETA, Cost, Delay)
- Save models to `models/` directory

**Expected output:**
```
[INFO] Downloading Supply Chain dataset from Kaggle...
[INFO] Dataset loaded: 100 rows, 24 columns
[INFO] Training ETA prediction model...
[INFO] ETA Model - MAE: 0.81, RMSE: 0.89, R²: 0.97
[INFO] Training cost estimation model...
[INFO] Cost Model - MAE: 34.93, RMSE: 48.29, R²: 0.91
[INFO] Training delay classification model...
[INFO] Delay Model - Accuracy: 0.80
[INFO] Training completed successfully!
```

**Expected time:** 30-60 seconds

### Step 3: Frontend Setup

#### 3.1 Open New Terminal and Navigate to Frontend
```bash
cd frontend
```

#### 3.2 Install Node Dependencies
```bash
npm install
```

This will install:
- React (UI framework)
- Vite (build tool)
- Axios (HTTP client)
- Recharts (charts)
- Tailwind CSS (styling)
- Other dependencies

**Expected time:** 1-3 minutes

---

## ▶️ Running the Application

### Step 4: Start Backend Server

**In Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Expected output:**
```
[INFO] Loaded eta_model.joblib
[INFO] Loaded cost_model.joblib
[INFO] Loaded delay_model.joblib
[INFO] Loaded encoders.joblib
[INFO] All models loaded successfully.
[INFO] Starting AI Logistics API on port 5001
 * Running on http://127.0.0.1:5001
```

✅ Backend is ready when you see "Running on http://127.0.0.1:5001"

### Step 5: Start Frontend Server

**In Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v5.4.21  ready in 1091 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

✅ Frontend is ready when you see "Local: http://localhost:3000/"

---

## 🌐 Access the Application

1. **Open your web browser**
2. **Navigate to:** http://localhost:3000
3. **You should see the dashboard with:**
   - Metrics cards (Total Shipments, On-Time Rate, etc.)
   - Shipment creation form
   - Analytics charts
   - Shipment list

---

## 🧪 Testing the System

### Test 1: Create a Shipment

1. Fill in the form:
   - **Distance:** 150 (km)
   - **Traffic:** medium
   - **Weather:** clear
   - **Vehicle:** truck

2. Click **"Create Shipment"**

3. You should see:
   - ✅ Prediction results (ETA, Cost, Delay status)
   - ✅ New shipment appears in the list
   - ✅ Metrics update automatically

### Test 2: Verify Backend API

Open a new terminal and test the API:

```bash
# Health check
curl http://localhost:5001/health

# Expected response:
# {"status":"ok","models_loaded":true,"timestamp":"..."}
```

---

## 📁 Project Structure

```
logistics-ai-system/
├── backend/                    # Python Flask API
│   ├── app.py                 # Main API server
│   ├── train.py               # ML model training
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Trained ML models (generated)
│   │   ├── eta_model.joblib
│   │   ├── cost_model.joblib
│   │   ├── delay_model.joblib
│   │   └── encoders.joblib
│   └── data/                  # Dataset storage (auto-created)
│
└── frontend/                  # React Application
    ├── src/
    │   ├── components/        # React components
    │   ├── pages/            # Dashboard page
    │   ├── services/         # API integration
    │   └── App.jsx           # Main app
    ├── package.json          # Node dependencies
    ├── .env                  # Environment config
    └── vite.config.js        # Vite configuration
```

---

## 🔧 Configuration

### Backend Configuration

**File:** `backend/app.py`

Change port (default: 5001):
```python
port = int(os.environ.get("PORT", 5001))  # Change 5001 to desired port
```

### Frontend Configuration

**File:** `frontend/.env`

Change API URL:
```
VITE_API_URL=http://localhost:5001  # Change to your backend URL
```

**File:** `frontend/vite.config.js`

Change frontend port (default: 3000):
```javascript
server: {
  port: 3000,  // Change to desired port
}
```

---

## 🐛 Troubleshooting

### Issue 1: "pip: command not found"

**Solution:**
- Try `pip3` instead of `pip`
- Or use `python -m pip` or `python3 -m pip`

### Issue 2: "python: command not found"

**Solution:**
- Try `python3` instead of `python`
- Ensure Python is added to PATH

### Issue 3: Port Already in Use

**Backend (Port 5001):**
```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5001 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9
```

### Issue 4: Module Not Found Errors

**Solution:**
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall

cd ../frontend
npm install
```

### Issue 5: CORS Errors in Browser

**Solution:**
- Ensure backend is running on port 5001
- Check `frontend/.env` has correct API URL
- Hard refresh browser (Ctrl+Shift+R)

### Issue 6: Models Not Found

**Solution:**
```bash
cd backend
python train.py
```

This regenerates all model files.

---

## 📊 System Requirements

### Minimum Requirements
- **CPU:** Dual-core processor
- **RAM:** 4 GB
- **Disk:** 500 MB free space
- **OS:** Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommended Requirements
- **CPU:** Quad-core processor
- **RAM:** 8 GB
- **Disk:** 1 GB free space
- **Internet:** Required for initial dataset download

---

## 🔐 Security Notes

### For Development
- Default configuration is suitable for local development
- Backend accepts connections from any origin (CORS enabled)

### For Production
1. **Disable debug mode:**
   ```python
   app.run(host="0.0.0.0", port=5001, debug=False)
   ```

2. **Configure CORS properly:**
   ```python
   CORS(app, origins=["https://yourdomain.com"])
   ```

3. **Use environment variables:**
   - Store sensitive config in `.env` files
   - Never commit `.env` to version control

4. **Use production server:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

---

## 📚 Additional Resources

### API Documentation
- **Health Check:** `GET /health`
- **Create Shipment:** `POST /shipments`
- **Get All Shipments:** `GET /shipments`
- **Get Analytics:** `GET /analytics`
- **Optimize Route:** `POST /optimize-route`

See `README.md` for detailed API documentation.

### Dataset Information
- **Source:** Kaggle Supply Chain Analysis
- **URL:** https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis
- **Size:** ~10 KB
- **Records:** 100 rows

### Technology Stack
- **Backend:** Python 3.8+, Flask 3.0+, XGBoost 2.0+, Scikit-learn 1.4+
- **Frontend:** React 18, Vite 5, Tailwind CSS 3, Recharts 2
- **ML Models:** XGBoost Regressor/Classifier, Random Forest

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] ML models trained (`python train.py`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend server running (port 5001)
- [ ] Frontend server running (port 3000)
- [ ] Dashboard accessible at http://localhost:3000
- [ ] Test shipment created successfully

---

## 🆘 Getting Help

If you encounter issues:

1. **Check terminal output** for error messages
2. **Verify all prerequisites** are installed
3. **Ensure ports 5001 and 3000** are available
4. **Review troubleshooting section** above
5. **Check logs** in terminal windows

---

## 🎉 Success!

If you can:
- ✅ Access the dashboard at http://localhost:3000
- ✅ Create a shipment and see predictions
- ✅ View analytics and charts
- ✅ See shipments in the list

**Congratulations! Your installation is complete and working!**

---

*Last Updated: 2026-04-09*
*Version: 1.0.0*