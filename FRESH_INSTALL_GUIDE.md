# 🚀 Fresh Machine Installation & Setup Guide
## AI-Powered Logistics Optimization System

This guide will walk you through setting up the entire application on a fresh machine from scratch.

---

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **Git** - [Download](https://git-scm.com/downloads)
4. **Code Editor** - VS Code recommended

---

## 🔧 Step 1: System Setup

### Windows
```powershell
# Verify Python installation
python --version

# Verify Node.js installation
node --version
npm --version

# Verify Git installation
git --version
```

### macOS/Linux
```bash
# Verify Python installation
python3 --version

# Verify Node.js installation
node --version
npm --version

# Verify Git installation
git --version
```

---

## 📥 Step 2: Download/Clone the Project

### Option A: Clone from Git (if available)
```bash
git clone <repository-url>
cd logistics-ai-system
```

### Option B: Extract from ZIP
1. Extract the `logistics-ai-system` folder
2. Open terminal/command prompt in that folder

---

## 🐍 Step 3: Backend Setup (Python/Flask)

### Navigate to Backend Directory
```bash
cd backend
```

### Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages include:**
- Flask (Web framework)
- Flask-CORS (Cross-origin support)
- scikit-learn (Machine learning)
- pandas (Data processing)
- numpy (Numerical computing)
- joblib (Model serialization)

### Train ML Models (First Time Only)
```bash
python train.py
```

**Expected output:**
```
Training ETA model...
Training Cost model...
Training Delay model...
Models saved successfully!
```

This creates:
- `models/eta_model.joblib`
- `models/cost_model.joblib`
- `models/delay_model.joblib`
- `models/encoders.joblib`

### Start Backend Server
```bash
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://127.0.0.1:5001
```

✅ **Backend is now running!** Keep this terminal open.

---

## ⚛️ Step 4: Frontend Setup (React/Vite)

### Open New Terminal
Keep the backend terminal running and open a **new terminal**.

### Navigate to Frontend Directory
```bash
cd frontend
```
(If you're in the backend folder, use `cd ../frontend`)

### Install Node Dependencies
```bash
npm install
```

**This installs:**
- React (UI framework)
- Vite (Build tool)
- Tailwind CSS (Styling)
- Axios (HTTP client)
- Lucide React (Icons)
- Recharts (Charts)

**Installation time:** 2-5 minutes depending on internet speed

### Configure Environment Variables

Create `.env` file in the `frontend` folder:

**Windows PowerShell:**
```powershell
@"
VITE_API_URL=http://localhost:5000
VITE_GOOGLE_MAPS_API_KEY=AIzaSyCPJvpZRuKzN6utgg58dVMTULirQQaXpQs
"@ | Out-File -FilePath .env -Encoding utf8
```

**macOS/Linux/Git Bash:**
```bash
cat > .env << EOF
VITE_API_URL=http://localhost:5000
VITE_GOOGLE_MAPS_API_KEY=AIzaSyCPJvpZRuKzN6utgg58dVMTULirQQaXpQs
EOF
```

**Or manually create `.env` file with:**
```env
VITE_API_URL=http://localhost:5000
VITE_GOOGLE_MAPS_API_KEY=AIzaSyCPJvpZRuKzN6utgg58dVMTULirQQaXpQs
```

### Start Frontend Development Server
```bash
npm run dev
```

**Expected output:**
```
VITE v5.4.21  ready in 2392 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

✅ **Frontend is now running!** Keep this terminal open too.

---

## 🌐 Step 5: Access the Application

### Open Your Browser
Navigate to: **http://localhost:3000**

You should see the **AI-Powered Logistics Dashboard**

---

## 🎯 Step 6: Verify Everything Works

### Test 1: Dashboard Tab
1. Click on **Dashboard** tab
2. Fill in the prediction form:
   - **Origin City:** Mumbai
   - **Destination City:** Delhi
   - **Distance:** Should auto-calculate (~1150 km)
   - **Weight:** 500 kg
   - **Traffic:** Medium
   - **Weather:** Clear
   - **Vehicle:** Truck
3. Click **Get Prediction**
4. ✅ Should show ETA, Cost, and Delay predictions

### Test 2: Advanced Features Tab
1. Click on **Advanced Features** tab
2. Try **Alternative Routes**:
   - Select origin and destination
   - Distance auto-calculates
   - Click **Find Alternative Routes**
   - ✅ Should show 3 route options
3. Try **AI-Powered Automated Planning**:
   - Set max shipments: 10
   - Priority: High
   - Vehicle: Truck
   - Max distance: 500 km
   - Click **Generate Automated Plan**
   - ✅ Should show AI-generated shipment plan

### Test 3: Create Shipment
1. Go back to **Dashboard**
2. Fill form and click **Create Shipment**
3. ✅ Should appear in shipment list below

---

## 🛠️ Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'flask'`
```bash
# Make sure virtual environment is activated
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** `FileNotFoundError: models/eta_model.joblib`
```bash
# Train the models first
python train.py
```

**Problem:** Port 5000 already in use
```bash
# Kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**Problem:** `npm: command not found`
- Install Node.js from https://nodejs.org/

**Problem:** `EACCES: permission denied`
```bash
# Run with sudo (macOS/Linux)
sudo npm install

# Or fix npm permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

**Problem:** Port 3000 already in use
- Vite will automatically use next available port (3001, 3002, etc.)
- Or kill the process:
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

**Problem:** White text on white background
- This has been fixed in the latest version
- Make sure you have the updated files

---

## 📁 Project Structure

```
logistics-ai-system/
├── backend/
│   ├── app.py              # Flask API server
│   ├── ai_agent.py         # AI planning agent
│   ├── realtime_agent.py   # Real-time tracking
│   ├── train.py            # ML model training
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Trained ML models
│   └── data/               # Training data
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.jsx         # Main app
│   ├── package.json        # Node dependencies
│   ├── .env                # Environment variables
│   └── vite.config.js      # Vite configuration
└── README.md
```

---

## 🚀 Quick Start Commands

### Start Both Servers (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv first (see Step 3)
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Stop Servers
- Press `Ctrl + C` in each terminal

---

## 🔑 Key Features

### ✅ Implemented Features
1. **ML-Powered Predictions**
   - ETA prediction
   - Cost estimation
   - Delay classification

2. **25 Indian Cities**
   - Auto-distance calculation
   - Real GPS coordinates
   - Haversine formula

3. **Alternative Routes**
   - 3 route options
   - Cost/time comparison
   - AI recommendations

4. **Automated Planning**
   - AI-powered shipment planning
   - Vehicle fleet management
   - Intelligent optimization

5. **Real-time Tracking**
   - Shipment status updates
   - Analytics dashboard
   - Interactive charts

6. **Google Maps Integration**
   - Route visualization
   - API key configured

---

## 📊 System Requirements

### Minimum
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB
- **Storage:** 2 GB free space
- **OS:** Windows 10, macOS 10.14+, Ubuntu 18.04+

### Recommended
- **CPU:** Quad-core 2.5 GHz+
- **RAM:** 8 GB+
- **Storage:** 5 GB free space
- **Internet:** For package installation

---

## 🆘 Getting Help

### Check Logs
**Backend logs:** Visible in backend terminal
**Frontend logs:** Browser console (F12)

### Common URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Health: http://localhost:5000/health

### Documentation Files
- `README.md` - Project overview
- `INSTALLATION.md` - Installation guide
- `SETUP_GUIDE.md` - Setup instructions
- `HOW_TO_SEE_CHANGES.md` - Feature guide
- `FINAL_IMPLEMENTATION.md` - Technical details

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git installed (optional)
- [ ] Project files downloaded/extracted
- [ ] Backend virtual environment created
- [ ] Python dependencies installed
- [ ] ML models trained
- [ ] Backend server running
- [ ] Frontend dependencies installed
- [ ] .env file created
- [ ] Frontend server running
- [ ] Application accessible in browser
- [ ] Dashboard predictions working
- [ ] Alternative routes working
- [ ] Automated planning working

---

## 🎉 Success!

If you've completed all steps and the checklist, your AI-Powered Logistics System is fully operational!

**Next Steps:**
1. Explore all features
2. Create test shipments
3. Try alternative routes
4. Generate automated plans
5. View analytics dashboard

**Enjoy your intelligent logistics platform! 🚀**

---

*Last Updated: April 9, 2026*
*Version: 3.0*
*Google Maps API Key: AIzaSyCPJvpZRuKzN6utgg58dVMTULirQQaXpQs*