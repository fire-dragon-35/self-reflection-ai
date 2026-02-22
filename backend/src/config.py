# backend/src/config.py

import os
from typing import Any

MODELS = {
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-4-5-20251001",
}

MAX_TOKENS = {
    "chat": 2048,
    "analysis": 2048,
}

MAX_CONTEXT = 10  # user messages
MIN_ANALYSIS_CONTEXT = 5  # user messages

def add_sslmode(db_uri: str) -> str:
    if "sslmode" not in db_uri:
        db_uri += "?sslmode=require"
    return db_uri

DATABASE_URI: str = add_sslmode(os.getenv("DATABASE_URI", "sqlite:///reflektion.db"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLERK_DOMAIN = os.getenv("CLERK_DOMAIN")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
SENTRY_DSN = os.getenv("SENTRY_DSN")

BIG_FIVE_PROMPT_HEADER = f"""
Analyse this conversation and determine the user's Big Five personality traits.
Return ONLY valid JSON with this exact structure:
{{
  "openness": <float 0-10>,
  "conscientiousness": <float 0-10>,
  "extraversion": <float 0-10>,
  "agreeableness": <float 0-10>,
  "neuroticism": <float 0-10>
}}
"""

ATTACHMENT_STYLE_PROMPT_HEADER = f"""
Analyse this conversation for attachment style patterns.
Return ONLY valid JSON with this exact structure:
{{
  "anxiety_score": <float 0-10>,
  "avoidance_score": <float 0-10>,
  "style": "<Secure|Anxious Preoccupied|Dismissive Avoidant|Fearful Avoidant>"
}}
"""

SUMMARY_PROMPT_HEADER = """
You maintain a rolling summary of the user's conversations.
Never refer to yourself.
Update the summary to include:
- Main themes and recurring concerns
- Progress or changes over time  
- Important events mentioned
Keep it concise (under 500 words). Return ONLY the updated summary. 
"""

CHAT_PROMPT_HEADER = """
You help people reflect on their thoughts and emotions.
Guidelines:
- Be direct and conversational. No excessive formatting or emojis.
- Challenge me when needed - don't just validate. 
- Prioritize truth over comfort. 
- Point out if the conversation is going in circles. 
- Keep responses brief unless depth is needed.
- If you don't know something, say so.
Your role is to help me understand myself better, not to make me feel better.
"""

# these are just for extra protection against spam
RATE_LIMITS = {
    "chat": "50 per hour",
    "analysis": "20 per hour",
    "read": "500 per hour",
    "delete": "20 per hour",
}
TOKEN_PACKAGES: dict[str, dict[str, Any]] = {
    "small": {"tokens": 200000, "price": 2.99, "price_id": "price_1T3KMFD57iw5zYt253WDgE1I"},
    "medium": {"tokens": 500000, "price": 4.99, "price_id": "price_1T3KMmD57iw5zYt203GSmE9z"},
    "large": {"tokens": 1000000, "price": 8.99, "price_id": "price_1T3KNUD57iw5zYt2gksBlvnf"},
}

FREE_TOKENS = 40000

ALLOWED_ORIGINS = {
    "development": "http://localhost:5173",
    "production": "https://reflektion.app"
}
