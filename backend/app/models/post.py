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
        String(255), nullable=False, comment="博文标题，文件 metadata 中的 title 字段"
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="博文分类，相对 POSTS_DIR 目录的子目录"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="文件路径，相对 DATA_DIR 路径"
    )
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="文件哈希，SHA1")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="访问量")
    status: Mapped[PostStatusEnum] = mapped_column(
        Enum(PostStatusEnum), default=PostStatusEnum.SHOW, comment="博文状态"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        comment="更新时间，内容变化时手动触发更新，其他操作不触发",
    )

    # 评论关系
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', category='{self.category}')>"
