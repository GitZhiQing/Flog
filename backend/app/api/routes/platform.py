from fastapi import APIRouter

from app.crud.platform import crud_platform
from app.deps import session_dep
from app.schemas import BaseResponse, Platform, PlatformInfo, PlatformUpdate

router = APIRouter()


@router.get("/", response_model=BaseResponse[PlatformInfo])
async def get_platform_info(session: session_dep):
    """获取平台配置信息"""
    db_platform = await crud_platform.get_or_create_default(session)
    platform_info = PlatformInfo(
        title=db_platform.title,
        description=db_platform.description,
        footer=db_platform.footer,
    )
    return BaseResponse.success(data=platform_info)


@router.put("/", response_model=BaseResponse[Platform])
async def update_platform_info(platform_data: PlatformUpdate, session: session_dep):
    """更新平台配置信息"""
    db_platform = await crud_platform.update_config(
        session,
        title=platform_data.title,
        description=platform_data.description,
        footer=platform_data.footer,
    )
    return BaseResponse.success(data=Platform.model_validate(db_platform))
