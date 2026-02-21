# backend/src/config.py

import os

MODELS = {
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-4-5-20251001",
}

MAX_TOKENS = {
    "chat": 1024,
    "analysis": 500,
}

MAX_CONTEXT = 20  # user messages
MIN_ANALYSIS_CONTEXT = 5  # user messages

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///reflektion.db")
SENTRY_DSN = os.getenv("SENTRY_DSN")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLERK_DOMAIN = os.getenv("CLERK_DOMAIN")

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
Update the summary to include:
- Main themes and recurring concerns
- Progress or changes over time  
- Important events mentioned
Keep it concise. Return ONLY the updated summary.
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
    "analysis": "5 per hour",
    "read": "500 per hour",
    "delete": "5 per hour",
}

TIER_LIMITS = {  # type: ignore
    "free": {
        "tokens": 50000,
        "chat_model": MODELS["haiku"],
    },
    "pro": {
        "tokens": 30000,
        "chat_model": MODELS["sonnet"],
    },
}

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
if FLASK_ENV == "production":
    ALLOWED_ORIGINS.append("https://reflektion.vercel.app")
