"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:02 AM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.services.auth_service import AuthService
# Updated imports to match your schema file exactly
from app.schema.auth import UserRegisterRequest, UserLoginRequest
from app.routers.deps_router import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService()
    return await service.register(
        db=db,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=payload.password
    )


@router.post("/login")
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService()
    return await service.login(
        db=db,
        email=payload.email,
        password=payload.password
    )


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    service = AuthService()
    return service.get_me_profile(current_user)