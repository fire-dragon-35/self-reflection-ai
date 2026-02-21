from flask import request
import jwt
from src.config import CLERK_DOMAIN

JWKS_URL = f"{CLERK_DOMAIN}/.well-known/jwks.json"


def get_user_id() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        jwks_client = jwt.PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # verify and decode the token
        decoded = jwt.decode(
            token, signing_key.key, algorithms=["RS256"], options={"verify_aud": False}
        )

        user_id = decoded.get("sub")
        return user_id

    except Exception:
        return None
