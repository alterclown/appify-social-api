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
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment

class ICommentRepository(ABC):
    @abstractmethod
    async def create_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str, parent_comment_id: Optional[UUID]) -> Comment: pass
    @abstractmethod
    async def verify_comment_exists(self, db: AsyncSession, comment_id: UUID) -> bool: pass
    @abstractmethod
    async def get_by_id_with_author(self, db: AsyncSession, comment_id: UUID) -> Optional[Comment]: pass
    @abstractmethod
    async def get_comments_by_post(self, db: AsyncSession, post_id: UUID) -> List[Comment]: pass
    @abstractmethod
    async def toggle_comment_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> bool: pass
    @abstractmethod
    async def get_comment_likers(self, db: AsyncSession, comment_id: UUID) -> List: pass


class CommentRepository(ICommentRepository):

    async def create_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str, parent_comment_id: Optional[UUID]) -> Comment:
        new_comment = Comment(
            user_id=author_id,
            post_id=post_id,
            text_content=text_content,
            parent_comment_id=parent_comment_id
        )
        db.add(new_comment)
        await db.flush()
        return new_comment

    async def verify_comment_exists(self, db: AsyncSession, comment_id: UUID) -> bool:
        stmt = select(func.count()).select_from(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        return result.scalar() > 0

    async def get_by_id_with_author(self, db: AsyncSession, comment_id: UUID) -> Optional[Comment]:
        # FIX: Eagerly load replies and their corresponding users to avoid Greenlet lazy-load crashes
        stmt = (
            select(Comment)
            .options(
                selectinload(Comment.user),
                selectinload(Comment.replies).selectinload(Comment.user)
            )
            .where(Comment.id == comment_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_comments_by_post(self, db: AsyncSession, post_id: UUID) -> List[Comment]:
        stmt = (
            select(Comment)
            .options(
                selectinload(Comment.user),
                selectinload(Comment.replies).selectinload(Comment.user)
            )
            .where(Comment.post_id == post_id, Comment.parent_comment_id == None)
            .order_by(Comment.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def toggle_comment_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> bool:
        return True

    async def get_comment_likers(self, db: AsyncSession, comment_id: UUID) -> List:
        return []