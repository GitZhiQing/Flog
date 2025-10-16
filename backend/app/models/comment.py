from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from .enums import CommentStatusEnum

if TYPE_CHECKING:
    from .post import Post


class Comment(Base):
    """评论模型"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    author_email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author_link: Mapped[str | None] = mapped_column(String(200), nullable=True)
    post_slug: Mapped[str] = mapped_column(String(100), ForeignKey("posts.slug"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)
    status: Mapped[CommentStatusEnum] = mapped_column(
        Enum(CommentStatusEnum), default=CommentStatusEnum.SHOW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # 博文关系
    post: Mapped["Post"] = relationship(
        "Post", back_populates="comments", foreign_keys=[post_slug], lazy="joined"
    )
    # 自引用关系，用于回复功能
    parent: Mapped["Comment"] = relationship(
        "Comment", remote_side=[id], back_populates="replies", lazy="joined"
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, author_name='{self.author_name}', post_slug='{self.post_slug}')>"
