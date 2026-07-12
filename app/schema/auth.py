"""
====================================================================================
  appify_social_api

  Date          : 7/11/2026 11:57 PM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime

# 1. Incoming payload for Registration
class UserRegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=50, examples=["Doe"])
    email: EmailStr = Field(..., examples=["john.doe@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["securepass123"])

# 2. Incoming payload for Login
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["john.doe@example.com"])
    password: str = Field(..., examples=["securepass123"])

# 3. Secure, sanitized user data returned to the client (excludes password hash)
class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime

    # Tells Pydantic to read database ORM objects directly
    model_config = ConfigDict(from_attributes=True)

# 4. Standard OAuth2 / JWT Response token shape
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"