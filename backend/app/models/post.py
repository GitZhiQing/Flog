from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from .enums import PostStatusEnum

if TYPE_CHECKING:
    from app.models.comment import Comment


class Post(Base):
    """博文模型"""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="博文 slug，唯一键，由文件名得到，可用于生成 URL",
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="博文标题，文件 matadata"
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="博文分类，相对 POSTS_DIR 目录"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="文件路径，相对 DATA_DIR 路径"
    )
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="文件哈希，SHA1")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="访问量")
    status: Mapped[PostStatusEnum] = mapped_column(
        Enum(PostStatusEnum), default=PostStatusEnum.SHOW, comment="博文状态"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        comment="更新时间，内容变化时手动触发更新",
    )

    # 评论关系
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', category='{self.category}')>"

    @property
    def comment_count(self) -> int:
        """获取评论总数"""
        return len(self.comments)

    @property
    def visible_comment_count(self) -> int:
        """获取可见评论数量"""
        return len([c for c in self.comments if not c.is_hidden])

    def get_all_comments(self) -> list["Comment"]:
        """获取所有评论（包括回复）"""
        all_comments = []
        for comment in self.comments:
            all_comments.append(comment)
            all_comments.extend(comment.get_all_replies())
        return all_comments
