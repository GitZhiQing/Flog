from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate


class CRUDPlatform(CRUDBase[Platform, PlatformCreate, PlatformUpdate]):
    """平台配置CRUD操作类"""

    async def get_first(self, session: AsyncSession) -> Platform | None:
        """获取第一条平台配置记录"""
        stmt = select(Platform).order_by(Platform.id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_default(self, session: AsyncSession) -> Platform:
        """获取或创建默认平台配置"""
        platform = await self.get_first(session)
        if platform is None:
            platform_data = {
                "title": "Flog",
                "description": "一个文件驱动的博客系统",
                "footer": "© 2023 Flog. All rights reserved.",
            }
            platform = Platform(**platform_data)
            session.add(platform)
            await session.flush()
        return platform

    async def update_config(
        self,
        session: AsyncSession,
        *,
        title: str | None = None,
        description: str | None = None,
        footer: str | None = None,
    ) -> Platform:
        """更新平台配置"""
        platform = await self.get_or_create_default(session)

        if title is not None:
            platform.title = title
        if description is not None:
            platform.description = description
        if footer is not None:
            platform.footer = footer

        session.add(platform)
        await session.flush()
        return platform


# 创建平台配置CRUD实例
crud_platform = CRUDPlatform(Platform)
