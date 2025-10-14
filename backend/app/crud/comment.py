from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    """评论CRUD操作类"""

    async def get_by_post_id(
        self, session: AsyncSession, *, post_id: int, skip: int = 0, limit: int = 100
    ) -> list[Comment]:
        """根据博文ID获取评论列表"""
        stmt = (
            select(Comment)
            .where(and_(Comment.post_id == post_id, not Comment.is_hidden))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_top_level_comments(
        self, session: AsyncSession, *, post_id: int, skip: int = 0, limit: int = 100
    ) -> list[Comment]:
        """获取顶级评论（非回复）"""
        stmt = (
            select(Comment)
            .where(
                and_(Comment.post_id == post_id, Comment.parent_id.is_(None), not Comment.is_hidden)
            )
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_replies(self, session: AsyncSession, *, parent_id: int) -> list[Comment]:
        """获取评论回复"""
        stmt = (
            select(Comment)
            .where(and_(Comment.parent_id == parent_id, not Comment.is_hidden))
            .order_by(desc(Comment.created_at))
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_by_post_id(self, session: AsyncSession, *, post_id: int) -> int:
        """统计博文评论数量"""
        filters = [and_(Comment.post_id == post_id, not Comment.is_hidden)]
        return await self.count(session, filters=filters)

    async def get_all(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        is_hidden: bool | None = None,
    ) -> list[Comment]:
        """获取所有评论列表，支持隐藏状态过滤"""
        stmt = select(Comment)

        if is_hidden is not None:
            stmt = stmt.where(Comment.is_hidden == is_hidden)

        stmt = stmt.order_by(desc(Comment.created_at)).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_all_visible(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Comment]:
        """获取所有可见评论"""
        stmt = (
            select(Comment)
            .where(not Comment.is_hidden)
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create_comment(
        self,
        session: AsyncSession,
        *,
        content: str,
        author_name: str,
        author_email: str | None = None,
        author_link: str | None = None,
        post_id: int,
        parent_id: int | None = None,
    ) -> Comment:
        """创建评论"""
        comment_data = {
            "content": content,
            "author_name": author_name,
            "author_email": author_email,
            "author_link": author_link,
            "post_id": post_id,
            "parent_id": parent_id,
            "is_hidden": False,
        }
        db_obj = Comment(**comment_data)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def hide_comment(self, session: AsyncSession, *, id: int) -> Comment:
        """隐藏评论"""
        comment = await self.get_or_404(session, id=id)
        comment.is_hidden = True
        session.add(comment)
        await session.flush()
        return comment

    async def show_comment(self, session: AsyncSession, *, id: int) -> Comment:
        """显示评论"""
        comment = await self.get_or_404(session, id=id)
        comment.is_hidden = False
        session.add(comment)
        await session.flush()
        return comment


# 创建评论CRUD实例
crud_comment = CRUDComment(Comment)
