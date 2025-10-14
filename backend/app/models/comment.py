from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.post import Post


class Comment(Base):
    """评论模型"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    author_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="评论者名称")
    author_email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="评论者邮箱"
    )
    author_link: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="评论者链接"
    )
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id"), nullable=False, comment="博文 ID"
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("comments.id"), nullable=True, comment="父评论 ID"
    )
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否隐藏")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        comment="更新时间",
    )

    # 博文关系
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    # 自引用关系，用于回复功能
    parent: Mapped["Comment | None"] = relationship(
        "Comment", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Comment(id={self.id}, author_name='{self.author_name}', post_id='{self.post_id}')>"
        )

    @property
    def is_reply(self) -> bool:
        """检查是否为回复评论"""
        return self.parent_id is not None

    @property
    def has_replies(self) -> bool:
        """检查是否有回复"""
        return len(self.replies) > 0

    @property
    def reply_count(self) -> int:
        """获取回复数量"""
        return len(self.replies)

    def get_all_replies(self) -> list["Comment"]:
        """递归获取所有回复（包括子回复）"""
        all_replies = []
        for reply in self.replies:
            all_replies.append(reply)
            all_replies.extend(reply.get_all_replies())
        return all_replies

    def get_level(self) -> int:
        """获取评论层级（0为顶级评论）"""
        if self.parent is None:
            return 0
        return self.parent.get_level() + 1
