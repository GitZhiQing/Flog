from fastapi import APIRouter, Query
from sqlalchemy import desc
from sqlalchemy.orm import selectinload

from app.core import exceptions
from app.core.config import get_settings
from app.core.file_system import get_markdown_content_and_metadata, sync_posts_to_database
from app.crud.post import crud_post
from app.deps import session_dep
from app.models.enums import PostStatusEnum
from app.models.post import Post as PostModel
from app.schemas import (
    BaseResponse,
    PageResponse,
    PageResult,
    Post,
    PostContent,
    PostUpdate,
)

router = APIRouter()
settings = get_settings()


@router.post("/actions/sync", response_model=BaseResponse[dict])
async def sync_posts(session: session_dep):
    """同步文章文件到数据库"""
    stats = await sync_posts_to_database(session)
    return BaseResponse.success(data=stats)


@router.get("", response_model=PageResponse[Post])
async def get_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: PostStatusEnum = Query(PostStatusEnum.SHOW, description="文章状态筛选"),
):
    """获取文章列表，支持按状态筛选"""
    skip = (page - 1) * size
    filters = []
    # 添加状态筛选
    # TODO: HIDE 文章需要鉴权
    filters.append(PostModel.status == status)
    total = await crud_post.count(session, filters=filters if filters else None)
    posts = await crud_post.get_multi_by_filters(
        session,
        filters=filters if filters else None,
        skip=skip,
        limit=size,
        order_by=[desc(PostModel.created_at)],
        options=[selectinload(PostModel.comments)],
    )
    return PageResponse.success(
        data=PageResult[Post](total=total, page=page, size=size, items=posts)
    )


@router.patch("/slug/{post_slug}/status", response_model=BaseResponse[Post])
async def update_post_status(
    session: session_dep,
    post_slug: str,
    status: PostStatusEnum = Query(PostStatusEnum.SHOW, description="文章状态"),
):
    """更新文章状态"""
    # TODO: 需要鉴权
    post = await crud_post.get_by_filters(session, filters=[PostModel.slug == post_slug])
    if not post:
        raise exceptions.NotFoundException(msg="Post not found")
    post_updated = await crud_post.update(session, id=post.id, obj_in=PostUpdate(status=status))
    return BaseResponse.success(data=post_updated)


@router.get("/slug/{post_slug}", response_model=BaseResponse[PostContent])
async def get_post_by_slug(session: session_dep, post_slug: str):
    """通过 slug 获取文章"""
    # TODO: HIDE 文章需要鉴权
    post = await crud_post.get_by_filters(session, filters=[PostModel.slug == post_slug])
    if not post:
        raise exceptions.NotFoundException(msg="Post not found")
    if post.status == PostStatusEnum.HIDE:  # TODO: HIDE 文章需要鉴权
        raise exceptions.NotFoundException(msg="Post not found")
    content = get_markdown_content_and_metadata(settings.DATA_DIR / post.file_path)["content"]
    post_content = PostContent(
        slug=post.slug,
        title=post.title,
        category=post.category,
        content=content,
    )
    return BaseResponse.success(data=post_content)
