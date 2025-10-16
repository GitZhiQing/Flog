import pytest
from httpx import AsyncClient

from app.core.config import TestingSettings


@pytest.mark.anyio
async def test_read_root(client: AsyncClient, settings: TestingSettings):
    """测试根路由"""
    response = await client.get("/")
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["msg"] == "success"
