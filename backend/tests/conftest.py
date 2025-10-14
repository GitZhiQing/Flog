import asyncio
from collections.abc import AsyncGenerator

import pytest
from app.db.base import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Comment, Platform, Post

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# 创建测试会话
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    """创建测试数据库会话"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def sample_article(db_session: AsyncSession) -> Post:
    """创建示例文章"""
    article = Post(
        title="测试文章",
        content="这是一篇测试文章的内容。",
        category="测试",
        tags="测试,文章",
        file_path="test.md",
        file_hash="test_hash",
        is_published=True,
        view_count=0,
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return article


@pytest.fixture(scope="function")
async def sample_comment(db_session: AsyncSession, sample_article: Post) -> Comment:
    """创建示例评论"""
    comment = Comment(
        content="这是一条测试评论",
        author_name="测试用户",
        author_email="test@example.com",
        post_id=sample_article.id,
        ip_address="127.0.0.1",
        user_agent="TestAgent",
        is_visible=True,
    )
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment


@pytest.fixture(scope="function")
async def sample_platform(db_session: AsyncSession) -> Platform:
    """创建示例平台配置"""
    platform = Platform(title="测试博客", description="这是一个测试博客", footer="© 2023 测试博客")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)
    return platform
