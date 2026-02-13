# backend/src/config.py

import os

MODELS = {
    "chat": "claude-sonnet-4-20250514",
    "analysis": "claude-haiku-4-20250514",
}

MAX_TOKENS = {
    "chat": 1024,
    "analysis": 500,
}

MAX_CONTEXT_MESSAGES = 20
ANALYSIS_FREQUENCY = 5

DATABASE_URL = os.getenv("DATABASE_URL")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
SENTRY_DSN = os.getenv("SENTRY_DSN")
FLASK_ENV = os.getenv("FLASK_ENV", "development")

BIG_FIVE_PROMPT_HEADER = f"""Analyze this conversation and determine the user's Big Five personality traits.
Return ONLY valid JSON with this exact structure:
{{
  "openness": <float 0-10>,
  "conscientiousness": <float 0-10>,
  "extraversion": <float 0-10>,
  "agreeableness": <float 0-10>,
  "neuroticism": <float 0-10>
}}"""

ATTACHMENT_STYLE_PROMPT_HEADER = f"""Analyze this conversation for attachment style patterns.
Return ONLY valid JSON with this exact structure:
{{
  "anxiety_score": <float 0-10>,
  "avoidance_score": <float 0-10>,
  "style": "<Secure|Anxious Preoccupied|Dismissive Avoidant|Fearful Avoidant>"
}}"""

RATE_LIMITS = {
    "chat": "30 per hour",
    "analysis": "5 per hour",
    "read": "100 per hour",
    "delete": "2 per day",
}

FRONTEND_URL = "http://localhost:5173"

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
if FLASK_ENV == "production":
    ALLOWED_ORIGINS.append("https://yourapp.vercel.app")
