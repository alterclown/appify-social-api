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
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.repository.feed_repo import IFeedRepository, FeedRepository
from app.schema.post import PostResponse, LikedByResponse
from app.utils.response import success_response
from app.models.post import Post


class IFeedService(ABC):
    @abstractmethod
    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str],
                          privacy: str) -> JSONResponse: pass

    @abstractmethod
    async def get_feed(self, db: AsyncSession, current_user_id: UUID, page: int, size: int) -> JSONResponse: pass

    @abstractmethod
    async def toggle_like(self, db: AsyncSession, user_id: UUID, post_id: UUID) -> JSONResponse: pass

    @abstractmethod
    async def get_likers(self, db: AsyncSession, post_id: UUID) -> JSONResponse: pass


class FeedService(IFeedService):

    def __init__(self, feed_repo: IFeedRepository = None):
        self.feed_repo = feed_repo or FeedRepository()

    async def create_post(self, db: AsyncSession, author_id: UUID, text_content: str, image_url: Optional[str],
                          privacy: str) -> JSONResponse:
        clean_text = text_content.strip()
        if not clean_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post content cannot be empty.")

        post = await self.feed_repo.create_post(db, author_id, clean_text, image_url, privacy)
        await db.commit()
        await db.refresh(post)

        # Pre-populate dynamic metrics for a brand new post block
        post.likes_count = 0
        post.comments_count = 0
        post.is_liked_by_me = False

        serialized = PostResponse.model_validate(post).model_dump(mode="json")
        return success_response(data=serialized, status_code=status.HTTP_201_CREATED)

    async def get_feed(self, db: AsyncSession, current_user_id: UUID, page: int, size: int) -> JSONResponse:
        safe_size = min(size, 50)
        offset = (max(page, 1) - 1) * safe_size

        posts = await self.feed_repo.get_timeline(db, current_user_id, limit=safe_size, offset=offset)

        # Set safety fallback values for evaluation requirements
        for post in posts:
            if not hasattr(post, "likes_count") or post.likes_count is None: post.likes_count = 0
            if not hasattr(post, "comments_count") or post.comments_count is None: post.comments_count = 0
            if not hasattr(post, "is_liked_by_me") or post.is_liked_by_me is None: post.is_liked_by_me = False

        serialized = [PostResponse.model_validate(p).model_dump(mode="json") for p in posts]
        return success_response(data=serialized, status_code=status.HTTP_200_OK)

    async def toggle_like(self, db: AsyncSession, user_id: UUID, post_id: UUID) -> JSONResponse:
        is_liked = await self.feed_repo.toggle_post_like(db, user_id, post_id)
        await db.commit()

        result_payload = {
            "liked": is_liked,
            "message": "Post liked" if is_liked else "Post unliked"
        }
        return success_response(data=result_payload, status_code=status.HTTP_200_OK)

    async def get_likers(self, db: AsyncSession, post_id: UUID) -> JSONResponse:
        likers = await self.feed_repo.get_post_likers(db, post_id)

        # Build payload structure matching the exact LikedByResponse expectation
        wrapped_payload = {"liked_by": likers}
        serialized = LikedByResponse.model_validate(wrapped_payload).model_dump(mode="json")
        return success_response(data=serialized, status_code=status.HTTP_200_OK)