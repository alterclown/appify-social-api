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

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from uuid import UUID

from app.repository.user_repo import IUserRepository, UserRepository
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token, decode_access_token
from app.models.user import User
from app.schema.auth import UserResponse, TokenResponse
from app.utils.response import success_response


# ==============================================================================
# 🔑 INTERFACE
# ==============================================================================
class IAuthService(ABC):
    @abstractmethod
    async def register(self, db: AsyncSession, first_name: str, last_name: str, email: str, password: str) -> JSONResponse:
        """Register user, commit to database, serialize, and return standardized JSONResponse."""
        pass

    @abstractmethod
    async def login(self, db: AsyncSession, email: str, password: str) -> JSONResponse:
        """Authenticate credentials, issue JWT, and return standardized JSONResponse."""
        pass

    @abstractmethod
    def get_me_profile(self, current_user: User) -> JSONResponse:
        """Serialize active profile and return standardized JSONResponse."""
        pass

    @abstractmethod
    async def authenticate_token(self, db: AsyncSession, token: str) -> User:
        """Decode a JWT token and verify the corresponding user exists in the database."""
        pass


# ==============================================================================
# 🚀 IMPLEMENTATION
# ==============================================================================
class AuthService(IAuthService):

    def __init__(self, user_repo: IUserRepository = None):
        # Now every method safely pulls from this single encapsulated instance
        self.user_repo = user_repo or UserRepository()

    async def register(self, db: AsyncSession, first_name: str, last_name: str, email: str, password: str) -> JSONResponse:
        # Changed from user_repo to self.user_repo
        existing_user = await self.user_repo.get_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists."
            )

        hashed_pwd = hash_password(password)
        # Changed from user_repo to self.user_repo
        new_user = await self.user_repo.create_user(db, first_name, last_name, email, hashed_pwd)

        await db.commit()
        await db.refresh(new_user)

        serialized_user = UserResponse.model_validate(new_user).model_dump(mode="json")
        return success_response(data=serialized_user, status_code=status.HTTP_201_CREATED)

    async def login(self, db: AsyncSession, email: str, password: str) -> JSONResponse:
        # Changed from user_repo to self.user_repo
        user = await self.user_repo.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )

        token = create_access_token(user_id=str(user.id))

        token_data = TokenResponse(access_token=token, token_type="bearer").model_dump(mode="json")
        return success_response(data=token_data, status_code=status.HTTP_200_OK)

    def get_me_profile(self, current_user: User) -> JSONResponse:
        serialized_user = UserResponse.model_validate(current_user).model_dump(mode="json")
        return success_response(data=serialized_user, status_code=status.HTTP_200_OK)

    async def authenticate_token(self, db: AsyncSession, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user_id_str = decode_access_token(token)
        if not user_id_str:
            raise credentials_exception

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception

        user = await self.user_repo.get_by_id(db, user_id)
        if user is None:
            raise credentials_exception

        return user