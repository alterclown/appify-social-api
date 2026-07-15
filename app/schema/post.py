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
from typing import Optional, Literal, List


class UserMinResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class PostCreateRequest(BaseModel):
    text_content: str = Field(..., min_length=1, examples=["Hello World! This is my first post."])
    image_url: Optional[str] = Field(None, examples=["https://cloudstorage.com/bucket/img.jpg"])
    privacy: Literal["public", "private"] = "public"


class PostResponse(BaseModel):
    id: UUID
    author: UserMinResponse
    text_content: str
    image_url: Optional[str]
    privacy: Literal["public", "private"]
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    is_liked_by_me: bool = False

    model_config = ConfigDict(from_attributes=True)


class LikedByResponse(BaseModel):
    liked_by: List[UserMinResponse]