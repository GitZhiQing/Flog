from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""

    pass


settings = get_settings()

# 创建异步数据库引擎
async_engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DEBUG,  # 调试模式下显示 SQL 语句
    future=True,  # 启用 2.0 风格
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不使实例过期
    autoflush=True,  # 自动刷新
    autocommit=False,  # 不自动提交
)
