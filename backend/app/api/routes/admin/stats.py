from fastapi import APIRouter

from app.deps import session_dep

router = APIRouter()


@router.get("", tags=["后台-统计"])
async def get_stats(session: session_dep):
    """获取后台统计数据"""
    # 这里需要实现统计逻辑，暂时返回空字典
    # 实际实现需要统计文章数量、评论数量、访问量等
    return {
        "total_posts": 0,
        "total_comments": 0,
        "total_views": 0,
        "recent_posts": [],
        "recent_comments": [],
    }
