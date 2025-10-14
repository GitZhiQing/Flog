from fastapi import APIRouter, Query

from app.crud.comment import crud_comment
from app.deps import session_dep
from app.schemas import BaseResponse, Comment, CommentList, PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[CommentList])
async def get_all_comments(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_hidden: bool | None = Query(None, description="是否隐藏"),
    post_id: int | None = Query(None, description="博文ID"),
):
    """获取所有评论列表（包括隐藏的）"""
    skip = (page - 1) * size

    if post_id is not None:
        comments = await crud_comment.get_by_post_id(
            session, post_id=post_id, skip=skip, limit=size
        )
        total = await crud_comment.count_by_post_id(session, post_id=post_id)
    else:
        comments = await crud_comment.get_all(session, skip=skip, limit=size, is_hidden=is_hidden)
        total = await crud_comment.count(session, is_hidden=is_hidden)

    comment_list = []
    for c in comments:
        comment_data = CommentList.model_validate(c)
        comment_data.is_reply = c.is_reply
        comment_data.reply_count = c.reply_count
        comment_list.append(comment_data)

    return PageResponse.create(comment_list, total, page, size)


@router.get("/{id}", response_model=BaseResponse[Comment])
async def get_comment(id: int, session: session_dep):
    """获取评论详情"""
    db_comment = await crud_comment.get_or_404(session, id=id)

    comment_model = Comment.model_validate(db_comment)
    comment_model.is_reply = db_comment.is_reply
    comment_model.reply_count = db_comment.reply_count
    comment_model.level = db_comment.get_level()

    return BaseResponse.success(data=comment_model)


@router.get("/{id}/replies", response_model=BaseResponse[list[Comment]])
async def get_comment_replies(id: int, session: session_dep):
    """获取评论的回复列表"""
    replies = await crud_comment.get_replies(session, parent_id=id)

    reply_list = []
    for r in replies:
        reply_model = Comment.model_validate(r)
        reply_model.is_reply = r.is_reply
        reply_model.reply_count = r.reply_count
        reply_model.level = r.get_level()
        reply_list.append(reply_model)

    return BaseResponse.success(data=reply_list)


@router.put("/{id}/hide", response_model=BaseResponse[Comment])
async def hide_comment(id: int, session: session_dep):
    """隐藏评论"""
    db_comment = await crud_comment.hide_comment(session, id=id)

    comment_model = Comment.model_validate(db_comment)
    comment_model.is_reply = db_comment.is_reply
    comment_model.reply_count = db_comment.reply_count
    comment_model.level = db_comment.get_level()

    return BaseResponse.success(data=comment_model)


@router.put("/{id}/show", response_model=BaseResponse[Comment])
async def show_comment(id: int, session: session_dep):
    """显示评论"""
    db_comment = await crud_comment.show_comment(session, id=id)

    comment_model = Comment.model_validate(db_comment)
    comment_model.is_reply = db_comment.is_reply
    comment_model.reply_count = db_comment.reply_count
    comment_model.level = db_comment.get_level()

    return BaseResponse.success(data=comment_model)


@router.delete("/{id}", response_model=BaseResponse[dict])
async def delete_comment(id: int, session: session_dep):
    """删除评论"""
    await crud_comment.delete(session, id=id)
    return BaseResponse.success(data={"message": "评论已删除"})


@router.delete("/{id}/with-replies", response_model=BaseResponse[dict])
async def delete_comment_with_replies(id: int, session: session_dep):
    """删除评论及其所有回复"""
    db_comment = await crud_comment.get_or_404(session, id=id)

    # 获取所有回复
    all_replies = db_comment.get_all_replies()

    # 删除所有回复
    for reply in all_replies:
        await crud_comment.delete(session, id=reply.id)

    # 删除原评论
    await crud_comment.delete(session, id=id)

    return BaseResponse.success(data={"message": "评论及其所有回复已删除"})
