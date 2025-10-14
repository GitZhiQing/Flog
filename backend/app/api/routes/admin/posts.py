from fastapi import APIRouter, Query

from app.crud.post import crud_post
from app.deps import session_dep
from app.schemas import (
    BaseResponse,
    PageResponse,
    PageResult,
    Post,
    PostCreate,
    PostUpdate,
)

router = APIRouter()


@router.get("", response_model=PageResponse[Post])
async def get_all_posts(
    session: session_dep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: str | None = Query(None, description="分类过滤"),
    search: str | None = Query(None, description="搜索关键词"),
    is_hidden: bool | None = Query(None, description="是否隐藏"),
):
    """获取所有文章列表（包括隐藏的）"""
    skip = (page - 1) * size
    total = await crud_post.count_all(
        session, category=category, search=search, is_hidden=is_hidden
    )
    posts = await crud_post.get_all(
        session,
        skip=skip,
        limit=size,
        category=category,
        search=search,
        is_hidden=is_hidden,
    )
    data = PageResult(total=total, page=page, size=size, items=posts)
    return PageResponse.success(data=data)


@router.get("/{id}", response_model=BaseResponse[Post])
async def get_post(id: int, session: session_dep):
    """获取文章详情"""
    db_post = await crud_post.get_or_404(session, id=id)
    return BaseResponse.success(data=db_post)


@router.post("/", response_model=BaseResponse[Post])
async def create_post(post_data: PostCreate, session: session_dep):
    """创建文章"""
    db_post = await crud_post.create(session, obj_in=post_data)
    return BaseResponse.success(data=db_post)


@router.put("/{id}", response_model=BaseResponse[Post])
async def update_post(id: int, post_data: PostUpdate, session: session_dep):
    """更新文章"""
    db_post = await crud_post.update(session, id=id, obj_in=post_data)
    return BaseResponse.success(data=db_post)


@router.put("/{id}/hide", response_model=BaseResponse[Post])
async def hide_post(id: int, session: session_dep):
    """隐藏文章"""
    post_data = PostUpdate(is_hidden=True)
    db_post = await crud_post.update(session, id=id, obj_in=post_data)
    return BaseResponse.success(data=db_post)


@router.put("/{id}/show", response_model=BaseResponse[Post])
async def show_post(id: int, session: session_dep):
    """显示文章"""
    post_data = PostUpdate(is_hidden=False)
    db_post = await crud_post.update(session, id=id, obj_in=post_data)
    return BaseResponse.success(data=db_post)


@router.delete("/{id}", response_model=BaseResponse[dict])
async def delete_post(id: int, session: session_dep):
    """删除文章"""
    await crud_post.delete(session, id=id)
    return BaseResponse.success(data={"message": "文章已删除"})


@router.post("/sync", response_model=BaseResponse[list[Post]])
async def sync_posts(session: session_dep):
    """同步文章（从文件系统读取并更新数据库）"""
    synced_posts = await crud_post.sync_from_file_system(session)
    return BaseResponse.success(data=synced_posts)
