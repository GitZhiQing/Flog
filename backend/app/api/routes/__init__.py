from fastapi import APIRouter

from . import comments, platform, posts
from .admin import admin_api_router

api_router = APIRouter()

api_router.include_router(posts.router, prefix="/posts", tags=["博文"])
api_router.include_router(comments.router, prefix="/comments", tags=["评论"])
api_router.include_router(platform.router, prefix="/platform", tags=["平台配置"])

__all__ = ["api_router", "admin_api_router"]
