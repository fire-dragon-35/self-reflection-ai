# backend/src/rate_limit.py

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.auth import get_user_id


def get_user_or_ip() -> str:
    user_id = get_user_id()
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address()}"


limiter = Limiter(
    key_func=get_user_or_ip,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
