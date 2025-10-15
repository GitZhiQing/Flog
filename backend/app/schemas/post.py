from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    """创建文章模型"""

    slug: str
    title: str
    category: str
    file_path: str | None = None
    file_hash: str | None = None


class PostUpdate(BaseModel):
    """更新文章模型"""

    title: str | None = None
    category: str | None = None
    file_hash: str | None = None


class Post(BaseModel):
    """数据库中的文章模型"""

    model_config = ConfigDict(from_attributes=True)
    file_path: str | None = None
    file_hash: str | None = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime


class PostContent(BaseModel):
    """文章内容模型"""

    slug: str
    title: str | None = None
    category: str | None = None
    content: str
