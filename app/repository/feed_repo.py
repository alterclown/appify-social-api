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
from sqlalchemy import select, or_, and_, func, literal
from sqlalchemy.orm import selectinload

from app.models.post import Post, PrivacyType
from app.models.like import PostLike
from app.models.comment import Comment
from app.models.user import User


class IFeedRepository(ABC):
    @abstractmethod
    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str],
                          privacy: str) -> Post: pass

    @abstractmethod
    async def get_timeline(self, db: AsyncSession, current_user_id: UUID, limit: int, offset: int) -> List[Post]: pass

    @abstractmethod
    async def toggle_post_like(self, db: AsyncSession, user_id: UUID, post_id: UUID) -> bool: pass

    @abstractmethod
    async def get_post_likers(self, db: AsyncSession, post_id: UUID) -> List[User]: pass


class FeedRepository(IFeedRepository):

    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str],
                          privacy: str) -> Post:
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
        # 1. Total likes count subquery per post
        likes_subquery = (
            select(PostLike.post_id, func.count(PostLike.user_id).label("likes_count"))
            .group_by(PostLike.post_id)
            .subquery()
        )

        # 2. Total root comments count subquery per post
        comments_subquery = (
            select(Comment.post_id, func.count(Comment.id).label("comments_count"))
            .group_by(Comment.post_id)
            .subquery()
        )

        # 3. Dynamic evaluation checking if the logged-in user liked the post
        user_like_subquery = (
            select(PostLike.post_id, literal(True).label("is_liked"))
            .where(PostLike.user_id == current_user_id)
            .subquery()
        )

        # Main query binding the aggregations via outer joins
        query = (
            select(
                Post,
                func.coalesce(likes_subquery.c.likes_count, 0).label("likes_count"),
                func.coalesce(comments_subquery.c.comments_count, 0).label("comments_count"),
                func.coalesce(user_like_subquery.c.is_liked, False).label("is_liked_by_me")
            )
            .outerjoin(likes_subquery, Post.id == likes_subquery.c.post_id)
            .outerjoin(comments_subquery, Post.id == comments_subquery.c.post_id)
            .outerjoin(user_like_subquery, Post.id == user_like_subquery.c.post_id)
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

        posts = []
        for row in result.unique().all():
            post_obj = row[0]
            # Bind aggregated properties directly onto the ORM model instances dynamically
            post_obj.likes_count = row.likes_count
            post_obj.comments_count = row.comments_count
            post_obj.is_liked_by_me = row.is_liked_by_me
            posts.append(post_obj)

        return posts

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