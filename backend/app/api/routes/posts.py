from fastapi import APIRouter, Query
from sqlalchemy import and_, desc

from app.core import exceptions
from app.core.config import get_settings
from app.core.file_system import get_markdown_content_and_metadata, sync_posts_to_database
from app.crud.post import crud_post
from app.deps import session_dep
from app.models.enums import PostStatusEnum
from app.models.post import Post as PostModel
from app.schemas import BaseResponse, PageResponse, PageResult, Post, PostContent, PostUpdate

router = APIRouter()
settings = get_settings()


@router.post("/sync", response_model=BaseResponse[dict])
async def sync_posts(session: session_dep):
    """同步文章文件到数据库"""
    stats = await sync_posts_to_database(session)
    return BaseResponse.success(
        data=stats,
        msg=f"同步完成: 新增 {stats['added']} 篇，更新 {stats['updated']} 篇，删除 {stats['deleted']} 篇",
    )


@router.get("", response_model=PageResponse[Post])
async def get_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取全部文章列表"""
    skip = (page - 1) * size
    total = await crud_post.count(session)
    posts = await crud_post.get_multi(
        session, skip=skip, limit=size, order_by=[desc(PostModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Post](total=total, page=page, size=size, items=posts)
    )


@router.get("/status/show", response_model=PageResponse[Post])
async def get_show_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取可见文章列表"""
    skip = (page - 1) * size
    filters = [PostModel.status == PostStatusEnum.SHOW]
    total = await crud_post.count(session, filters=filters)
    posts = await crud_post.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(PostModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Post](total=total, page=page, size=size, items=posts),
        msg=f"获取 {total} 篇可见文章",
    )


@router.get("/status/hide", response_model=PageResponse[Post])
async def get_hide_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取隐藏文章列表"""
    skip = (page - 1) * size
    filters = [PostModel.status == PostStatusEnum.HIDE]
    total = await crud_post.count(session, filters=filters)
    posts = await crud_post.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(PostModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Post](total=total, page=page, size=size, items=posts),
        msg=f"获取 {total} 篇隐藏文章",
    )


@router.get("/slug/{post_slug}", response_model=BaseResponse[PostContent])
async def get_post_by_slug(session: session_dep, slug: str):
    """通过 slug 获取可见文章"""
    post = await crud_post.get_by_filters(
        session, filters=[and_(PostModel.slug == slug, PostModel.status == PostStatusEnum.SHOW)]
    )
    if not post:
        raise exceptions.NotFoundException(msg="Post not found")
    content = get_markdown_content_and_metadata(settings.DATA_DIR / post.file_path)["content"]
    post_content = PostContent(
        slug=post.slug,
        title=post.title,
        category=post.category,
        content=content,
    )
    return BaseResponse.success(
        data=post_content,
        msg="获取文章成功",
    )


@router.put("/slug/{post_slug}/status/{status}", response_model=BaseResponse[Post])
async def update_post_status(session: session_dep, post_slug: str, status: PostStatusEnum):
    """通过 slug 更新博文状态"""
    post = await crud_post.get_by_filters(
        session,
        filters=[and_(PostModel.slug == post_slug, PostModel.status == PostStatusEnum.SHOW)],
    )
    if not post:
        raise exceptions.NotFoundException(msg="Post not found")
    post_update = PostUpdate(status=status)
    post_updated = await crud_post.update(session, id=post.id, obj_in=post_update)
    return BaseResponse.success(
        data=post_updated,
        msg=f"更新文章状态为 {status.value}",
    )
