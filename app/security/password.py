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

import bcrypt


def hash_password(password: str) -> str:
    """
    Generates a secure, salted bcrypt hash from a plain text password string.
    Uses the native bcrypt engine directly to bypass unmaintained passlib wrappers.
    """
    # 1. Bcrypt expects raw bytes, so we encode the UTF-8 string
    password_bytes = password.encode('utf-8')

    # 2. Generate a fresh, random salt and hash the password
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # 3. Decode back to a standard string so it stores cleanly in your Postgres text column
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain text password string against a stored database hash string.
    """
    # Convert both strings back to bytes for verification
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)