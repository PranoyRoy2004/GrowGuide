import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, request, jsonify
from ml.predict import predict_crop
from app_logger import setup_logger

recommend_bp = Blueprint("recommend", __name__)
logger = setup_logger("recommend")


@recommend_bp.route("/recommend-crop", methods=["POST"])
def recommend_crop():
    """
    Accepts structured soil/climate features and returns crop recommendations.

    Request JSON:
    {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9
    }

    Response JSON:
    {
        "success": true,
        "top_crop": "rice",
        "confidence": 99.5,
        "top_3": [
            {"crop": "rice",    "confidence": 99.5},
            {"crop": "coconut", "confidence": 0.3},
            {"crop": "papaya",  "confidence": 0.2}
        ]
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data received."
            }), 400

        logger.info(f"Received crop recommendation request: {data}")

        # Validate all required keys are present and numeric
        required = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        missing  = [k for k in required if k not in data]

        if missing:
            return jsonify({
                "success": False,
                "error"  : f"Missing required fields: {missing}"
            }), 400

        # Validate numeric types
        for key in required:
            try:
                data[key] = float(data[key])
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error"  : f"Field '{key}' must be a number."
                }), 400

        # Run prediction
        result = predict_crop(data)

        logger.info(f"Prediction result: {result['top_crop']} ({result['confidence']}%)")

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as e:
        logger.error(f"Error in /recommend-crop: {str(e)}")
        return jsonify({
            "success": False,
            "error"  : "Internal server error. Please try again."
        }), 500