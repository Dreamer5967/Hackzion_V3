"""
train.py — Smart Logistics ML Pipeline
=======================================
Downloads the Supply Chain Analysis dataset via kagglehub, engineers features
that map to the React frontend's inputs (distance, traffic, weather, vehicle),
trains Random Forest / XGBoost models for ETA and Cost regression plus a
classifier for Delay prediction, and persists everything as joblib artifacts.

Usage:
    python train.py

Outputs (saved to ./models/):
    eta_model.joblib
    cost_model.joblib
    delay_model.joblib
    preprocessor.joblib   <- sklearn ColumnTransformer for inference
    feature_columns.joblib <- ordered list of columns expected by models
"""

import os
import warnings
import joblib
import numpy as np
import pandas as pd
import kagglehub

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] xgboost not installed – falling back to RandomForest everywhere.")

warnings.filterwarnings("ignore")

# ── Output directory ──────────────────────────────────────────────────────────
MODELS_DIR = "./models"
os.makedirs(MODELS_DIR, exist_ok=True)


# =============================================================================
# 1. DATASET ACQUISITION
# =============================================================================

def load_dataset() -> pd.DataFrame:
    print("[1/6] Downloading Supply Chain Analysis dataset via kagglehub ...")
    path = kagglehub.dataset_download("harshsingh2209/supply-chain-analysis")
    print(f"      Dataset path: {path}")

    csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {path}")

    df = pd.read_csv(os.path.join(path, csv_files[0]))
    print(f"      Loaded {len(df):,} rows x {len(df.columns)} columns.")
    print(f"      Columns: {list(df.columns)}\n")
    return df


# =============================================================================
# 2. DATA CLEANING
# =============================================================================

def clean(df: pd.DataFrame) -> pd.DataFrame:
    print("[2/6] Cleaning data ...")
    df = df.copy()

    # Normalise column names
    df.columns = (
        df.columns.str.strip()
               .str.lower()
               .str.replace(r"[\s/\-]+", "_", regex=True)
               .str.replace(r"[^\w]", "", regex=True)
    )

    df.dropna(how="all", inplace=True)

    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            df[col].fillna(df[col].median(), inplace=True)
        else:
            df[col].fillna(df[col].mode()[0], inplace=True)

    print(f"      Shape after cleaning: {df.shape}")
    print(f"      Cleaned columns: {list(df.columns)}\n")
    return df


# =============================================================================
# 3. FEATURE ENGINEERING
# Maps dataset columns to UI inputs: distance, traffic, weather, vehicle
# Targets: eta (hours), cost (USD), delay (0/1)
# =============================================================================

