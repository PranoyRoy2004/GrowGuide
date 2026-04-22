# backend/ml/predict.py

import os
import joblib
import numpy as np

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR            = os.path.dirname(__file__)
MODEL_PATH          = os.path.join(BASE_DIR, "model.pkl")
SCALER_PATH         = os.path.join(BASE_DIR, "scaler.pkl")
LABEL_ENCODER_PATH  = os.path.join(BASE_DIR, "label_encoder.pkl")


# ─────────────────────────────────────────
# Load artifacts once at import time
# (avoids reloading on every API request)
# ─────────────────────────────────────────
try:
    model         = joblib.load(MODEL_PATH)
    scaler        = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    print("[INFO] ML artifacts loaded successfully. ✅")
except FileNotFoundError as e:
    raise RuntimeError(
        f"[ERROR] Model artifact not found: {e}. "
        "Please run ml/train.py first."
    )


def predict_crop(features: dict) -> dict:
    """
    Takes a dictionary of 7 soil/climate features and returns
    the top-3 recommended crops with confidence scores.

    Args:
        features (dict): Keys must be:
            N, P, K, temperature, humidity, ph, rainfall

    Returns:
        dict: {
            "top_crop": str,
            "confidence": float,
            "top_3": [ {"crop": str, "confidence": float}, ... ]
        }
    """

    REQUIRED_KEYS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

    # ── Validate input ────────────────────────────────────────
    missing = [k for k in REQUIRED_KEYS if k not in features]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    # ── Build feature array in the correct order ──────────────
    input_array = np.array([[features[k] for k in REQUIRED_KEYS]])

    # ── Scale using the saved scaler ─────────────────────────
    input_scaled = scaler.transform(input_array)

    # ── Predict probabilities for all 22 crops ────────────────
    probabilities = model.predict_proba(input_scaled)[0]

    # ── Get top-3 crops ───────────────────────────────────────
    top3_indices = np.argsort(probabilities)[::-1][:3]

    top3 = [
        {
            "crop"      : label_encoder.classes_[i],
            "confidence": round(float(probabilities[i]) * 100, 2)
        }
        for i in top3_indices
    ]

    return {
        "top_crop"  : top3[0]["crop"],
        "confidence": top3[0]["confidence"],
        "top_3"     : top3
    }


# ─────────────────────────────────────────
# Quick test when run directly
# ─────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "N"          : 90,
        "P"          : 42,
        "K"          : 43,
        "temperature": 20.87,
        "humidity"   : 82.00,
        "ph"         : 6.50,
        "rainfall"   : 202.93
    }

    result = predict_crop(sample)

    print("\n── Prediction Result ──────────────────────")
    print(f"  Top crop   : {result['top_crop']}")
    print(f"  Confidence : {result['confidence']}%")
    print("\n  Top 3 recommendations:")
    for i, rec in enumerate(result['top_3'], 1):
        print(f"    {i}. {rec['crop']:<15} {rec['confidence']}%")