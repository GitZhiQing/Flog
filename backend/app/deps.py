import base64
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.core.exceptions import AuthenticationException, BizException


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    安全获取数据库会话的依赖项，自动处理事务和异常
    """
    async with async_session_factory() as session:
        try:
            async with session.begin():
                yield session
        except SQLAlchemyError as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise BizException(code=500, msg="Internal server error") from e


# Basic Auth 安全方案
security = HTTPBasic()


async def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """验证 Basic Auth 认证信息"""
    settings = get_settings()
    # 验证用户名和密码
    is_correct_username = credentials.username == settings.BASIC_AUTH_USERNAME
    is_correct_password = credentials.password == settings.BASIC_AUTH_PASSWORD
    if not (is_correct_username and is_correct_password):
        raise AuthenticationException(msg="Invalid authentication credentials")
    return True


# Basic Auth 可选认证依赖项
async def verify_basic_auth_optional(request: Request) -> bool | None:
    """Basic Auth 可选认证依赖项"""
    # 检查是否有 Authorization 头
    authorization = request.headers.get("Authorization")
    if not authorization:  # 未提供认证信息
        return None
    scheme, param = get_authorization_scheme_param(authorization)
    if not scheme or scheme.lower() != "basic":  # 不是 Basic Auth 认证
        return None
    # 如果提供了 Basic Auth，则验证它
    try:
        # 手动解析 Basic Auth
        decoded = base64.b64decode(param).decode("ascii")
        username, password = decoded.split(":")
        settings = get_settings()
        is_correct_username = username == settings.BASIC_AUTH_USERNAME
        is_correct_password = password == settings.BASIC_AUTH_PASSWORD
        if not (is_correct_username and is_correct_password):
            raise AuthenticationException(msg="Invalid authentication credentials")
        return True
    except Exception:
        raise AuthenticationException(msg="Invalid authentication credentials") from None


# session 依赖项
# 使用示例: async def get_todos(session: session_dep)
session_dep = Annotated[AsyncSession, Depends(get_session)]
# Basic Auth 认证依赖项
# 使用示例: async def protected_route(session: session_dep, auth: basic_auth_dep)
basic_auth_dep = Annotated[bool, Depends(verify_basic_auth)]
# Basic Auth 可选认证依赖项
optional_basic_auth_dep = Annotated[bool | None, Depends(verify_basic_auth_optional)]
