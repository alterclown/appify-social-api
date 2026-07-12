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


from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schema.post import UserMinResponse

# 1. Incoming payload for a comment or a reply
class CommentCreateRequest(BaseModel):
    text_content: str = Field(..., min_length=1, examples=["Great post! Highly agree."])
    # If provided, this marks the entry as a reply to a previous comment
    parent_comment_id: Optional[UUID] = None

# 2. Output structure for comments/replies
class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user: UserMinResponse
    parent_comment_id: Optional[UUID]
    text_content: str
    created_at: datetime
    likes_count: int = 0
    is_liked_by_me: bool = False
    replies: List["CommentResponse"] = []  # Self-referential list for deep threads

    model_config = ConfigDict(from_attributes=True)

# Required by Pydantic v2 to securely compile recursive models
CommentResponse.model_rebuild()