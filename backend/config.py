# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Config:
    """Central configuration — all settings pulled from .env"""

    # Flask
    DEBUG    = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    ENV      = os.getenv("FLASK_ENV", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "growguide-secret-2024")

    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Paths
    BASE_DIR  = os.path.dirname(__file__)
    DATA_PATH = os.path.join(BASE_DIR, "data", "crop_data.csv")
    ML_DIR    = os.path.join(BASE_DIR, "ml")
     # CORS — allow all origins
    ALLOWED_ORIGINS = ["*"]
    # CORS — allowed origins for frontend requests
    ALLOWED_ORIGINS = ["http://localhost:5500",   # VS Code Live Server
                       "http://127.0.0.1:5500",
                       "http://localhost:3000",    # React (if ever used)
                       "http://127.0.0.1:5000"]