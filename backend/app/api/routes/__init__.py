from fastapi import APIRouter

from . import categories, comments, posts

router = APIRouter()

router.include_router(posts.router, prefix="/posts", tags=["博文"])
router.include_router(comments.router, prefix="/comments", tags=["评论"])
router.include_router(categories.router, prefix="/categories", tags=["分类"])
