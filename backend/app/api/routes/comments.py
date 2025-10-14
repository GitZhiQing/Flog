from fastapi import APIRouter, Query

from app.crud.comment import crud_comment
from app.deps import session_dep
from app.schemas import BaseResponse, Comment, CommentCreate, CommentList, PageResponse

router = APIRouter()


@router.get("/", response_model=PageResponse[CommentList])
async def get_comments(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取所有评论列表"""
    skip = (page - 1) * size
    comments = await crud_comment.get_all_visible(session, skip=skip, limit=size)
    total = await crud_comment.count(session)

    comment_list = []
    for c in comments:
        comment_data = CommentList.model_validate(c)
        comment_data.is_reply = c.is_reply
        comment_data.reply_count = c.reply_count
        comment_list.append(comment_data)

    return PageResponse.create(comment_list, total, page, size)


@router.get("/post/{post_id}", response_model=BaseResponse[list[Comment]])
async def get_comments_by_post(post_id: int, session: session_dep):
    """根据博文ID获取评论列表"""
    comments = await crud_comment.get_by_post_id(session, post_id=post_id)

    # 构建评论树结构
    comment_dict = {}
    for c in comments:
        comment_model = Comment.model_validate(c)
        comment_model.is_reply = c.is_reply
        comment_model.reply_count = c.reply_count
        comment_model.level = c.get_level()
        comment_dict[c.id] = comment_model

    root_comments = []
    for c in comments:
        if c.parent_id is None:
            root_comments.append(comment_dict[c.id])
        else:
            parent = comment_dict.get(c.parent_id)
            if parent:
                parent.replies.append(comment_dict[c.id])

    return BaseResponse.success(data=root_comments)


@router.get("/post/{post_id}/top-level", response_model=PageResponse[CommentList])
async def get_top_level_comments_by_post(
    post_id: int,
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """根据博文ID获取顶级评论列表"""
    skip = (page - 1) * size
    comments = await crud_comment.get_top_level_comments(
        session, post_id=post_id, skip=skip, limit=size
    )
    total = await crud_comment.count_by_post_id(session, post_id=post_id)

    comment_list = []
    for c in comments:
        comment_data = CommentList.model_validate(c)
        comment_data.is_reply = c.is_reply
        comment_data.reply_count = c.reply_count
        comment_list.append(comment_data)

    return PageResponse.create(comment_list, total, page, size)


@router.get("/{comment_id}/replies", response_model=BaseResponse[list[Comment]])
async def get_comment_replies(comment_id: int, session: session_dep):
    """获取评论的回复列表"""
    replies = await crud_comment.get_replies(session, parent_id=comment_id)

    reply_list = []
    for r in replies:
        reply_model = Comment.model_validate(r)
        reply_model.is_reply = r.is_reply
        reply_model.reply_count = r.reply_count
        reply_model.level = r.get_level()
        reply_list.append(reply_model)

    return BaseResponse.success(data=reply_list)


@router.post("/", response_model=BaseResponse[Comment])
async def create_comment(comment_data: CommentCreate, session: session_dep):
    """创建评论"""
    db_comment = await crud_comment.create_comment(
        session,
        content=comment_data.content,
        author_name=comment_data.author_name,
        author_email=comment_data.author_email,
        author_link=comment_data.author_link,
        post_id=comment_data.post_id,
        parent_id=comment_data.parent_id,
    )

    comment_model = Comment.model_validate(db_comment)
    comment_model.is_reply = db_comment.is_reply
    comment_model.reply_count = db_comment.reply_count
    comment_model.level = db_comment.get_level()

    return BaseResponse.success(data=comment_model)


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
