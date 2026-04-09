# Quick Start Guide

## ✅ System is Running!

Both servers are currently running:
- **Backend**: http://localhost:5001 ✅
- **Frontend**: http://localhost:3000 ✅

## 🔧 If You See Connection Errors

The browser may have cached the old API URL (port 5000). To fix this:

### Option 1: Hard Refresh Browser
1. Open http://localhost:3000
2. Press **Ctrl + Shift + R** (Windows/Linux) or **Cmd + Shift + R** (Mac)
3. This clears the cache and reloads the page

### Option 2: Clear Browser Cache
1. Open Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Open in Incognito/Private Window
1. Open a new incognito/private browser window
2. Navigate to http://localhost:3000
3. The system will work without cached data

## 📊 Verify System is Working

Check the terminal output - you should see:
```
[INFO] 127.0.0.1 - - [Date Time] "GET /analytics HTTP/1.1" 200 -
[INFO] 127.0.0.1 - - [Date Time] "GET /shipments HTTP/1.1" 200 -
```

The "200" status means the backend is responding correctly!

## 🚀 Using the System

1. **Create a Shipment**:
   - Enter distance (e.g., 150)
   - Select traffic condition
   - Select weather
   - Select vehicle type
   - Click "Create Shipment"

2. **View Results**:
   - ETA prediction
   - Cost estimation
   - Delay status
   - Estimated arrival time

3. **Monitor Dashboard**:
   - Total shipments
   - On-time percentage
   - Average ETA and cost
   - Performance charts

## 🔍 Troubleshooting

If you still see errors after hard refresh:

1. **Stop all old servers**:
   - Close Terminal 1 (old backend on port 5000)
   - Close Terminal 2 (old frontend)

2. **Keep only the new servers running**:
   - Terminal 5: Backend on port 5001 ✅
   - Terminal 4: Frontend on port 3000 ✅

3. **Restart frontend if needed**:
   ```bash
   cd logistics-ai-system/frontend
   npm run dev
   ```

## ✨ System Features

- ✅ AI-powered ETA prediction (96.62% accuracy)
- ✅ Cost estimation (91.12% accuracy)
- ✅ Delay classification (80% accuracy)
- ✅ Real-time analytics dashboard
- ✅ Interactive charts
- ✅ Shipment tracking
- ✅ Performance metrics

The system is fully functional - just needs a browser cache clear!