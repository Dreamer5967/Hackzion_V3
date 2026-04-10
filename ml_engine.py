import joblib
import os
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Dynamically load the model and its required features
try:
    eta_model = joblib.load(os.path.join(MODEL_DIR, 'dynamic_eta_model.pkl'))
    imputer = joblib.load(os.path.join(MODEL_DIR, 'data_imputer.pkl'))
    feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.pkl'))
    MODELS_LOADED = True
except FileNotFoundError:
    print("⚠️ WARNING: Models not found. Run train_model.py first.")
    MODELS_LOADED = False

def predict_base_eta(shipment_data):
    """
    Dynamically maps the input data to whatever features the model was trained on.
    """
    if not MODELS_LOADED:
        return 5.0 # Fallback
    
    try:
        # Create an empty array for the features
        input_features = []
        
        # Match incoming data to required features
        for feature in feature_names:
            # If the user/app provided this specific feature (e.g., shipping_costs)
            if feature in shipment_data:
                input_features.append(shipment_data[feature])
            # If we don't have it (e.g. we don't know 'weather_condition_severity' right now)
            else:
                input_features.append(np.nan) # Mark as missing
                
        # Use the imputer to safely fill the 'nan' values with historical averages
        final_features = imputer.transform([input_features])

        # Predict!
        prediction = eta_model.predict(final_features)
        return float(prediction[0])
    
    except Exception as e:
        print(f"Prediction Error: {e}")
        return 5.0