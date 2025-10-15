from fastapi import APIRouter, Query

from app.crud.post import crud_post
from app.deps import session_dep
from app.models.enums import PostStatusEnum
from app.models.post import Post as PostModel
from app.schemas import BaseResponse, PageResponse, PageResult, Post

router = APIRouter()


@router.get("", response_model=BaseResponse[list[str | None]])
async def get_categories(session: session_dep):
    """获取分类列表"""
    categories = await crud_post.get_categories(session)
    return BaseResponse.success(data=categories)


@router.get("/{category_name}/posts", response_model=PageResponse[Post])
async def get_posts_by_category(
    session: session_dep,
    category_name: str,
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
):
    """根据分类名称获取**可见**文章列表"""
    skip = (page - 1) * size
    filters = [PostModel.category == category_name, PostModel.status == PostStatusEnum.SHOW]
    total = await crud_post.count(session, filters=filters)
    posts = await crud_post.get_multi_by_filters(session, filters=filters, skip=skip, limit=size)
    return PageResponse.success(
        data=PageResult[Post](total=total, page=page, size=size, items=posts)
    )
