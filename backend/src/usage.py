from models import db, User
from datetime import datetime, timezone
from config import TIER_LIMITS  # type: ignore
from typing import cast

# cache
user_token_cache: dict[str, int] = {}


def check_token_limit(user_id: str) -> bool:
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user:
        return True

    today = datetime.now(timezone.utc).date()

    # reset if needed
    if user.tier == "free":
        # monthly reset for free users
        days_since_reset = (today - user.tokens_reset_date).days
        if days_since_reset >= 30:
            user.tokens_used = 0  # type: ignore
            user.tokens_reset_date = today  # type: ignore
            db.session.commit()
            user_token_cache[user_id] = 0
    else:
        # daily reset for others
        if user.tokens_reset_date < today:
            user.tokens_used = 0  # type: ignore
            user.tokens_reset_date = today  # type: ignore
            db.session.commit()
            user_token_cache[user_id] = 0

    user_token_cache[user_id] = user.tokens_used

    limit = TIER_LIMITS[user.tier]["tokens"]  # type: ignore

    return user.tokens_used < limit  # type: ignore


def add_tokens(user_id: str, tokens: int) -> None:
    if user_id in user_token_cache:
        user_token_cache[user_id] += tokens
    else:
        user_token_cache[user_id] = tokens

    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user:
        user = User(user_id=user_id, tier="free", tokens_used=tokens)  # type: ignore
        db.session.add(user)
    else:
        user.tokens_used += tokens  # type: ignore
    db.session.commit()


def get_user_usage(user_id: str) -> dict[str, str | int]:
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user:
        return {
            "tier": "free",
            "tokens_used": 0,
            "tokens_limit": TIER_LIMITS["free"]["tokens"],  # type: ignore
        }

    return {
        "tier": user.tier,
        "tokens_used": user.tokens_used,
        "tokens_limit": TIER_LIMITS[user.tier]["tokens"],  # type: ignore
    }
