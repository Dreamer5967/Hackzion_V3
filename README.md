# AI-Powered Intelligent Logistics Optimization System

A comprehensive logistics optimization platform leveraging AI/ML for predictive analytics, route optimization, and automated shipment planning.

## 🎯 Problem Statement

Traditional logistics systems lack the ability to dynamically adapt to real-time conditions and often fail to provide accurate delivery predictions. This system addresses these challenges by building an intelligent platform that can:

- Predict delivery times (ETA) with high accuracy
- Estimate costs based on multiple factors
- Detect potential delays before they occur
- Optimize routes dynamically
- Automate shipment planning and allocation

## 🚀 Features

### Core Capabilities
- **ETA Prediction**: ML-powered estimation of delivery times
- **Cost Estimation**: Accurate cost forecasting based on distance, vehicle, and conditions
- **Delay Classification**: Proactive delay detection using traffic and weather data
- **Route Optimization**: Intelligent route planning for multiple shipments
- **Real-time Monitoring**: Live tracking and status updates
- **Analytics Dashboard**: Comprehensive insights and performance metrics

### Technical Features
- RESTful API with Flask backend
- React-based responsive frontend
- XGBoost and Random Forest ML models
- Real-time data processing
- Automated model training pipeline
- Interactive data visualizations

## 📋 System Architecture

```
logistics-ai-system/
├── backend/                 # Python Flask API
│   ├── app.py              # Main API server
│   ├── train.py            # ML model training
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Trained ML models
│   ├── data/               # Dataset storage
│   ├── routes/             # API routes
│   └── utils/              # Utility functions
│
└── frontend/               # React application
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── services/       # API services
    │   └── utils/          # Helper functions
    ├── public/             # Static assets
    └── package.json        # Node dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd logistics-ai-system/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Train ML models:
```bash
python train.py
```
This will:
- Download the Supply Chain dataset from Kaggle
- Process and engineer features
- Train ETA, cost, and delay prediction models
- Save models to `models/` directory

4. Start the Flask API server:
```bash
python app.py
```
The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd logistics-ai-system/frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`

## 📊 API Endpoints

### Health Check
```
GET /health
```
Returns system status and model availability.

### Predict Shipment
```
POST /predict
Content-Type: application/json

{
  "distance": 150.5,
  "traffic": "medium",
  "weather": "clear",
  "vehicle": "truck"
}
```
Returns ETA, cost, and delay predictions.

### Create Shipment
```
POST /shipments
Content-Type: application/json

{
  "distance": 150.5,
  "traffic": "medium",
  "weather": "clear",
  "vehicle": "truck"
}
```
Creates a new shipment with predictions.

### Get All Shipments
```
GET /shipments
```
Returns list of all shipments.

### Optimize Route
```
POST /optimize-route
Content-Type: application/json

{
  "shipments": [
    {"id": 1, "distance": 100, "priority": 1},
    {"id": 2, "distance": 50, "priority": 2}
  ]
}
```
Returns optimized route order.

### Get Analytics
```
GET /analytics
```
Returns dashboard analytics data.

## 🎨 Frontend Features

### Dashboard
- Real-time metrics cards (total shipments, on-time rate, avg ETA, avg cost)
- Interactive prediction form
- Shipment list with detailed information
- Performance analytics charts
- Vehicle distribution statistics

### Components
- **PredictionForm**: Create new shipments with instant predictions
- **ShipmentList**: View all shipments with status indicators
- **AnalyticsChart**: Visualize trends and patterns
- **MetricsCard**: Display key performance indicators

## 🧠 Machine Learning Models

### 1. ETA Prediction Model
- **Algorithm**: XGBoost Regressor
- **Features**: Distance, traffic, weather, vehicle type
- **Output**: Estimated time of arrival (hours)

### 2. Cost Estimation Model
- **Algorithm**: Random Forest Regressor
- **Features**: Distance, traffic, weather, vehicle type
- **Output**: Estimated cost ($)

### 3. Delay Classification Model
- **Algorithm**: XGBoost Classifier
- **Features**: Distance, traffic, weather, vehicle type
- **Output**: Binary classification (On Time / Delayed)

## 📈 Model Performance

The models are trained on simulated logistics data with the following considerations:
- Traffic conditions (low, medium, high)
- Weather conditions (clear, rain)
- Vehicle types (truck, drone, train)
- Distance ranges (10-500 km)

Performance metrics are logged during training and can be viewed in the console output.

## 🔧 Configuration

### Backend Configuration
Edit `backend/app.py` to configure:
- Port number (default: 5000)
- Debug mode
- CORS settings

### Frontend Configuration
Edit `frontend/vite.config.js` to configure:
- Port number (default: 3000)
- API proxy settings

## 📦 Dataset

The system uses the Supply Chain Analysis dataset from Kaggle:
https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis

The training script automatically downloads this dataset using `kagglehub`.

## 🎯 Evaluation Criteria Alignment

| Criteria | Implementation |
|----------|----------------|
| **Prediction Accuracy** | XGBoost and Random Forest models with feature engineering |
| **Optimization Efficiency** | Route optimization algorithm for multiple shipments |
| **Innovation** | AI-powered predictions with real-time adaptation |
| **Automation Level** | Automated model training, prediction, and shipment creation |
| **Practicality** | RESTful API, responsive UI, real-world applicable |
| **Presentation** | Interactive dashboard with visualizations |

## 🚀 Usage Examples

### Creating a Shipment
1. Open the dashboard at `http://localhost:3000`
2. Fill in the shipment details:
   - Distance (km)
   - Traffic condition
   - Weather condition
   - Vehicle type
3. Click "Create Shipment"
4. View instant predictions and shipment details

### Viewing Analytics
- Dashboard automatically displays:
  - Total shipments
  - On-time delivery rate
  - Average ETA and cost
  - Vehicle distribution
  - Performance trends

## 🔮 Future Enhancements

- Real-time GPS tracking integration
- Advanced route optimization (TSP, genetic algorithms)
- Multi-modal transportation planning
- Weather API integration
- IoT sensor data integration
- Blockchain for supply chain transparency
- Mobile application
- Predictive maintenance for vehicles

## 📝 License

This project is created for the AI-Powered Intelligent Logistics Optimization System hackathon.

## 👥 Contributing

This is a hackathon project. For improvements or suggestions, please create an issue or pull request.

## 🙏 Acknowledgments

- Kaggle for the Supply Chain Analysis dataset
- Flask and React communities
- Scikit-learn and XGBoost developers