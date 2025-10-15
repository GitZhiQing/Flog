import hashlib
from pathlib import Path

import frontmatter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.crud.post import crud_post
from app.schemas.post import PostCreate, PostUpdate

settings = get_settings()


def get_markdown_content_and_metadata(file_path: str | Path) -> dict[str, any]:
    """
    从 Markdown 文件中同时提取内容和元数据

    Args:
        file_path: Markdown 文件的路径

    Returns:
        Dict: 包含 'metadata' 和 'content' 键的字典
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            post = frontmatter.load(f)
        return {
            "metadata": post.metadata,
            "content": post.content,
            "raw": post,  # 原始 frontmatter.Post 对象
        }
    except Exception as e:
        raise Exception(f"解析 Markdown 文件时出错: {str(e)}") from e


def calculate_file_hash(file_path: Path) -> str:
    """
    计算文件的 SHA1 哈希值

    Args:
        file_path: 文件路径

    Returns:
        str: 文件的 SHA1 哈希值
    """
    hash_sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        # 分块读取文件，避免大文件内存问题
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def get_category_from_path(file_path: Path, base_dir: Path) -> str:
    """
    从文件路径中提取分类信息

    Args:
        file_path: 文件路径
        base_dir: 基础目录路径

    Returns:
        str: 分类名称
    """
    # 获取相对于基础目录的路径
    relative_path = file_path.relative_to(base_dir)

    # 如果文件在根目录，分类为空字符串
    if len(relative_path.parts) == 1:
        return ""

    # 否则，使用第一级目录作为分类
    return relative_path.parts[0]


def scan_posts_directory() -> list[dict]:
    """
    扫描文章目录，返回所有 Markdown 文件的信息

    Returns:
        list[dict]: 包含文件信息的字典列表
    """
    posts_info = []

    if not settings.POSTS_DIR.exists():
        return posts_info

    # 递归扫描所有 .md 文件
    for file_path in settings.POSTS_DIR.rglob("*.md"):
        if file_path.is_file():
            try:
                # 计算文件哈希
                file_hash = calculate_file_hash(file_path)

                # 获取文件元数据
                markdown_data = get_markdown_content_and_metadata(file_path)
                metadata = markdown_data["metadata"]

                # 从文件路径获取分类
                category = get_category_from_path(file_path, settings.POSTS_DIR)

                # 获取相对于 DATA_DIR 的路径
                relative_path = file_path.relative_to(settings.DATA_DIR)

                # 获取文件名（不含扩展名）作为 slug
                slug = file_path.stem

                # 获取标题，优先使用元数据中的标题，否则使用文件名
                title = metadata.get("title", slug)

                posts_info.append(
                    {
                        "slug": slug,
                        "title": title,
                        "category": category,
                        "file_path": relative_path.as_posix(),
                        "file_hash": file_hash,
                        "file_path_obj": file_path,  # 保存 Path 对象用于后续操作
                        "metadata": metadata,
                        "content": markdown_data["content"],
                    }
                )
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                continue

    return posts_info


async def sync_posts_to_database(session: AsyncSession) -> dict[str, int]:
    """
    同步文章文件到数据库

    Args:
        session: 数据库会话

    Returns:
        dict[str, int]: 同步结果统计，包含新增、更新、删除的数量
    """
    # 扫描文件系统
    posts_info = scan_posts_directory()

    # 获取数据库中所有文章
    db_posts = await crud_post.get_multi(session)
    db_posts_by_path = {post.file_path: post for post in db_posts}

    # 统计结果
    stats = {
        "added": 0,
        "updated": 0,
        "deleted": 0,
    }

    # 处理文件系统中的文章
    for post_info in posts_info:
        file_path = post_info["file_path"]

        # 检查数据库中是否存在
        if file_path in db_posts_by_path:
            db_post = db_posts_by_path[file_path]
            # 检查文件哈希是否变化
            if db_post.file_hash != post_info["file_hash"]:
                # 更新文章
                post_update = PostUpdate(
                    title=post_info["title"],
                    category=post_info["category"],
                    file_hash=post_info["file_hash"],
                )
                await crud_post.update(
                    session,
                    id=db_post.id,
                    obj_in=post_update,
                )
                stats["updated"] += 1
            # 从字典中移除，表示已处理
            del db_posts_by_path[file_path]
        else:
            # 创建新文章
            post_create = PostCreate(
                slug=post_info["slug"],
                title=post_info["title"],
                category=post_info["category"],
                file_path=post_info["file_path"],
                file_hash=post_info["file_hash"],
            )
            await crud_post.create(
                session,
                obj_in=post_create,
            )
            stats["added"] += 1

    # 删除数据库中存在但文件系统中不存在的文章
    for db_post in db_posts_by_path.values():
        await crud_post.delete(session, id=db_post.id)
        stats["deleted"] += 1

    # 提交事务
    await session.commit()

    return stats
