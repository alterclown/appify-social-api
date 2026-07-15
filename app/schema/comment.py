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

from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schema.post import UserMinResponse


class CommentCreateRequest(BaseModel):
    text_content: str = Field(..., min_length=1, examples=["Great post! Highly agree."])
    parent_comment_id: Optional[UUID] = None

class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user: UserMinResponse
    parent_comment_id: Optional[UUID]
    text_content: str
    created_at: datetime
    likes_count: int = 0
    is_liked_by_me: bool = False
    replies: List["CommentResponse"] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("user", mode="before")
    @classmethod
    def ensure_user_profile_image(cls, v: any) -> any:
        """Enforces a default fallback profile avatar on the raw input before parsing schema structures."""
        if v is not None:
            if hasattr(v, "profile_image_url"):
                if not getattr(v, "profile_image_url", None):
                    v.profile_image_url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            elif isinstance(v, dict):
                if not v.get("profile_image_url"):
                    v["profile_image_url"] = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
        return v

CommentResponse.model_rebuild()