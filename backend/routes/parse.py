import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, request, jsonify
from nlp.parser import parse_natural_language
from ml.predict import predict_crop
from app_logger import setup_logger

parse_bp = Blueprint("parse", __name__)
logger   = setup_logger("parse")


@parse_bp.route("/parse-input", methods=["POST"])
def parse_input():
    """
    Accepts natural language farm description, extracts features,
    and optionally returns a crop recommendation.

    Request JSON:
    {
        "text": "I live in a tropical region with loamy soil and heavy rainfall.",
        "recommend": true
    }

    Response JSON:
    {
        "success": true,
        "extracted_features": { "N": 80, "P": 48, ... },
        "extraction_method": "hybrid",
        "missing_before_llm": ["P", "K"],
        "recommendation": {          ← only if "recommend": true
            "top_crop": "rice",
            "confidence": 95.2,
            "top_3": [...]
        }
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data or "text" not in data:
            return jsonify({
                "success": False,
                "error"  : "Request must include a 'text' field."
            }), 400

        text = str(data["text"]).strip()

        if len(text) < 5:
            return jsonify({
                "success": False,
                "error"  : "Please provide a more descriptive input."
            }), 400

        if len(text) > 1000:
            return jsonify({
                "success": False,
                "error"  : "Input too long. Please keep it under 1000 characters."
            }), 400

        logger.info(f"Received NLP parse request: '{text[:80]}...'")

        # Parse natural language → structured features
        parsed = parse_natural_language(text)

        response = {
            "success"           : True,
            "extracted_features": parsed["features"],
            "extraction_method" : parsed["extraction_method"],
            "missing_before_llm": parsed["missing_before_llm"]
        }

        # Optionally also return a crop recommendation
        if data.get("recommend", False):
            recommendation = predict_crop(parsed["features"])
            response["recommendation"] = recommendation
            logger.info(f"Auto-recommendation: {recommendation['top_crop']}")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in /parse-input: {str(e)}")
        return jsonify({
            "success": False,
            "error"  : "Internal server error. Please try again."
        }), 500