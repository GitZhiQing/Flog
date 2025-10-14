from sqlalchemy import and_, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    """文章CRUD操作类"""

    async def get_by_file_path(self, session: AsyncSession, *, file_path: str) -> Post | None:
        """根据文件路径获取文章"""
        stmt = select(Post).where(Post.file_path == file_path)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_file_hash(self, session: AsyncSession, *, file_hash: str) -> Post | None:
        """根据文件哈希获取文章"""
        stmt = select(Post).where(Post.file_hash == file_hash)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_category(
        self, session: AsyncSession, *, category: str, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """根据分类获取文章列表"""
        stmt = (
            select(Post)
            .where(Post.category == category)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        search: str | None = None,
        is_hidden: bool | None = None,
    ) -> list[Post]:
        """获取所有文章列表，支持分类、搜索和隐藏状态过滤"""
        filters = []

        if category:
            filters.append(Post.category == category)

        if search:
            filters.append(or_(Post.title.contains(search), Post.content.contains(search)))

        if is_hidden is not None:
            filters.append(Post.is_hidden == is_hidden)

        stmt = select(Post)
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.order_by(desc(Post.created_at)).offset(skip).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_all(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        search: str | None = None,
        is_hidden: bool | None = None,
    ) -> int:
        """统计所有文章数量，支持分类、搜索和隐藏状态过滤"""
        filters = []

        if category:
            filters.append(Post.category == category)

        if search:
            filters.append(or_(Post.title.contains(search), Post.content.contains(search)))

        if is_hidden is not None:
            filters.append(Post.is_hidden == is_hidden)

        return await self.count(session, filters=filters)

    async def get_visible_posts(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        search: str | None = None,
    ) -> list[Post]:
        """获取可见文章列表，支持分类和搜索过滤"""
        filters = [not Post.is_hidden]

        if category:
            filters.append(Post.category == category)

        if search:
            filters.append(or_(Post.title.contains(search), Post.content.contains(search)))

        stmt = (
            select(Post)
            .where(and_(*filters))
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_visible_posts(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        search: str | None = None,
    ) -> int:
        """统计可见文章数量，支持分类和搜索过滤"""
        filters = [not Post.is_hidden]

        if category:
            filters.append(Post.category == category)

        if search:
            filters.append(or_(Post.title.contains(search), Post.content.contains(search)))

        return await self.count(session, filters=filters)

    async def increment_view_count(self, session: AsyncSession, *, id: int) -> Post:
        """增加文章访问量"""
        post = await self.get_or_404(session, id=id)
        post.view_count += 1
        session.add(post)
        await session.flush()
        return post

    async def get_categories(self, session: AsyncSession) -> list[str]:
        """获取所有文章分类"""
        stmt = select(Post.category).distinct()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create_from_file(
        self,
        session: AsyncSession,
        *,
        file_path: str,
        title: str,
        slug: str,
        category: str,
        content: str,
        file_hash: str,
    ) -> Post:
        """根据文件信息创建文章"""
        post_data = {
            "title": title,
            "slug": slug,
            "category": category,
            "content": content,
            "file_path": file_path,
            "file_hash": file_hash,
            "view_count": 0,
            "is_hidden": False,
        }
        db_obj = Post(**post_data)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update_from_file(
        self,
        session: AsyncSession,
        *,
        file_path: str,
        title: str,
        slug: str,
        content: str,
        file_hash: str,
    ) -> Post:
        """根据文件信息更新文章"""
        post = await self.get_by_file_path(session, file_path=file_path)
        if not post:
            raise ValueError(f"Post with file path {file_path} not found")

        post.title = title
        post.slug = slug
        post.content = content
        post.file_hash = file_hash
        session.add(post)
        await session.flush()
        return post

    async def sync_from_file_system(self, session: AsyncSession) -> list[Post]:
        """从文件系统同步文章到数据库"""
        from app.core.file_system import scan_posts_dir

        # 扫描文件系统中的所有文章
        file_posts = scan_posts_dir()
        synced_posts = []

        for file_post in file_posts:
            # 检查数据库中是否已存在相同文件路径的文章
            db_post = await self.get_by_file_path(session, file_path=file_post["file_path"])

            # 如果文章不存在，或者文件哈希值不同（文件已修改），则更新数据库
            if not db_post or db_post.file_hash != file_post["file_hash"]:
                post_data = {
                    "title": file_post["title"],
                    "slug": file_post["slug"],
                    "content": file_post["content"],
                    "file_path": file_post["file_path"],
                    "file_hash": file_post["file_hash"],
                    "category": file_post["category"],
                    "is_hidden": file_post["is_hidden"],
                }

                if db_post:
                    # 更新现有文章
                    update_data = PostUpdate(**post_data)
                    await self.update(session, id=db_post.id, obj_in=update_data)
                    synced_posts.append(db_post)
                else:
                    # 创建新文章
                    new_post = await self.create(session, obj_in=PostCreate(**post_data))
                    synced_posts.append(new_post)

        return synced_posts


# 创建文章CRUD实例
crud_post = CRUDPost(Post)
