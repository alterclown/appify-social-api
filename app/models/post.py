"""
====================================================================================
  NexusACS - Nexus Auth Function
  Copyright (c) 2025 Nybsys Inc. All rights reserved.
 
  Date          : 7/11/2026 1:01 AM
  Author        : rahir
  Description:
    ----------
====================================================================================
Last Update    :  
Last Modifier  : 
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class PrivacyType(str, enum.Enum):
    public = "public"
    private = "private"
    friends = "friends"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    privacy: Mapped[PrivacyType] = mapped_column(
        Enum(PrivacyType, native_enum=False),
        default=PrivacyType.public,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["PostLike"]] = relationship(back_populates="post", cascade="all, delete-orphan")

# Indexes optimized for timeline sorting and user portfolio retrieval
Index("idx_posts_created_at_desc", Post.created_at.desc())
Index("idx_posts_author_id", Post.author_id)