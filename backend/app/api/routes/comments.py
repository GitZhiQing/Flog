from fastapi import APIRouter, Query
from sqlalchemy import desc

from app.core import exceptions
from app.crud.comment import crud_comment
from app.crud.post import crud_post
from app.deps import session_dep
from app.models.comment import Comment as CommentModel
from app.models.enums import CommentStatusEnum
from app.models.post import Post as PostModel
from app.schemas import (
    BaseResponse,
    Comment,
    CommentCreate,
    CommentUpdate,
    PageResponse,
    PageResult,
)

router = APIRouter()


@router.get("", response_model=PageResponse[Comment])
async def get_comments(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    post_slug: str | None = Query(None, description="博文 slug 筛选"),
    status: CommentStatusEnum = Query(CommentStatusEnum.SHOW, description="评论状态筛选"),
):
    """获取评论列表，支持按状态和博文 slug 筛选"""
    skip = (page - 1) * size
    filters = []
    # 筛选评论状态(TODO: HIDE 评论需要鉴权)
    filters.append(CommentModel.status == status)
    if post_slug:  # 筛选指定博文的评论
        filters.append(CommentModel.post_slug == post_slug)
    total = await crud_comment.count(session, filters=filters if filters else None)
    comments = await crud_comment.get_multi_by_filters(
        session,
        filters=filters if filters else None,
        skip=skip,
        limit=size,
        order_by=[desc(CommentModel.created_at)],
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.post("", response_model=BaseResponse[Comment])
async def create_comment(comment_create: CommentCreate, session: session_dep):
    """创建评论"""
    # 检查博文是否存在
    post = await crud_post.get_by_filters(
        session, filters=[PostModel.slug == comment_create.post_slug]
    )
    if not post:
        raise exceptions.NotFoundException(msg="Post not found")
    # 检查父评论是否存在(如果有)
    if comment_create.parent_id:
        await crud_comment.get_or_404(session, id=comment_create.parent_id)
    comment_created = await crud_comment.create(session, obj_in=comment_create)
    return BaseResponse.success(data=comment_created)


@router.patch("/{comment_id}/status", response_model=BaseResponse[Comment])
async def update_comment_status(
    comment_id: int,
    session: session_dep,
    status: CommentStatusEnum = Query(..., description="评论状态筛选"),
):
    """更新评论状态"""
    # TODO: 需要鉴权
    await crud_comment.get_or_404(session, id=comment_id)
    comment_updated = await crud_comment.update(
        session, id=comment_id, obj_in=CommentUpdate(status=status)
    )
    return BaseResponse.success(data=comment_updated)


@router.delete("/{comment_id}", response_model=BaseResponse[dict])
async def delete_comment(
    comment_id: int,
    session: session_dep,
):
    """删除评论"""
    # TODO: 需要鉴权
    await crud_comment.get_or_404(session, id=comment_id)
    await crud_comment.delete(session, id=comment_id)
    return BaseResponse.success()
