"""
====================================================================================
  NexusACS - Nexus Auth Function
  Copyright (c) 2025 Nybsys Inc. All rights reserved.
 
  Date          : 7/11/2026 11:45 PM
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
        """Fetch a single user profile object by email for credential verification."""
        pass

    @abstractmethod
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Fetch a single user profile object by its unique ID identifier."""
        pass

    @abstractmethod
    async def create_user(self, db: AsyncSession, first_name: str, last_name: str, email: str, password_hash: str) -> User:
        """Persist a newly registered user instance into the database."""
        pass

class UserRepository(IUserRepository):
    """
    Handles PostgreSQL user data operations using SQLAlchemy ORM.
    Strictly stateless to safely handle millions of continuous hits.
    """

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
        # Flush executes statement to pull IDs/defaults while keeping transaction open
        await db.flush()
        return new_user