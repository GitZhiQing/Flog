from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CommentStatusEnum


class CommentCreate(BaseModel):
    """创建评论模型"""

    content: str = Field(..., description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    post_id: int = Field(..., description="博文 ID")
    parent_id: int | None = Field(None, description="父评论ID")


class CommentUpdate(BaseModel):
    """更新评论模型"""

    content: str | None = Field(None, description="评论内容")
    status: CommentStatusEnum | None = Field(None, description="评论内容")


class Comment(BaseModel):
    """评论响应模型"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str | None = Field(None, description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    is_reply: bool = Field(default=False, description="是否为回复评论")
    created_at: datetime
    updated_at: datetime
