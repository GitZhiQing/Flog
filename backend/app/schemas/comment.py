from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """评论基础模型"""

    content: str = Field(..., description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    post_id: int = Field(..., description="博文ID")
    parent_id: int | None = Field(None, description="父评论ID")
    is_hidden: bool = Field(default=False, description="是否隐藏")


class CommentCreate(BaseModel):
    """创建评论模型"""

    content: str = Field(..., description="评论内容")
    author_name: str = Field(..., description="评论者名称")
    author_email: str | None = Field(None, description="评论者邮箱")
    author_link: str | None = Field(None, description="评论者链接")
    post_id: int = Field(..., description="博文ID")
    parent_id: int | None = Field(None, description="父评论ID")


class CommentUpdate(BaseModel):
    """更新评论模型"""

    content: str | None = Field(None, description="评论内容")
    is_hidden: bool | None = Field(None, description="是否隐藏")


class CommentInDB(CommentBase):
    """数据库中的评论模型"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Comment(CommentInDB):
    """评论响应模型"""

    replies: list["Comment"] = Field(default_factory=list, description="回复列表")
    is_reply: bool = Field(default=False, description="是否为回复评论")
    reply_count: int = Field(default=0, description="回复数量")
    level: int = Field(default=0, description="评论层级")


class CommentList(BaseModel):
    """评论列表项模型"""

    id: int
    content: str
    author_name: str
    author_email: str | None
    author_link: str | None
    post_id: int
    parent_id: int | None
    created_at: datetime
    is_reply: bool = Field(default=False, description="是否为回复评论")
    reply_count: int = Field(default=0, description="回复数量")

    class Config:
        from_attributes = True


# 解决循环引用
Comment.model_rebuild()
