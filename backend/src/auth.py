from flask import request
from config import CLERK_SECRET_KEY
from clerk_backend_api import Clerk

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)


def get_user_id() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        # Verify session token
        session = clerk.sessions.verify_token(token)  # type: ignore
        return session.user_id  # type: ignore
    except Exception as e:
        print(f"Auth error: {e}")
        return None
