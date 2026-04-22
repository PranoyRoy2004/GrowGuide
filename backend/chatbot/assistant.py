# backend/chatbot/assistant.py

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# ── Load knowledge base ───────────────────────────────────────────────────────
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")

try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
    print("[INFO] Knowledge base loaded successfully. ✅")
except FileNotFoundError:
    KNOWLEDGE_BASE = ""
    print("[WARNING] knowledge_base.txt not found. Chatbot will use LLM general knowledge only.")


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are GrowGuide, a friendly and knowledgeable AI agriculture assistant.

Your expertise covers:
- Crop selection and plantation techniques
- Soil health and fertilizer recommendations
- Irrigation methods and water management
- Pest and disease identification and control
- Seasonal farming practices
- Harvesting and post-harvest storage
- Organic and sustainable farming

Personality:
- Warm, patient, and encouraging — many users are small-scale farmers
- Use simple language; avoid heavy jargon unless asked for technical details
- Give practical, actionable advice
- When uncertain, say so honestly rather than guessing
- Keep responses focused and concise (3-6 sentences for simple questions)
- For complex topics, use short numbered steps or bullet points

Boundaries:
- Only answer agriculture-related questions
- If asked about unrelated topics, politely redirect to farming topics
- Do not recommend illegal substances or practices

Reference knowledge base:
{KNOWLEDGE_BASE}
"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CHAT FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def chat(user_message: str, conversation_history: list) -> dict:
    """
    Sends a user message to the Groq LLM and returns a response.
    Maintains conversation context through history.

    Args:
        user_message (str): The user's current message
        conversation_history (list): List of previous messages:
            [{"role": "user"|"assistant", "content": str}, ...]

    Returns:
        dict: {
            "response": str,
            "updated_history": list,
            "tokens_used": int
        }
    """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Build the full message list for the API
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",            
            messages    = messages,
            temperature = 0.7,    # balanced creativity vs consistency
            max_tokens  = 600,    # enough for detailed but focused answers
        )

        assistant_message = response.choices[0].message.content.strip()
        tokens_used       = response.usage.total_tokens

        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]

        # Keep history to last 10 exchanges (20 messages) to avoid token overflow
        if len(updated_history) > 20:
            updated_history = updated_history[-20:]

        return {
            "response"        : assistant_message,
            "updated_history" : updated_history,
            "tokens_used"     : tokens_used
        }

    except Exception as e:
        error_msg = f"I'm having trouble connecting right now. Please try again in a moment. (Error: {str(e)})"
        return {
            "response"        : error_msg,
            "updated_history" : conversation_history,
            "tokens_used"     : 0
        }


def get_welcome_message() -> str:
    """Returns the initial greeting when a user opens the chat."""
    return (
        "👋 Hello! I'm GrowGuide, your AI agriculture assistant. "
        "I can help you with crop selection, soil health, irrigation, "
        "pest control, fertilizers, and general farming advice. "
        "What would you like to know today? 🌱"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Quick tests when run directly
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("  GROWGUIDE CHATBOT — INTERACTIVE TEST")
    print("=" * 55)
    print(f"\nGrowGuide: {get_welcome_message()}\n")

    history = []
    test_questions = [
        "How often should I water rice crops?",
        "What fertilizer is best for improving nitrogen?",
        "My wheat leaves are turning yellow. What could be wrong?",
        "What's the best crop for black soil in summer?",
    ]

    for question in test_questions:
        print(f"You: {question}")
        result = chat(question, history)
        history = result["updated_history"]
        print(f"\nGrowGuide: {result['response']}")
        print(f"[tokens used: {result['tokens_used']}]")
        print("\n" + "─" * 55 + "\n")
    