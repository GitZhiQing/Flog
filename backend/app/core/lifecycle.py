from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from app.core.config import get_settings
from app.core.database import Base, async_engine, async_session_factory
from app.crud import crud_post

settings = get_settings()


def ensure_data_dirs() -> None:
    """确保所有必要的数据目录存在"""
    try:
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        settings.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        settings.PAGES_DIR.mkdir(parents=True, exist_ok=True)
        settings.POSTS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("数据目录创建成功")
    except OSError as e:
        logger.error(f"创建数据目录失败: {e}")
        raise


async def test_db_connection() -> bool:
    """测试数据库连接"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("数据库连接测试成功")
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: [{settings.SQLALCHEMY_DATABASE_URI}] {e}")
        return False


async def check_first_startup() -> bool:
    """检查是否是第一次启动"""
    try:
        is_first_startup = True
        if settings.ENV != "production":
            logger.info("检测是否首次启动: 开发环境，默认首次启动")
            return is_first_startup
        async with async_session_factory() as session:
            post_count = await crud_post.count(session)
            is_first_startup = post_count == 0
        logger.info(f"检测是否首次启动: 生产环境，当前博客文章数量为 {post_count}")
        return is_first_startup
    except SQLAlchemyError as e:
        logger.error(f"检查首次启动状态失败: {e}")
        return True


async def initialize_database(force_drop: bool = False) -> bool:
    """数据库初始化"""
    try:
        if force_drop and settings.ENV == "production":
            raise RuntimeError("生产环境禁止强制删除数据库表")
        async with async_engine.begin() as conn:
            if force_drop:
                logger.warning("强制删除数据库表")
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建完成")
        return True
    except SQLAlchemyError as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
    except Exception as e:
        logger.error(f"数据库初始化过程中发生未知错误: {e}")
        return False


async def cleanup_resources() -> None:
    """清理资源"""
    try:
        await async_engine.dispose()  # 关闭数据库连接
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"资源清理失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    logger.info("应用启动中...")
    # 启动阶段
    try:
        ensure_data_dirs()  # 1. 确保数据目录存在
        if not await test_db_connection():  # 2. 测试数据库连接
            raise RuntimeError("数据库连接失败，应用启动终止")
        # 3. 检查是否是第一次启动并初始化数据库
        is_first_startup = await check_first_startup()
        if is_first_startup:
            force_drop = settings.ENV != "production"
            logger.info(f"首次启动，{'强制' if force_drop else '非强制'}删除数据库表并重建")
            if not await initialize_database(force_drop=force_drop):
                raise RuntimeError("数据库初始化失败，应用启动终止")
        else:
            logger.info("数据库已初始化，跳过创建表")
        logger.info("应用启动完成")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise

    # 应用运行阶段
    try:
        yield
    except Exception as e:
        logger.error(f"应用运行时发生错误: {e}")
        raise

    # 关闭阶段
    logger.info("应用关闭中...")
    try:
        await cleanup_resources()
        logger.info("应用关闭完成")
    except Exception as e:
        logger.error(f"应用关闭过程中发生错误: {e}")
