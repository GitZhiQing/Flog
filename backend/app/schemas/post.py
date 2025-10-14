from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    """文章基础模型"""

    title: str
    category: str
    slug: str
    is_hidden: bool = False


class PostCreate(PostBase):
    """创建文章模型"""

    file_path: str | None = None
    file_hash: str | None = None


class PostUpdate(BaseModel):
    """更新文章模型"""

    title: str | None = None
    content: str | None = None
    category: str | None = None
    slug: str | None = None
    is_hidden: bool | None = None
    file_path: str | None = None
    file_hash: str | None = None


class PostInDB(PostBase):
    """数据库中的文章模型"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str | None = None
    file_hash: str | None = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime


class Post(PostInDB):
    """文章响应模型"""

    pass


class PostCategory(BaseModel):
    """文章分类响应模型"""

    category: str
    count: int


class PostFile(BaseModel):
    """文章文件响应模型"""

    file_path: str
    title: str
    category: str
    content: str
    is_hidden: bool = False
