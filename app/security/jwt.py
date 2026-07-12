"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:26 AM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
# Importing decouple configuration manager
from decouple import config

# Safely manage environment configurations with clean default typing
SECRET_KEY = config("JWT_SECRET", default="super-secret-fallback-key-change-this-in-production")
ALGORITHM = config("JWT_ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES", default=60, cast=int)


def create_access_token(user_id: str) -> str:
    """
    Creates a signed JSON Web Token (JWT) containing the user's ID string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodes and validates a JWT. Returns the user ID string if valid, None if expired/corrupted.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        return None