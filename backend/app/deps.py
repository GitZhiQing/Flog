from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.exceptions import BizException


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    安全获取数据库会话的依赖项，自动处理事务和异常
    """
    async with async_session_factory() as session:
        try:
            async with session.begin():
                yield session
        except SQLAlchemyError as e:
            logger.error(f"数据库操作失败: {str(e)}")

            raise BizException(code=500, msg="Internal server error") from e


# session 依赖项
# 使用示例: async def get_todos(session: session_dep)
session_dep = Annotated[AsyncSession, Depends(get_session)]