def find_col(df: pd.DataFrame, candidates: list) -> str:
    """Return the first candidate column that exists (fuzzy match)."""
    for c in candidates:
        if c in df.columns:
            return c
    for c in candidates:
        matches = [col for col in df.columns if c in col]
        if matches:
            return matches[0]
    return None


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    print("[3/6] Engineering features ...")
    df = df.copy()

    shipping_time_col = find_col(df, ["shipping_times", "shipping_time", "lead_time", "lead_times"])
    shipping_cost_col = find_col(df, ["shipping_costs", "shipping_cost", "costs"])
    transport_col     = find_col(df, ["transportation_modes", "transportation_mode", "transport_mode", "shipping_carriers", "carrier"])
    defect_col        = find_col(df, ["defect_rates", "defect_rate"])
    risk_col          = find_col(df, ["risk_factors", "risk_factor", "risks"])
    revenue_col       = find_col(df, ["revenue_generated", "revenue", "price"])

    print(f"      Detected -> shipping_time: {shipping_time_col} | shipping_cost: {shipping_cost_col} "
          f"| transport: {transport_col} | defect: {defect_col} | risk: {risk_col}")

    n = len(df)
    rng = np.random.default_rng(42)

    # ── TARGET 1: ETA (hours) ─────────────────────────────────────────────────
    if shipping_time_col:
        df["eta"] = pd.to_numeric(df[shipping_time_col], errors="coerce").fillna(5) * 24
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        base = df[numeric_cols[0]] if numeric_cols else pd.Series(rng.uniform(3, 10, n))
        df["eta"] = (base / base.max() * 120 + 12).clip(2, 200)
    df["eta"] = df["eta"].clip(1, 500)

    # ── TARGET 2: COST (USD) ──────────────────────────────────────────────────
    if shipping_cost_col:
        df["cost"] = pd.to_numeric(df[shipping_cost_col], errors="coerce").fillna(500)
    elif revenue_col:
        df["cost"] = pd.to_numeric(df[revenue_col], errors="coerce").fillna(500) * 0.15
    else:
        df["cost"] = rng.uniform(200, 2000, n)
    df["cost"] = df["cost"].clip(10, 50000)

    # ── SYNTHETIC UI FEATURES ─────────────────────────────────────────────────
    # distance: derived from shipping time
    eta_norm = (df["eta"] - df["eta"].min()) / (df["eta"].max() - df["eta"].min() + 1e-9)
    df["distance"] = (eta_norm * 950 + 50 + rng.normal(0, 30, n)).clip(10, 1500)

    # traffic: defect/risk rate as proxy for "chaos"
    if defect_col:
        proxy = pd.to_numeric(df[defect_col], errors="coerce").fillna(0)
    elif risk_col:
        proxy = pd.to_numeric(df[risk_col], errors="coerce").fillna(0)
    else:
        proxy = pd.Series(rng.uniform(0, 1, n))

    proxy_norm = (proxy - proxy.min()) / (proxy.max() - proxy.min() + 1e-9)
    traffic_bins = pd.cut(proxy_norm, bins=3, labels=["low", "medium", "high"])
    df["traffic"] = traffic_bins.astype(str)

    # weather: random, biased toward rain when delay is expected
    weather_choices = rng.choice(["clear", "rain"], size=n, p=[0.65, 0.35])
    eta_thresh_weather = df["eta"].quantile(0.70)
    rain_mask = (df["eta"] > eta_thresh_weather) & (rng.random(n) < 0.55)
    weather_choices[rain_mask] = "rain"
    df["weather"] = weather_choices

    # vehicle: map transport mode or assign randomly
    if transport_col:
        mode_map = {}
        raw_modes = df[transport_col].str.lower().str.strip().unique()
        for m in raw_modes:
            if any(x in m for x in ["road", "truck", "car", "van"]):
                mode_map[m] = "truck"
            elif any(x in m for x in ["air", "drone", "fly", "plane"]):
                mode_map[m] = "drone"
            elif any(x in m for x in ["rail", "train", "sea", "ship", "water"]):
                mode_map[m] = "train"
            else:
                mode_map[m] = rng.choice(["truck", "drone", "train"])
        df["vehicle"] = df[transport_col].str.lower().str.strip().map(mode_map).fillna("truck")
    else:
        df["vehicle"] = rng.choice(["truck", "drone", "train"], size=n, p=[0.6, 0.15, 0.25])

    # ── Apply UI-feature multipliers so models learn real patterns ────────────
    traffic_eta_mult  = {"low": 0.80, "medium": 1.00, "high": 1.40}
    traffic_cost_mult = {"low": 0.85, "medium": 1.00, "high": 1.30}
    df["eta"]  *= df["traffic"].map(traffic_eta_mult).fillna(1.0)
    df["cost"] *= df["traffic"].map(traffic_cost_mult).fillna(1.0)

    weather_eta_mult  = {"clear": 0.90, "rain": 1.30}
    weather_cost_mult = {"clear": 0.95, "rain": 1.20}
    df["eta"]  *= df["weather"].map(weather_eta_mult).fillna(1.0)
    df["cost"] *= df["weather"].map(weather_cost_mult).fillna(1.0)

    vehicle_eta_mult  = {"truck": 1.00, "drone": 0.45, "train": 1.25}
    vehicle_cost_mult = {"truck": 1.00, "drone": 2.40, "train": 0.65}
    df["eta"]  *= df["vehicle"].map(vehicle_eta_mult).fillna(1.0)
    df["cost"] *= df["vehicle"].map(vehicle_cost_mult).fillna(1.0)

    # Scale by distance
    df["eta"]  = (df["eta"]  * (df["distance"] / 500)).clip(0.5, 500)
    df["cost"] = (df["cost"] * (df["distance"] / 500)).clip(10, 50000)

    # ── TARGET 3: DELAY ───────────────────────────────────────────────────────
    eta_thresh = df["eta"].quantile(0.70)
    df["delay"] = (df["eta"] > eta_thresh).astype(int)

    print(f"      ETA range  : {df['eta'].min():.1f} - {df['eta'].max():.1f} hrs")
    print(f"      Cost range : ${df['cost'].min():.0f} - ${df['cost'].max():.0f}")
    print(f"      Delay split: {df['delay'].value_counts().to_dict()}")
    print(f"      Traffic    : {df['traffic'].value_counts().to_dict()}")
    print(f"      Weather    : {df['weather'].value_counts().to_dict()}")
    print(f"      Vehicle    : {df['vehicle'].value_counts().to_dict()}\n")

    return df


