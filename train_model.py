import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer
import joblib
import os

print("🚀 Starting Dynamic AI Model Training...")

# 1. Load Data (Can be ANY supply chain dataset)
DATA_FILE = 'dynamic_supply_chain_logistics_dataset.csv' # Update this to your active file

try:
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded dataset with {len(df)} records and {len(df.columns)} columns.")
except FileNotFoundError:
    print(f"❌ ERROR: Cannot find '{DATA_FILE}'. Please check the folder.")
    exit()

# 2. Automatically Identify Target & Features
# It looks for 'lead_time_days', but will fallback to 'Lead times' or similar
target_col = next((col for col in df.columns if 'lead' in col.lower() and 'time' in col.lower()), None)

if not target_col:
    print("❌ ERROR: Could not find a 'Lead Time' column to predict. Please ensure your dataset has one.")
    exit()

print(f"🎯 Target identified as: '{target_col}'")

# Drop non-predictive columns (timestamps, IDs, GPS, and target)
cols_to_drop = [target_col] + [c for c in df.columns if 'time' in c.lower() and 'stamp' in c.lower()]
cols_to_drop += [c for c in df.columns if 'latitude' in c.lower() or 'longitude' in c.lower() or 'id' in c.lower()]

# Select only numeric features to ensure adaptability without complex text encoding
X = df.drop(columns=[c for c in cols_to_drop if c in df.columns]).select_dtypes(include=[np.number])
y = df[target_col]

# Save the exact feature names the model learned on
feature_names = list(X.columns)

# 3. Handle Missing Data Dynamically (Fills blanks with the column's average)
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# 4. Train Model
X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.2, random_state=42)

print(f"🧠 Training Random Forest on {len(feature_names)} dynamic features...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print(f"📊 Model Accuracy: Off by an average of {mae:.2f} days.")

# 5. Save the Brain, the Imputer, and the Feature Map
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/dynamic_eta_model.pkl')
joblib.dump(imputer, 'models/data_imputer.pkl')
joblib.dump(feature_names, 'models/feature_names.pkl')

print("\n✅ SUCCESS! AI is trained and adapted to the new dataset.")