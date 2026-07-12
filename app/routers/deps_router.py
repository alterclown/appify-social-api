"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:23 AM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Reusable authentication dependency for protected routes.
    Delegates validation entirely to the AuthService layer.
    """
    service = AuthService()
    # The dependency now passes control straight to the service layer
    return await service.authenticate_token(db, token)