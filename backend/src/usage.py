from src.models import db
from datetime import datetime, timezone
from src.config import FREE_TOKENS
from src.services import get_or_create_user


def check_token_limit(user_id: str) -> bool:
    user = get_or_create_user(user_id)
    today = datetime.now(timezone.utc).date()

    # reset monthly free tokens
    days_since_reset = (today - user.tokens_reset_date).days
    if days_since_reset >= 30:
        user.tokens_available += FREE_TOKENS  # type: ignore
        user.tokens_reset_date = today  # type: ignore
        db.session.commit()

    return user.tokens_available > 0


def use_tokens(user_id: str, tokens: int) -> None:
    user = get_or_create_user(user_id)
    user.tokens_available = max(user.tokens_available - tokens, 0)  # type: ignore
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
        "tokens_reset_date": user.tokens_reset_date.isoformat(),
    }
