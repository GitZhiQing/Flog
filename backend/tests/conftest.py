from collections.abc import AsyncGenerator

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import TestingSettings, get_settings

load_dotenv()


@pytest.fixture(scope="session")
def anyio_backend():
    """To solve the ERROR at setup of test_read_root[asyncio]
    Ref: https://stackoverflow.com/a/72996947
    """
    return "asyncio"


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """FastAPI 应用实例"""
    from app.main import app

    return app


@pytest.fixture(scope="session", autouse=True)
async def life() -> AsyncGenerator[None]:
    """全局生命周期管理(自动使用)"""
    from app.core.lifecycle import shutdown, startup

    try:
        await startup()
        yield
    finally:
        await shutdown()


@pytest.fixture(scope="session")
async def settings() -> TestingSettings:
    """应用配置"""
    settings = get_settings()
    if settings.ENV != "testing":
        raise RuntimeError(f"ENV must be testing, but now it's {settings.ENV}")
    return get_settings()


@pytest.fixture(scope="session")
async def client(app: FastAPI, settings: TestingSettings) -> AsyncGenerator[AsyncClient]:
    """异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def admin_token_headers(client: AsyncClient, settings: TestingSettings) -> dict[str, str]:
    """管理员 Basic Auth 头 fixture"""
    # 通过 BASIC_AUTH_USERNAME 和 BASIC_AUTH_PASSWORD 构造
    return {"Authorization": f"Basic {settings.BASIC_AUTH_USERNAME}:{settings.BASIC_AUTH_PASSWORD}"}
