from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CommentStatusEnum


class CommentCreate(BaseModel):
    """评论创建模型"""

    content: str = Field(..., description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    post_slug: str = Field(..., description="博文 slug")
    parent_id: int | None = Field(None, description="父评论 ID")


class CommentUpdate(BaseModel):
    """评论更新模型"""

    status: CommentStatusEnum | None = Field(None, description="评论状态")


class Comment(BaseModel):
    """评论响应模型"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str | None = Field(None, description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    parent_id: int | None = Field(None, description="父评论 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
