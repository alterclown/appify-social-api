"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:04 AM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""

"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 12:04 AM
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
from app.services.comment_service import CommentService, ICommentService
from app.schema.comment import CommentCreateRequest
from app.routers.deps_router import get_current_user
from app.models.user import User

router = APIRouter(tags=["Comments & Replies"])

# Factory function to safely provide the service without FastAPI parsing its __init__
def get_comment_service() -> ICommentService:
    return CommentService()

@router.post("/api/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment_to_post(
    post_id: UUID,
    payload: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    return await service.add_comment(
        db=db,
        author_id=current_user.id,
        post_id=post_id,
        text_content=payload.text_content,
        parent_comment_id=payload.parent_comment_id
    )

@router.get("/api/posts/{post_id}/comments", status_code=status.HTTP_200_OK)
async def get_comments_for_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    # Fixed: Added the missing current_user_id argument required by CommentService.get_comments()
    return await service.get_comments(db=db, post_id=post_id, current_user_id=current_user.id)

@router.post("/api/comments/{comment_id}/like", status_code=status.HTTP_200_OK)
async def toggle_like_on_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    return await service.toggle_like(db=db, user_id=current_user.id, comment_id=comment_id)

@router.get("/api/comments/{comment_id}/likes", status_code=status.HTTP_200_OK)
async def get_comment_engagement_list(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    return await service.get_likers(db=db, comment_id=comment_id)