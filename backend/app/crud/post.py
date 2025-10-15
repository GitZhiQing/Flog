from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    """文章CRUD操作类"""

    async def get_categories(self, session):
        """获取所有分类"""
        categories = await session.execute(select(Post.category))
        return categories.scalars().all()

    async def get_by_category(self, session, *, category_name: str):
        """根据分类名称获取文章列表"""
        filters = [Post.category == category_name]
        return await self.get_multi_by_filters(session, filters=filters)


# 创建文章CRUD实例
crud_post = CRUDPost(Post)
