# backend/app.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from app_logger import setup_logger

from routes.recommend import recommend_bp
from routes.parse     import parse_bp
from routes.chat      import chat_bp

# ── App setup ────────────────────────────────────────────────
app    = Flask(__name__)
logger = setup_logger("app")

app.config.from_object(Config)

CORS(app, origins="*")
# ── Register Blueprints ───────────────────────────────────────
app.register_blueprint(recommend_bp)
app.register_blueprint(parse_bp)
app.register_blueprint(chat_bp)

# ── Health check ──────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status" : "running",
        "app"    : "GrowGuide API",
        "version": "1.0.0",
        "endpoints": [
            "POST /recommend-crop",
            "POST /parse-input",
            "POST /chat",
            "GET  /chat/welcome"
        ]
    }), 200

# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed."}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error."}), 500

# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting GrowGuide API server...")
    logger.info("API running at http://127.0.0.1:5000")
    app.run(
        host  = "0.0.0.0",
        port  = 5000,
        debug = Config.DEBUG
    )