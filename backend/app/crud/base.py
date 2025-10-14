from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression

from app.core.exceptions import InternalServerException, NotFoundException
from app.core.database import Base
from sqlalchemy.orm import Load


class CRUDBase[
    ModelType: Base,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """
    CRUD 对象的基类，提供基本的数据库操作方法

    泛型参数:
        ModelType: SQLAlchemy 模型类，继承自 Base
        CreateSchemaType: Pydantic 创建模型类
        UpdateSchemaType: Pydantic 更新模型类
    """

    def __init__(self, model: type[ModelType]):
        """
        初始化 CRUD 对象

        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model

    async def get(self, session: AsyncSession, *, id: Any) -> ModelType | None:
        """
        根据 ID 获取单个对象，包含预加载逻辑

        Args:
            session: 数据库会话
            id: 对象 ID

        Returns:
            ModelType | None: 模型实例或 None
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filters(
        self, session: AsyncSession, *, filters: list[BinaryExpression]
    ) -> ModelType | None:
        """
        根据过滤条件获取单个对象

        Args:
            session: 数据库会话
            filters: 过滤条件列表

        Returns:
            ModelType | None: 模型实例或 None

        Example:
            # 获取 id 为 1 的用户
            user = await self.get_by_filters(session, [User.id == 1])

            # 获取 name 为 "张三" 的用户
            user = await self.get_by_filters(session, [User.name == "张三"])

            # 获取 name 为 "张三" 且 age 为 25 的用户
            user = await self.get_by_filters(session, [User.name == "张三", User.age == 25])
        """
        query = select(self.model)
        if filters:
            query = query.where(and_(*filters))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_404(self, session: AsyncSession, *, id: Any) -> ModelType:
        """
        根据 ID 获取单个对象，如果不存在则抛出 404 异常

        Args:
            session: 数据库会话
            id: 对象 ID

        Returns:
            ModelType: 模型实例

        Raises:
            NotFoundException: 当对象不存在时抛出
        """
        result = await self.get(session, id=id)
        if result is None:
            raise NotFoundException(msg=f"{self.model.__name__} with id {id} not found")
        return result

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        options: list[Load] | None = None,
    ) -> list[ModelType]:
        """
        获取多个对象列表，支持分页和查询选项

        Args:
            session: 数据库会话
            skip: 跳过的记录数（偏移量）
            limit: 返回的最大记录数
            options: 查询选项列表（如 joinedload 或 selectinload）

        Returns:
            list[ModelType]: 模型实例列表
        """
        stmt = select(self.model).offset(skip).limit(limit)
        if options:
            for option in options:
                stmt = stmt.options(option)  # 应用查询选项
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_multi_by_filters(
        self,
        session: AsyncSession,
        *,
        filters: list[BinaryExpression],
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """
        根据过滤条件获取多个对象列表，支持分页

        Args:
            session: 数据库会话
            filters: 过滤条件列表
            skip: 跳过的记录数（偏移量）
            limit: 返回的最大记录数

        Returns:
            list[ModelType]: 模型实例列表

        Example:
            # 获取 name 为 "张三" 的用户列表
            users = await self.get_multi_by_filters(session, [User.name == "张三"])

            # 获取 name 为 "张三" 且 age 为 25 的用户列表
            users = await self.get_multi_by_filters(session, [User.name == "张三", User.age == 25])
        """
        query = select(self.model)
        if filters:
            query = query.where(and_(*filters))
        stmt = query.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        """
        创建新对象

        Args:
            session: 数据库会话
            obj_in: 创建数据模型

        Returns:
            ModelType: 新创建的模型实例
        """
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update(
        self, session: AsyncSession, *, id: Any, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        更新对象

        Args:
            session: 数据库会话
            id: 对象 ID
            obj_in: 更新数据模型

        Returns:
            ModelType: 更新后的模型实例
        """
        db_obj = await self.get_or_404(session, id=id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():  # ORM 风格更新
            setattr(db_obj, key, value)
        session.add(db_obj)  # 将对象标记为脏数据
        await session.flush()
        return db_obj

    async def delete(self, session: AsyncSession, *, id: int):
        """
        删除对象

        Args:
            session: 数据库会话
            id: 对象 ID

        Raises:
            NotFoundException: 当对象不存在时抛出
            InternalServerException: 当删除操作失败时抛出
        """
        db_obj = await self.get(session, id)
        if not db_obj:
            raise NotFoundException(msg=f"{self.model.__name__} with id {id} not found")
        try:
            stmt = delete(self.model).where(self.model.id == id)
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to delete {self.model.__name__}: {e}")
            raise InternalServerException(msg="Internal server error") from e

    async def count(
        self, session: AsyncSession, *, filters: list[BinaryExpression] = None
    ) -> int:
        """
        统计对象数量，支持过滤条件

        Args:
            session: 数据库会话
            filters: 过滤条件列表

        Returns:
            int: 符合条件的对象数量
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            query = query.where(and_(*filters))
        result = await session.execute(query)
        return result.scalar_one()

    async def get_with_options(
        self, session: AsyncSession, *, id: Any, options: list[Load] | None = None
    ) -> ModelType | None:
        """
        根据 ID 获取单个对象，并支持查询选项

        Args:
            session: 数据库会话
            id: 对象 ID
            options: 查询选项列表（如 joinedload 或 selectinload）

        Returns:
            ModelType | None: 模型实例或 None
        """
        stmt = select(self.model).where(self.model.id == id)
        if options:
            for option in options:
                stmt = stmt.options(option)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
