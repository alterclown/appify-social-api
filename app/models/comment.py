"""
====================================================================================
  NexusACS - Nexus Auth Function
  Copyright (c) 2025 Nybsys Inc. All rights reserved.
 
  Date          : 7/11/2026 1:00 AM
  Author        : rahir
  Description:
    ----------
====================================================================================
Last Update    :  
Last Modifier  : 
"""
import uuid
from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"),
                                                                nullable=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    post: Mapped["Post"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")
    likes: Mapped[list["CommentLike"]] = relationship(back_populates="comment", cascade="all, delete-orphan")

    # Self-Referencing relationship mechanics for nested replies
    parent: Mapped["Comment | None"] = relationship("Comment", back_populates="replies", remote_side=[id])
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")


# Indexes optimized to construct thread views efficiently
Index("idx_comments_post_id", Comment.post_id)
Index("idx_comments_parent_id", Comment.parent_comment_id)