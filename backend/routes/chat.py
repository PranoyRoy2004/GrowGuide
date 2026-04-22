import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, request, jsonify
from chatbot.assistant import chat, get_welcome_message
from app_logger import setup_logger

chat_bp = Blueprint("chat", __name__)
logger  = setup_logger("chat")


@chat_bp.route("/chat", methods=["POST"])
def chat_endpoint():
    """
    Accepts a user message and conversation history,
    returns the assistant's response and updated history.

    Request JSON:
    {
        "message": "How often should I irrigate rice?",
        "history": []
    }

    Response JSON:
    {
        "success": true,
        "response": "Rice requires...",
        "updated_history": [...],
        "tokens_used": 312
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data or "message" not in data:
            return jsonify({
                "success": False,
                "error"  : "Request must include a 'message' field."
            }), 400

        message = str(data["message"]).strip()
        history = data.get("history", [])

        if not message:
            return jsonify({
                "success": False,
                "error"  : "Message cannot be empty."
            }), 400

        if len(message) > 2000:
            return jsonify({
                "success": False,
                "error"  : "Message too long. Please keep it under 2000 characters."
            }), 400

        # Validate history format
        if not isinstance(history, list):
            history = []

        logger.info(f"Chat message received: '{message[:60]}...'")

        result = chat(message, history)

        return jsonify({
            "success"         : True,
            "response"        : result["response"],
            "updated_history" : result["updated_history"],
            "tokens_used"     : result["tokens_used"]
        }), 200

    except Exception as e:
        logger.error(f"Error in /chat: {str(e)}")
        return jsonify({
            "success": False,
            "error"  : "Internal server error. Please try again."
        }), 500


@chat_bp.route("/chat/welcome", methods=["GET"])
def welcome():
    """Returns the chatbot's opening greeting."""
    return jsonify({
        "success" : True,
        "message" : get_welcome_message()
    }), 200