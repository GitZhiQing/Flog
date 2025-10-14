from fastapi import APIRouter

from . import comments, posts, stats

admin_api_router = APIRouter()
admin_api_router.include_router(posts.router, prefix="/posts", tags=["管理-博文"])
admin_api_router.include_router(comments.router, prefix="/comments", tags=["管理-评论"])
admin_api_router.include_router(stats.router, prefix="/stats", tags=["管理-统计"])
