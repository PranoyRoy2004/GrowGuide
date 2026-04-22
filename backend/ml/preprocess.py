# backend/ml/preprocess.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib
import os

def load_and_preprocess(data_path: str):
    """
    Loads the crop dataset, encodes labels, and scales features.
    Returns: X (features), y (labels), scaler, label_encoder
    """

    # --- Load ---
    df = pd.read_csv(data_path)
    print(f"[INFO] Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # --- Check for missing values ---
    if df.isnull().sum().any():
        print("[WARNING] Missing values found. Dropping rows...")
        df = df.dropna()
    else:
        print("[INFO] No missing values found. ✅")

    # --- Separate features and target ---
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[feature_cols].values
    y_raw = df['label'].values

    # --- Encode crop labels to integers ---
    # e.g., 'rice' → 0, 'maize' → 1, etc.
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    print(f"[INFO] Crops found: {list(label_encoder.classes_)}")
    print(f"[INFO] Total classes: {len(label_encoder.classes_)}")

    # --- Scale features to range [0, 1] ---
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    print("[INFO] Features scaled using MinMaxScaler. ✅")

    return X_scaled, y, scaler, label_encoder


def save_artifacts(scaler, label_encoder, save_dir: str):
    """
    Saves the scaler and label encoder for use during prediction.
    """
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))
    joblib.dump(label_encoder, os.path.join(save_dir, "label_encoder.pkl"))
    print(f"[INFO] Scaler and LabelEncoder saved to '{save_dir}'. ✅")


if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/crop_data.csv")
    SAVE_DIR = os.path.dirname(__file__)

    X, y, scaler, label_encoder = load_and_preprocess(DATA_PATH)
    save_artifacts(scaler, label_encoder, SAVE_DIR)

    print("\n[DONE] Preprocessing complete.")
    print(f"Feature matrix shape: {X.shape}")
    print(f"Label array shape: {y.shape}")