"""
====================================================================================
  NexusACS - Nexus Auth Function
  Copyright (c) 2025 Nybsys Inc. All rights reserved.
 
  Date          : 7/11/2026 11:50 PM
  Author        : rahir
  Description:
    ----------
====================================================================================
Last Update    :  
Last Modifier  : 
"""


from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.models.post import Post, PrivacyType
from app.models.like import PostLike
from app.models.user import User

class IFeedRepository(ABC):
    @abstractmethod
    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str], privacy: str) -> Post: pass

    @abstractmethod
    async def get_timeline(self, db: AsyncSession, current_user_id: UUID, limit: int, offset: int) -> List[Post]: pass

    @abstractmethod
    async def toggle_post_like(self, db: AsyncSession, user_id: UUID, post_id: UUID) -> bool: pass

    @abstractmethod
    async def get_post_likers(self, db: AsyncSession, post_id: UUID) -> List[User]: pass

class FeedRepository(IFeedRepository):

    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str], privacy: str) -> Post:
        new_post = Post(
            author_id=author_id,
            text_content=text_content,
            image_url=image_url,
            privacy=PrivacyType[privacy]
        )
        db.add(new_post)
        await db.flush()
        return new_post

    async def get_timeline(self, db: AsyncSession, current_user_id: UUID, limit: int, offset: int) -> List[Post]:
        query = (
            select(Post)
            .where(
                or_(
                    Post.privacy == PrivacyType.public,
                    and_(Post.privacy == PrivacyType.private, Post.author_id == current_user_id)
                )
            )
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(Post.author))
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def toggle_post_like(self, db: AsyncSession, user_id: UUID, post_id: UUID) -> bool:
        like_query = select(PostLike).where(PostLike.user_id == user_id, PostLike.post_id == post_id)
        result = await db.execute(like_query)
        existing_like = result.scalars().first()

        if existing_like:
            await db.delete(existing_like)
            await db.flush()
            return False

        new_like = PostLike(user_id=user_id, post_id=post_id)
        db.add(new_like)
        await db.flush()
        return True

    async def get_post_likers(self, db: AsyncSession, post_id: UUID) -> List[User]:
        query = (
            select(User)
            .join(PostLike, PostLike.user_id == User.id)
            .where(PostLike.post_id == post_id)
            .order_by(PostLike.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())