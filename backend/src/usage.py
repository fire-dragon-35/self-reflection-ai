# backend/src/usage.py

from models import db
from datetime import datetime, timezone
from config import FREE_TOKENS
from services import get_or_create_user

# cache
used_tokens_cache: dict[str, int] = {}


def check_token_limit(user_id: str) -> bool:
    user = get_or_create_user(user_id)
    today = datetime.now(timezone.utc).date()
    
    # reset monthly free tokens
    days_since_reset = (today - user.tokens_reset_date).days
    if days_since_reset >= 30:
        user.tokens_used = 0
        user.tokens_available = FREE_TOKENS
        user.tokens_reset_date = today
        db.session.commit()
        used_tokens_cache[user_id] = 0
    
    # update cache
    used_tokens_cache[user_id] = user.tokens_used

    return user.tokens_used < user.tokens_available


def use_tokens(user_id: str, tokens: int) -> None:
    # update cache
    if user_id in used_tokens_cache:
        used_tokens_cache[user_id] += tokens
    else:
        used_tokens_cache[user_id] = tokens
    
    # update database
    user = get_or_create_user(user_id)
    user.tokens_used += tokens  # type: ignore
    db.session.commit()


def add_purchased_tokens(user_id: str, tokens: int) -> None:
    user = get_or_create_user(user_id)
    user.tokens_available += tokens  # type: ignore
    db.session.commit()


def get_user_usage(user_id: str) -> dict[str, str | int]:
    user = get_or_create_user(user_id)
    
    return {
        "tier": user.tier,
        "tokens_used": user.tokens_used,
        "tokens_available": user.tokens_available,
    }