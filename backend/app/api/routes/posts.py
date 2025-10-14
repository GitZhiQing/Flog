from fastapi import APIRouter, HTTPException, Query

from app.crud.post import crud_post
from app.deps import session_dep
from app.schemas import (
    BaseResponse,
    PageResponse,
    PageResult,
    Post,
    PostCategory,
)

router = APIRouter()


@router.get("", response_model=PageResponse[Post])
async def get_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: str | None = Query(None, description="分类过滤"),
    search: str | None = Query(None, description="搜索关键词"),
):
    """获取文章列表"""
    skip = (page - 1) * size
    posts = await crud_post.get_visible_posts(
        session, skip=skip, limit=size, category=category, search=search
    )
    total = await crud_post.count_visible_posts(session, category=category, search=search)
    data = PageResult(total=total, page=page, size=size, items=posts)
    return PageResponse.success(data=data)


@router.get("/{id}", response_model=BaseResponse[Post])
async def get_post(id: int, session: session_dep):
    """获取文章详情"""
    db_post = await crud_post.get_or_404(session, id=id)
    # 如果文章被隐藏，返回404
    if db_post.is_hidden:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 增加访问量
    await crud_post.increment_view_count(session, id=id)
    return BaseResponse.success(data=db_post)


@router.get("/categories/list", response_model=BaseResponse[list[PostCategory]])
async def get_categories(session: session_dep):
    """获取所有文章分类"""
    categories = await crud_post.get_categories(session)
    # 统计每个分类的文章数量
    result = []
    for category in categories:
        count = await crud_post.count_visible_posts(session, category=category)
        result.append(PostCategory(category=category, count=count))
    return BaseResponse.success(data=result)


@router.get("/category/{category}", response_model=PageResponse[Post])
async def get_posts_by_category(
    category: str,
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """根据分类获取文章列表"""
    skip = (page - 1) * size
    posts = await crud_post.get_by_category(session, category=category, skip=skip, limit=size)
    total = await crud_post.count_visible_posts(session, category=category)
    data = PageResult(total=total, page=page, size=size, items=posts)
    return PageResponse.success(data=data)
