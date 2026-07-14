"""
====================================================================================
  appify_social_api

  Date          : 7/11/2026 11:55 PM
  Author        : rahir
  Description: Performance optimized comment repository supporting nested objects.
====================================================================================
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.like import CommentLike
from app.models.user import User


class ICommentRepository(ABC):
    @abstractmethod
    async def create_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str,
                             parent_comment_id: Optional[UUID]) -> Comment: pass

    @abstractmethod
    async def verify_comment_exists(self, db: AsyncSession, comment_id: UUID) -> bool: pass

    @abstractmethod
    async def get_by_id_with_relations(self, db: AsyncSession, comment_id: UUID, current_user_id: UUID) -> Optional[
        Comment]: pass

    @abstractmethod
    async def get_comments_by_post(self, db: AsyncSession, post_id: UUID, current_user_id: UUID) -> List[Comment]: pass

    @abstractmethod
    async def toggle_comment_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> bool: pass

    @abstractmethod
    async def get_comment_likers(self, db: AsyncSession, comment_id: UUID) -> List[User]: pass


class CommentRepository(ICommentRepository):

    async def create_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str,
                             parent_comment_id: Optional[UUID]) -> Comment:
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

    async def get_by_id_with_relations(self, db: AsyncSession, comment_id: UUID, current_user_id: UUID) -> Optional[Comment]:
        likes_subquery = select(CommentLike.comment_id, func.count(CommentLike.user_id).label("likes_count")).group_by(
            CommentLike.comment_id).subquery()
        user_like_subquery = select(CommentLike.comment_id, literal(True).label("is_liked")).where(
            CommentLike.user_id == current_user_id).subquery()

        stmt = (
            select(
                Comment,
                func.coalesce(likes_subquery.c.likes_count, 0).label("likes_count"),
                func.coalesce(user_like_subquery.c.is_liked, False).label("is_liked_by_me")
            )
            .outerjoin(likes_subquery, Comment.id == likes_subquery.c.comment_id)
            .outerjoin(user_like_subquery, Comment.id == user_like_subquery.c.comment_id)
            .options(selectinload(Comment.user), selectinload(Comment.replies))
            .where(Comment.id == comment_id)
        )
        result = await db.execute(stmt)
        row = result.unique().first()
        if row:
            comment = row[0]
            comment.likes_count = row.likes_count
            comment.is_liked_by_me = row.is_liked_by_me
            comment.replies = []
            return comment
        return None

    async def get_comments_by_post(self, db: AsyncSession, post_id: UUID, current_user_id: UUID) -> List[Comment]:
        likes_subquery = select(CommentLike.comment_id, func.count(CommentLike.user_id).label("likes_count")).group_by(
            CommentLike.comment_id).subquery()
        user_like_subquery = select(CommentLike.comment_id, literal(True).label("is_liked")).where(
            CommentLike.user_id == current_user_id).subquery()

        stmt = (
            select(
                Comment,
                func.coalesce(likes_subquery.c.likes_count, 0).label("likes_count"),
                func.coalesce(user_like_subquery.c.is_liked, False).label("is_liked_by_me")
            )
            .outerjoin(likes_subquery, Comment.id == likes_subquery.c.comment_id)
            .outerjoin(user_like_subquery, Comment.id == user_like_subquery.c.comment_id)
            .options(selectinload(Comment.user), selectinload(Comment.replies))
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        result = await db.execute(stmt)

        all_comments = []
        top_level_comments = []
        child_map = {}

        for row in result.unique().all():
            comment_obj = row[0]
            comment_obj.likes_count = row.likes_count
            comment_obj.is_liked_by_me = row.is_liked_by_me
            comment_obj.replies = []
            all_comments.append(comment_obj)

        for comment in all_comments:
            if comment.parent_comment_id is None:
                top_level_comments.append(comment)
            else:
                if comment.parent_comment_id not in child_map:
                    child_map[comment.parent_comment_id] = []
                child_map[comment.parent_comment_id].append(comment)

        for parent in top_level_comments:
            if parent.id in child_map:
                parent.replies = child_map[parent.id]

        return top_level_comments

    async def toggle_comment_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> bool:
        like_query = select(CommentLike).where(CommentLike.user_id == user_id, CommentLike.comment_id == comment_id)
        result = await db.execute(like_query)
        existing_like = result.scalars().first()

        if existing_like:
            await db.delete(existing_like)
            await db.flush()
            return False

        new_like = CommentLike(user_id=user_id, comment_id=comment_id)
        db.add(new_like)
        await db.flush()
        return True

    async def get_comment_likers(self, db: AsyncSession, comment_id: UUID) -> List[User]:
        query = (
            select(User)
            .join(CommentLike, CommentLike.user_id == User.id)
            .where(CommentLike.comment_id == comment_id)
            .order_by(CommentLike.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())