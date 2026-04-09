"""
app.py — Smart Logistics Flask API
====================================
Serves ML model predictions via /predict endpoint.
Loads trained joblib artifacts from ./models/ at startup.

Endpoints:
    GET  /health          — liveness probe
    POST /predict         — returns eta, cost, delay prediction

Expected POST /predict body:
    {
        "distance": 85.5,
        "traffic":  "high",
        "weather":  "rain",
        "vehicle":  "truck"
    }

Response:
    {
        "eta":   4.15,
        "cost":  1250.00,
        "delay": "Delay Expected"
    }
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── App init ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow React dev server (localhost:3000) to call the API

# ── Model store (populated at startup) ───────────────────────────────────────
MODELS = {}
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# ── Valid input values ────────────────────────────────────────────────────────
VALID_TRAFFIC = {"low", "medium", "high"}
VALID_WEATHER = {"clear", "rain"}
VALID_VEHICLE = {"truck", "drone", "train"}

# ── Delay label mapping ───────────────────────────────────────────────────────
DELAY_LABELS = {
    0: "On Time",
    1: "Delay Expected",
}


# =============================================================================
# STARTUP: Load Models
# =============================================================================

def load_models():
    """Load all joblib artifacts into memory at Flask startup."""
    required = ["preprocessor.joblib", "eta_model.joblib",
                "cost_model.joblib",  "delay_model.joblib"]

    for artifact in required:
        path = os.path.join(MODELS_DIR, artifact)
        if not os.path.exists(path):
            log.error(
                f"Model artifact not found: {path}\n"
                f"  -> Run `python train.py` first to generate models."
            )
            raise FileNotFoundError(
                f"Missing model artifact: {artifact}. "
                f"Please run train.py before starting the server."
            )
        key = artifact.replace(".joblib", "")
        MODELS[key] = joblib.load(path)
        log.info(f"Loaded {artifact}")

    log.info("All models loaded successfully.")


# =============================================================================
# HELPERS
# =============================================================================

def validate_input(data: dict) -> tuple[bool, str]:
    """Validate incoming prediction request. Returns (ok, error_message)."""
    if not isinstance(data.get("distance"), (int, float)):
        return False, "'distance' must be a number (float or int)."

    if data["distance"] <= 0:
        return False, "'distance' must be a positive number."

    if data.get("traffic") not in VALID_TRAFFIC:
        return False, f"'traffic' must be one of {sorted(VALID_TRAFFIC)}."

    if data.get("weather") not in VALID_WEATHER:
        return False, f"'weather' must be one of {sorted(VALID_WEATHER)}."

    if data.get("vehicle") not in VALID_VEHICLE:
        return False, f"'vehicle' must be one of {sorted(VALID_VEHICLE)}."

    return True, ""


def build_feature_frame(data: dict) -> pd.DataFrame:
    """Convert raw request dict to a single-row DataFrame ready for inference."""
    return pd.DataFrame([{
        "distance": float(data["distance"]),
        "traffic":  str(data["traffic"]).lower().strip(),
        "weather":  str(data["weather"]).lower().strip(),
        "vehicle":  str(data["vehicle"]).lower().strip(),
    }])


def predict(data: dict) -> dict:
    """Run all three models and return formatted prediction dict."""
    X_raw = build_feature_frame(data)
    X_enc = MODELS["preprocessor"].transform(X_raw)

    eta   = float(np.round(MODELS["eta_model"].predict(X_enc)[0], 2))
    cost  = float(np.round(MODELS["cost_model"].predict(X_enc)[0], 2))
    delay_class = int(MODELS["delay_model"].predict(X_enc)[0])
    delay_label = DELAY_LABELS.get(delay_class, "Unknown")

    # Add emoji indicators for the React frontend
    delay_display = (
        f"Delay Expected" if delay_class == 1 else "On Time"
    )

    return {
        "eta":   eta,
        "cost":  cost,
        "delay": delay_display,
    }


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/health")
def health():
    """Simple liveness probe — returns 200 if models are loaded."""
    models_ok = all(k in MODELS for k in
                    ["preprocessor", "eta_model", "cost_model", "delay_model"])
    return jsonify({
        "status": "ok" if models_ok else "degraded",
        "models_loaded": models_ok,
    }), 200 if models_ok else 503


@app.post("/predict")
def predict_route():
    """
    POST /predict
    Body: { "distance": float, "traffic": str, "weather": str, "vehicle": str }
    Returns: { "eta": float, "cost": float, "delay": str }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON (Content-Type: application/json)."}), 415

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or empty JSON body."}), 400

    ok, err = validate_input(data)
    if not ok:
        return jsonify({"error": err}), 422

    try:
        result = predict(data)
        log.info(
            f"Prediction | distance={data['distance']} traffic={data['traffic']} "
            f"weather={data['weather']} vehicle={data['vehicle']} "
            f"-> eta={result['eta']} cost={result['cost']} delay={result['delay']}"
        )
        return jsonify(result), 200

    except Exception as exc:
        log.exception("Prediction failed")
        return jsonify({"error": f"Internal prediction error: {str(exc)}"}), 500


# Optional: keep old GET-style predict for quick browser testing
@app.get("/predict")
def predict_get():
    """
    GET /predict?distance=85.5&traffic=high&weather=rain&vehicle=truck
    Convenience endpoint for quick manual testing in a browser / curl.
    """
    try:
        data = {
            "distance": float(request.args.get("distance", 100)),
            "traffic":  request.args.get("traffic",  "medium"),
            "weather":  request.args.get("weather",  "clear"),
            "vehicle":  request.args.get("vehicle",  "truck"),
        }
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid query parameter: {exc}"}), 422

    ok, err = validate_input(data)
    if not ok:
        return jsonify({"error": err}), 422

    try:
        result = predict(data)
        return jsonify(result), 200
    except Exception as exc:
        log.exception("Prediction failed (GET)")
        return jsonify({"error": f"Internal prediction error: {str(exc)}"}), 500


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    load_models()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    log.info(f"Starting Smart Logistics API on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
else:
    # When run via gunicorn / uwsgi
    load_models()