# =============================================================================
# 4. PREPROCESSOR
# =============================================================================

FEATURE_COLS      = ["distance", "traffic", "weather", "vehicle"]
NUMERIC_FEATS     = ["distance"]
CATEGORICAL_FEATS = ["traffic", "weather", "vehicle"]


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline([("scaler", StandardScaler())])
    categorical_pipeline = Pipeline([
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    return ColumnTransformer([
        ("num", numeric_pipeline, NUMERIC_FEATS),
        ("cat", categorical_pipeline, CATEGORICAL_FEATS),
    ])


# =============================================================================
# 5. TRAIN MODELS
# =============================================================================

def train_models(df: pd.DataFrame):
    print("[4/6] Splitting data & fitting models ...")

    X = df[FEATURE_COLS].copy()
    y_eta   = df["eta"].values
    y_cost  = df["cost"].values
    y_delay = df["delay"].values

    splits = train_test_split(
        X, y_eta, y_cost, y_delay,
        test_size=0.2, random_state=42
    )
    X_train, X_test = splits[0], splits[1]
    y_eta_tr,  y_eta_te   = splits[2], splits[3]
    y_cost_tr, y_cost_te  = splits[4], splits[5]
    y_delay_tr,y_delay_te = splits[6], splits[7]

    preprocessor = build_preprocessor()
    X_train_enc  = preprocessor.fit_transform(X_train)
    X_test_enc   = preprocessor.transform(X_test)

    # ETA Regressor
    if XGBOOST_AVAILABLE:
        eta_model = XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0
        )
    else:
        eta_model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

    eta_model.fit(X_train_enc, y_eta_tr)
    eta_pred = eta_model.predict(X_test_enc)
    print(f"      ETA  -> MAE: {mean_absolute_error(y_eta_te, eta_pred):.2f} hrs  "
          f"R2: {r2_score(y_eta_te, eta_pred):.3f}")

    # Cost Regressor
    if XGBOOST_AVAILABLE:
        cost_model = XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0
        )
    else:
        cost_model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

    cost_model.fit(X_train_enc, y_cost_tr)
    cost_pred = cost_model.predict(X_test_enc)
    print(f"      Cost -> MAE: ${mean_absolute_error(y_cost_te, cost_pred):.2f}  "
          f"R2: {r2_score(y_cost_te, cost_pred):.3f}")

    # Delay Classifier
    if XGBOOST_AVAILABLE:
        delay_model = XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            verbosity=0, eval_metric="logloss"
        )
    else:
        delay_model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)

    delay_model.fit(X_train_enc, y_delay_tr)
    delay_pred = delay_model.predict(X_test_enc)
    print(f"      Delay Classifier:\n"
          f"{classification_report(y_delay_te, delay_pred, target_names=['On Time','Delayed'])}")

    return preprocessor, eta_model, cost_model, delay_model


# =============================================================================
# 6. PERSIST
# =============================================================================

def save_artifacts(preprocessor, eta_model, cost_model, delay_model):
    print("[5/6] Saving model artifacts ...")
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, "preprocessor.joblib"))
    joblib.dump(eta_model,    os.path.join(MODELS_DIR, "eta_model.joblib"))
    joblib.dump(cost_model,   os.path.join(MODELS_DIR, "cost_model.joblib"))
    joblib.dump(delay_model,  os.path.join(MODELS_DIR, "delay_model.joblib"))
    joblib.dump(FEATURE_COLS, os.path.join(MODELS_DIR, "feature_columns.joblib"))
    print(f"      Artifacts saved to {MODELS_DIR}/\n")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("  Smart Logistics - ML Training Pipeline")
    print("=" * 60 + "\n")

    df_raw      = load_dataset()
    df_clean    = clean(df_raw)
    df_features = engineer_features(df_clean)
    preprocessor, eta_model, cost_model, delay_model = train_models(df_features)
    save_artifacts(preprocessor, eta_model, cost_model, delay_model)

    print("[6/6] Training complete! Models ready for Flask serving.")
    print("      Run:  python app.py\n")


if __name__ == "__main__":
    main()
