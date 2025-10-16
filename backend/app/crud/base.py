from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from sqlalchemy.sql.elements import BinaryExpression

from app.core.database import Base
from app.core.exceptions import InternalServerException, NotFoundException


class CRUDBase[
    ModelType: Base,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """
    CRUD 对象的基类，提供基本的数据库操作方法

    ## 泛型参数
    - `ModelType`: SQLAlchemy 模型类，继承自 Base
    - `CreateSchemaType`: Pydantic 创建模型类
    - `UpdateSchemaType`: Pydantic 更新模型类

    ## 使用示例

    ### 创建 CRUD 实例
    ```python
    user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
    ```

    ### 创建用户
    ```python
    user_data = UserCreate(name="张三", email="zhangsan@example.com")
    user = await user_crud.create(session, obj_in=user_data)
    ```

    ### 获取用户
    ```python
    user = await user_crud.get(session, id=1)
    ```

    ### 更新用户
    ```python
    update_data = UserUpdate(email="newemail@example.com")
    user = await user_crud.update(session, id=1, obj_in=update_data)
    ```

    ### 删除用户
    ```python
    await user_crud.delete(session, id=1)
    ```

    ### 获取用户列表
    ```python
    users = await user_crud.get_multi(session, skip=0, limit=10)
    ```

    ### 根据条件查询用户
    ```python
    users = await user_crud.get_multi_by_filters(
        session,
        filters=[User.name == "张三"],
        order_by=[desc(User.created_at)]
    )
    ```
    """

    def __init__(self, model: type[ModelType]):
        """
        初始化 CRUD 对象

        ## 参数
        - `model`: SQLAlchemy 模型类，必须继承自 Base

        ## 示例
        ```python
        # 创建用户 CRUD 实例
        user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
        ```
        """
        self.model = model

    async def get(
        self, session: AsyncSession, *, id: Any, options: list[Load] | None = None
    ) -> ModelType | None:
        """
        根据 ID 获取单个对象

        ## 参数
        - `session`: 数据库会话
        - `id`: 对象 ID，可以是任何类型，通常是 int 或 str
        - `options`: 查询选项列表（如 joinedload 或 selectinload）

        ## 返回值
        - `ModelType | None`: 如果找到则返回模型实例，否则返回 None

        ## 示例
        ```python
        # 获取 ID 为 1 的用户
        user = await user_crud.get(session, id=1)
        if user:
            print(f"用户名: {user.name}")
        else:
            print("用户不存在")

        # 获取用户并预加载关联数据
        from sqlalchemy.orm import joinedload
        user = await user_crud.get(session, id=1, options=[joinedload(User.profile)])
        ```
        """
        stmt = select(self.model).where(self.model.id == id)
        if options:
            for option in options:
                stmt = stmt.options(option)  # 应用查询选项
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filters(
        self,
        session: AsyncSession,
        *,
        filters: list[BinaryExpression],
        options: list[Load] | None = None,
    ) -> ModelType | None:
        """
        根据过滤条件获取单个对象

        ## 参数
        - `session`: 数据库会话
        - `filters`: 过滤条件列表
        - `options`: 查询选项列表（如 joinedload 或 selectinload）

        ## 返回值
        - `ModelType | None`: 模型实例或 None

        ## 示例
        ```python
        # 获取 id 为 1 的用户
        user = await self.get_by_filters(session, [User.id == 1])

        # 获取 name 为 "张三" 的用户
        user = await self.get_by_filters(session, [User.name == "张三"])

        # 获取 name 为 "张三" 且 age 为 25 的用户
        user = await self.get_by_filters(session, [User.name == "张三", User.age == 25])

        # 获取用户并预加载关联数据
        from sqlalchemy.orm import joinedload
        user = await self.get_by_filters(
            session,
            [User.name == "张三"],
            options=[joinedload(User.profile)]
        )
        ```
        """
        query = select(self.model)
        if filters:
            query = query.where(and_(*filters))
        if options:
            for option in options:
                query = query.options(option)  # 应用查询选项
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_404(self, session: AsyncSession, *, id: Any) -> ModelType:
        """
        根据 ID 获取单个对象，如果不存在则抛出 404 异常

        ## 参数
        - `session`: 数据库会话
        - `id`: 对象 ID，可以是任何类型，通常是 int 或 str

        ## 返回值
        - `ModelType`: 模型实例，保证存在

        ## 异常
        - `NotFoundException`: 当对象不存在时抛出，包含错误消息

        ## 示例
        ```python
        try:
            user = await user_crud.get_or_404(session, id=1)
            print(f"用户名: {user.name}")
        except NotFoundException as e:
            print(f"错误: {e.message}")
        ```
        """
        result = await self.get(session, id=id)
        if result is None:
            raise NotFoundException(msg=f"{self.model.__name__} with id {id} not found")
        return result

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int | None = None,
        limit: int | None = None,
        options: list[Load] | None = None,
        order_by: list[Any] | None = None,
    ) -> list[ModelType]:
        """
        获取多个对象列表，支持分页、查询选项和排序

        ## 参数
        - `session`: 数据库会话
        - `skip`: 跳过的记录数（偏移量）
        - `limit`: 返回的最大记录数
        - `options`: 查询选项列表（如 joinedload 或 selectinload）
        - `order_by`: 排序条件列表，可以使用 asc() 和 desc() 函数
          - `asc` 表示升序排序（正序），即从小到大排序
          - `desc` 表示降序排序（倒序），即从大到小排序

        ## 返回值
        - `list[ModelType]`: 模型实例列表

        ## 示例
        ```python
        # 按创建时间升序排序
        users = await self.get_multi(session, order_by=[asc(User.created_at)])

        # 按名称降序排序，再按创建时间升序排序
        users = await self.get_multi(session, order_by=[desc(User.name), asc(User.created_at)])

        # 获取用户并预加载关联数据
        from sqlalchemy.orm import joinedload
        users = await self.get_multi(
            session,
            options=[joinedload(User.profile)]
        )
        ```
        """
        stmt = select(self.model)
        if order_by:
            stmt = stmt.order_by(*order_by)
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
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
        skip: int | None = None,
        limit: int | None = None,
        order_by: list[Any] | None = None,
        options: list[Load] | None = None,
    ) -> list[ModelType]:
        """
        根据过滤条件获取多个对象列表，支持分页和排序

        ## 参数
        - `session`: 数据库会话
        - `filters`: 过滤条件列表
        - `skip`: 跳过的记录数（偏移量）
        - `limit`: 返回的最大记录数
        - `order_by`: 排序条件列表，可以使用 asc() 和 desc() 函数
          - `asc` 表示升序排序（正序），即从小到大排序
          - `desc` 表示降序排序（倒序），即从大到小排序
        - `options`: 查询选项列表（如 joinedload 或 selectinload）

        ## 返回值
        - `list[ModelType]`: 模型实例列表

        ## 示例
        ```python
        # 获取 name 为 "张三" 的用户列表，按创建时间降序排序
        users = await self.get_multi_by_filters(
            session,
            [User.name == "张三"],
            order_by=[desc(User.created_at)]
        )

        # 获取 name 为 "张三" 且 age 为 25 的用户列表，按年龄升序排序
        users = await self.get_multi_by_filters(
            session,
            [User.name == "张三", User.age == 25],
            order_by=[asc(User.age)]
        )

        # 获取用户并预加载关联数据
        from sqlalchemy.orm import joinedload
        users = await self.get_multi_by_filters(
            session,
            [User.is_active == True],
            options=[joinedload(User.profile)]
        )
        ```
        """
        query = select(self.model)
        if filters:
            query = query.where(and_(*filters))
        if order_by:
            query = query.order_by(*order_by)
        if options:
            for option in options:
                query = query.options(option)  # 应用查询选项
        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新对象

        ## 参数
        - `session`: 数据库会话
        - `obj_in`: 创建数据模型，继承自 BaseModel，包含要创建的数据

        ## 返回值
        - `ModelType`: 新创建的模型实例，包含数据库生成的 ID

        ## 注意
        - 此方法会自动调用 session.flush()，使对象在数据库中可见
        - 但不会自动提交事务，需要由调用者决定何时提交
        - 使用 model_dump(exclude_unset=True) 只包含已设置的字段

        ## 示例
        ```python
        # 创建新用户
        user_data = UserCreate(
            name="张三",
            email="zhangsan@example.com",
            age=25
        )
        user = await user_crud.create(session, obj_in=user_data)
        print(f"新用户 ID: {user.id}")
        ```
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

        ## 参数
        - `session`: 数据库会话
        - `id`: 对象 ID，可以是任何类型，通常是 int 或 str
        - `obj_in`: 更新数据模型，继承自 BaseModel，包含要更新的数据

        ## 返回值
        - `ModelType`: 更新后的模型实例

        ## 注意
        - 此方法会先调用 get_or_404 确保对象存在
        - 使用 model_dump(exclude_unset=True) 只更新已设置的字段
        - 使用 ORM 风格更新，逐个设置属性值
        - 会自动调用 session.flush()，使更改在数据库中可见
        - 但不会自动提交事务，需要由调用者决定何时提交

        ## 示例
        ```python
        # 更新用户邮箱
        update_data = UserUpdate(email="newemail@example.com")
        user = await user_crud.update(session, id=1, obj_in=update_data)
        print(f"更新后的邮箱: {user.email}")

        # 同时更新多个字段
        update_data = UserUpdate(
            name="李四",
            age=30,
            email="lisi@example.com"
        )
        user = await user_crud.update(session, id=1, obj_in=update_data)
        ```
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

        ## 参数
        - `session`: 数据库会话
        - `id`: 对象 ID，必须是 int 类型

        ## 异常
        - `NotFoundException`: 当对象不存在时抛出，包含错误消息
        - `InternalServerException`: 当删除操作失败时抛出，记录错误日志

        ## 注意
        - 此方法会先检查对象是否存在
        - 使用 SQLAlchemy 的 delete 语句执行删除操作
        - 不会自动提交事务，需要由调用者决定何时提交
        - 删除失败时会记录错误日志并抛出 InternalServerException

        ## 示例
        ```python
        try:
            await user_crud.delete(session, id=1)
            print("用户删除成功")
        except NotFoundException as e:
            print(f"删除失败: {e.message}")
        except InternalServerException as e:
            print(f"服务器错误: {e.message}")
        ```
        """
        db_obj = await self.get(session, id=id)
        if not db_obj:
            raise NotFoundException(msg=f"{self.model.__name__} with id {id} not found")
        try:
            stmt = delete(self.model).where(self.model.id == id)
            await session.execute(stmt)
        except Exception as e:
            logger.error(f"Failed to delete {self.model.__name__}: {e}")
            raise InternalServerException(msg="Internal server error") from e

    async def count(self, session: AsyncSession, *, filters: list[BinaryExpression] = None) -> int:
        """
        统计对象数量，支持过滤条件

        ## 参数
        - `session`: 数据库会话
        - `filters`: 过滤条件列表，使用 SQLAlchemy 的 BinaryExpression

        ## 返回值
        - `int`: 符合条件的对象数量

        ## 注意
        - 使用 func.count() 进行计数
        - 如果没有提供过滤条件，则统计所有对象数量
        - 使用 and_() 组合多个过滤条件

        ## 示例
        ```python
        # 统计所有用户数量
        total_users = await user_crud.count(session)

        # 统计年龄大于 18 的用户数量
        adult_users = await user_crud.count(
            session,
            filters=[User.age > 18]
        )

        # 统计名为"张三"且年龄大于 25 的用户数量
        specific_users = await user_crud.count(
            session,
            filters=[User.name == "张三", User.age > 25]
        )
        ```
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            query = query.where(and_(*filters))
        result = await session.execute(query)
        return result.scalar_one()
