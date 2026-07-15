"""
====================================================================================
  appify_social_api

  Date          : 7/11/2026 11:55 PM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""


from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def create_user(self, db: AsyncSession, first_name: str, last_name: str, email: str, password_hash: str) -> User:
        pass

class UserRepository(IUserRepository):

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, first_name: str, last_name: str, email: str, password_hash: str) -> User:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash
        )

        db.add(new_user)
        await db.flush()
        return new_user