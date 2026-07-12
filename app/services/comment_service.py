"""
====================================================================================
  appify_social_api

  Date          : 7/11/2026 11:58 PM
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
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.repository.comment_repo import ICommentRepository, CommentRepository
from app.schema.comment import CommentResponse
from app.schema.post import UserMinResponse
from app.utils.response import success_response


class ICommentService(ABC):
    @abstractmethod
    async def add_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str,
                          parent_comment_id: Optional[UUID]) -> JSONResponse: pass

    @abstractmethod
    async def get_comments(self, db: AsyncSession, post_id: UUID) -> JSONResponse: pass

    @abstractmethod
    async def toggle_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> JSONResponse: pass

    @abstractmethod
    async def get_likers(self, db: AsyncSession, comment_id: UUID) -> JSONResponse: pass


class CommentService(ICommentService):

    def __init__(self, comment_repo: ICommentRepository = None):
        self.comment_repo = comment_repo or CommentRepository()

    def _prepare_comment(self, comment):
        if comment is None:
            return None

        if not hasattr(comment, "likes_count") or comment.likes_count is None:
            comment.likes_count = 0
        if not hasattr(comment, "is_liked_by_me") or comment.is_liked_by_me is None:
            comment.is_liked_by_me = False

        # FIX: Check object's __dict__ to see if 'replies' is loaded.
        # This completely avoids both AttributeError and MissingGreenlet errors.
        if "replies" in comment.__dict__:
            if comment.replies:
                for reply in comment.replies:
                    self._prepare_comment(reply)
        else:
            comment.replies = []

        return comment

    async def add_comment(self, db: AsyncSession, author_id: UUID, post_id: UUID, text_content: str,
                          parent_comment_id: Optional[UUID]) -> JSONResponse:
        clean_text = text_content.strip()
        if not clean_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content cannot be empty.")

        if parent_comment_id:
            parent_exists = await self.comment_repo.verify_comment_exists(db, parent_comment_id)
            if not parent_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found.")

        try:
            inserted_comment = await self.comment_repo.create_comment(db, author_id, post_id, clean_text,
                                                                      parent_comment_id)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target post or user context does not exist in the system."
            )

        # Pull the fully hydrated comment object back out (eagerly loading relations)
        comment = await self.comment_repo.get_by_id_with_author(db, inserted_comment.id)
        self._prepare_comment(comment)

        serialized = CommentResponse.model_validate(comment).model_dump(mode="json")
        return success_response(data=serialized, status_code=status.HTTP_201_CREATED)

    async def get_comments(self, db: AsyncSession, post_id: UUID) -> JSONResponse:
        comments = await self.comment_repo.get_comments_by_post(db, post_id)

        for comment in comments:
            self._prepare_comment(comment)

        serialized = [CommentResponse.model_validate(c).model_dump(mode="json") for c in comments]
        return success_response(data=serialized, status_code=status.HTTP_200_OK)

    async def toggle_like(self, db: AsyncSession, user_id: UUID, comment_id: UUID) -> JSONResponse:
        comment_exists = await self.comment_repo.verify_comment_exists(db, comment_id)
        if not comment_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

        is_liked = await self.comment_repo.toggle_comment_like(db, user_id, comment_id)
        await db.commit()

        result_payload = {"liked": is_liked, "message": "Comment liked" if is_liked else "Comment unliked"}
        return success_response(data=result_payload, status_code=status.HTTP_200_OK)

    async def get_likers(self, db: AsyncSession, comment_id: UUID) -> JSONResponse:
        comment_exists = await self.comment_repo.verify_comment_exists(db, comment_id)
        if not comment_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

        likers = await self.comment_repo.get_comment_likers(db, comment_id)
        serialized_likers = [UserMinResponse.model_validate(u).model_dump(mode="json") for u in likers]

        return success_response(data={"liked_by": serialized_likers}, status_code=status.HTTP_200_OK)