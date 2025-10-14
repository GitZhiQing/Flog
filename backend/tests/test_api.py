import pytest
from fastapi.testclient import TestClient

from app.main import create_app

# 创建测试应用
app = create_app()
client = TestClient(app)


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"
    assert "data" in data
    assert data["data"]["status"] == "ok"


def test_get_articles():
    """测试获取文章列表接口"""
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "items" in data["data"]
    assert "total" in data["data"]
    assert "page" in data["data"]
    assert "size" in data["data"]


def test_get_platform():
    """测试获取平台配置接口"""
    response = client.get("/api/v1/platform")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "title" in data["data"]
    assert "description" in data["data"]
    assert "footer" in data["data"]


def test_get_categories():
    """测试获取文章分类列表接口"""
    response = client.get("/api/v1/articles/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_comments():
    """测试获取评论列表接口"""
    response = client.get("/api/v1/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "items" in data["data"]
    assert "total" in data["data"]
    assert "page" in data["data"]
    assert "size" in data["data"]


def test_create_comment():
    """测试创建评论接口"""
    # 首先获取文章列表，确保有文章存在
    articles_response = client.get("/api/v1/articles")
    assert articles_response.status_code == 200
    articles_data = articles_response.json()

    if articles_data["data"]["total"] > 0:
        article_id = articles_data["data"]["items"][0]["id"]

        # 创建评论
        comment_data = {
            "content": "这是一条测试评论",
            "author_name": "测试用户",
            "author_email": "test@example.com",
            "author_website": "https://example.com",
            "post_id": article_id,
        }

        response = client.post("/api/v1/comments", json=comment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert data["data"]["content"] == comment_data["content"]
        assert data["data"]["author_name"] == comment_data["author_name"]


def test_get_admin_stats():
    """测试获取统计数据接口"""
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "posts_count" in data["data"]
    assert "comments_count" in data["data"]
    assert "categories_count" in data["data"]


if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])
