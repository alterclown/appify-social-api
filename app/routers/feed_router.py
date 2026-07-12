"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:03 AM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.configs.database import get_db
from app.services.feed_service import FeedService
from app.schema.post import PostCreateRequest
from app.routers.deps_router import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/posts", tags=["Feed & Posts"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_post(
    payload: PostCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FeedService()
    return await service.create_post(
        db,
        author_id=current_user.id,
        text_content=payload.text_content,
        image_url=payload.image_url,
        privacy=payload.privacy
    )

@router.get("")
async def get_main_feed(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FeedService()
    return await service.get_feed(db, current_user_id=current_user.id, page=page, size=size)

@router.post("/{post_id}/like")
async def toggle_like_on_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FeedService()
    return await service.toggle_like(db, user_id=current_user.id, post_id=post_id)

@router.get("/{post_id}/likes")
async def get_post_engagement_list(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FeedService()
    return await service.get_likers(db, post_id=post_id)