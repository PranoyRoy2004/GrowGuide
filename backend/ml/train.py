# backend/ml/train.py

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from preprocess import load_and_preprocess, save_artifacts


# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DATA_PATH  = os.path.join(BASE_DIR, "../data/crop_data.csv")
SAVE_DIR   = BASE_DIR


def train():
    print("\n" + "=" * 55)
    print("       GROWGUIDE — MODEL TRAINING PIPELINE")
    print("=" * 55)

    # ── 1. Load & preprocess ──────────────────────────────────
    X, y, scaler, label_encoder = load_and_preprocess(DATA_PATH)
    save_artifacts(scaler, label_encoder, SAVE_DIR)

    # ── 2. Train / test split (80 / 20) ──────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y          # ensures every crop appears in both splits
    )
    print(f"\n[INFO] Training samples : {X_train.shape[0]}")
    print(f"[INFO] Testing  samples : {X_test.shape[0]}")

    # ── 3. Hyperparameter tuning with GridSearchCV ────────────
    print("\n[INFO] Running hyperparameter search (this may take ~1 min)...")

    param_grid = {
        "n_estimators"      : [100, 200],
        "max_depth"         : [None, 10, 20],
        "min_samples_split" : [2, 5],
    }

    grid_search = GridSearchCV(
        estimator  = RandomForestClassifier(random_state=42),
        param_grid = param_grid,
        cv         = 5,         # 5-fold cross-validation
        scoring    = "accuracy",
        n_jobs     = -1,        # use all CPU cores
        verbose    = 1
    )
    grid_search.fit(X_train, y_train)

    best_params = grid_search.best_params_
    print(f"\n[INFO] Best hyperparameters found: {best_params}")

    # ── 4. Train final model with best params ─────────────────
    model = RandomForestClassifier(**best_params, random_state=42)
    model.fit(X_train, y_train)
    print("[INFO] Model trained successfully. ✅")

    # ── 5. Cross-validation score ─────────────────────────────
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"\n[INFO] Cross-validation accuracy scores : {cv_scores.round(4)}")
    print(f"[INFO] Mean CV accuracy                 : {cv_scores.mean():.4f}")
    print(f"[INFO] Std  CV accuracy                 : {cv_scores.std():.4f}")

    # ── 6. Evaluate on test set ───────────────────────────────
    y_pred = model.predict(X_test)

    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"\n[INFO] Test set accuracy : {test_accuracy:.4f}")

    print("\n" + "=" * 55)
    print("CLASSIFICATION REPORT")
    print("=" * 55)
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_
    ))

    # ── 7. Feature importance ─────────────────────────────────
    feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    importances   = model.feature_importances_

    print("=" * 55)
    print("FEATURE IMPORTANCES")
    print("=" * 55)
    for feat, imp in sorted(zip(feature_names, importances),
                            key=lambda x: x[1], reverse=True):
        bar = "█" * int(imp * 50)
        print(f"  {feat:<12} {imp:.4f}  {bar}")

    # ── 8. Save the model ─────────────────────────────────────
    model_path = os.path.join(SAVE_DIR, "model.pkl")
    joblib.dump(model, model_path)
    print(f"\n[INFO] Model saved to '{model_path}'. ✅")

    print("\n" + "=" * 55)
    print("  TRAINING COMPLETE 🌱")
    print("=" * 55)


if __name__ == "__main__":
    train()