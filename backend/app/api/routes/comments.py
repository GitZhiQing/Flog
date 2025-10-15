from fastapi import APIRouter, Query
from sqlalchemy import and_, desc

from app.crud.comment import crud_comment
from app.deps import session_dep
from app.models.comment import Comment as CommentModel
from app.models.enums import CommentStatusEnum
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
):
    """获取全部评论列表"""
    skip = (page - 1) * size
    total = await crud_comment.count(session)
    comments = await crud_comment.get_multi(
        session, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.get("/status/show", response_model=PageResponse[Comment])
async def get_show_comments(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取可见评论列表"""
    skip = (page - 1) * size
    filters = [CommentModel.status == CommentStatusEnum.SHOW]
    total = await crud_comment.count(session, filters=filters)
    comments = await crud_comment.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.get("/status/hide", response_model=PageResponse[Comment])
async def get_hide_comments(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取隐藏评论列表"""
    skip = (page - 1) * size
    filters = [CommentModel.status == CommentStatusEnum.HIDE]
    total = await crud_comment.count(session, filters=filters)
    comments = await crud_comment.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.get("/post/{post_id}", response_model=PageResponse[Comment])
async def get_comments_by_post(
    session: session_dep,
    post_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """根据博文 ID 获取全部评论列表"""
    skip = (page - 1) * size
    filters = [CommentModel.post_id == post_id]
    total = await crud_comment.count(session, filters=filters)
    comments = await crud_comment.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.get("/post/{post_id}/status/hide", response_model=PageResponse[Comment])
async def get_hide_comments_by_post(
    session: session_dep,
    post_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """根据博文 ID 获取隐藏评论列表"""
    skip = (page - 1) * size
    filters = [and_(CommentModel.post_id == post_id, CommentModel.status == CommentStatusEnum.HIDE)]
    total = await crud_comment.count(session, filters=filters)
    comments = await crud_comment.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.get("/post/{post_id}/status/show", response_model=PageResponse[Comment])
async def get_show_comments_by_post(
    session: session_dep,
    post_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """根据博文 ID 获取可见评论列表"""
    skip = (page - 1) * size
    filters = [and_(CommentModel.post_id == post_id, CommentModel.status == CommentStatusEnum.SHOW)]
    total = await crud_comment.count(session, filters=filters)
    comments = await crud_comment.get_multi_by_filters(
        session, filters=filters, skip=skip, limit=size, order_by=[desc(CommentModel.created_at)]
    )
    return PageResponse.success(
        data=PageResult[Comment](total=total, page=page, size=size, items=comments)
    )


@router.post("/", response_model=BaseResponse[Comment])
async def create_comment(comment_create: CommentCreate, session: session_dep):
    """创建评论"""
    comment_created = await crud_comment.create(session, obj_in=comment_create)
    return BaseResponse.success(data=comment_created)


@router.put("/{comment_id}/status/{status}", response_model=BaseResponse[Comment])
async def update_comment_status(session: session_dep, comment_id: int, status: CommentStatusEnum):
    """更新评论状态"""
    await crud_comment.get_or_404(session, id=comment_id)
    comment_update = CommentUpdate(status=status)
    comment_updated = await crud_comment.update(session, id=comment_id, obj_in=comment_update)
    return BaseResponse.success(data=comment_updated)
