import hashlib
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def get_file_hash(file_path: str) -> str:
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 分块读取文件，避免大文件占用过多内存
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def parse_front_matter(content: str) -> tuple[dict[str, str], str]:
    """解析Markdown文件的前置元数据"""
    lines = content.split("\n")
    front_matter = {}
    content_start = 0

    # 检查是否有前置元数据
    if len(lines) > 2 and lines[0].strip() == "---":
        # 找到前置元数据的结束位置
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                content_start = i + 1
                break

            # 解析键值对
            if ":" in line:
                key, value = line.split(":", 1)
                front_matter[key.strip()] = value.strip()

    # 返回前置元数据和正文内容
    body_content = "\n".join(lines[content_start:])
    return front_matter, body_content


def scan_posts_dir() -> list[dict[str, str]]:
    """扫描文章目录，返回所有文章的元数据"""
    posts_dir = Path(settings.POSTS_DIR)
    posts = []

    if not posts_dir.exists():
        return posts

    for file_path in posts_dir.glob("**/*.md"):
        try:
            # 计算相对路径和哈希值
            rel_path = str(file_path.relative_to(posts_dir))
            file_hash = get_file_hash(str(file_path))

            # 读取并解析文件内容
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            front_matter, body_content = parse_front_matter(content)

            # 从前置元数据中提取标题，如果没有则使用文件名
            title = front_matter.get("title", file_path.stem)

            # 使用文件名（不含扩展名）作为 slug
            slug = file_path.stem

            # 获取文件相对 POSTS_DIR 的目录作为分类，可为空
            rel_dir = str(file_path.parent.relative_to(posts_dir))
            category = "" if rel_dir == "." else rel_dir.replace("\\", "/")

            # 从前置元数据中获取是否隐藏标记
            is_hidden = front_matter.get("hidden", "false").lower() == "true"

            posts.append(
                {
                    "file_path": rel_path,
                    "file_hash": file_hash,
                    "title": title,
                    "slug": slug,
                    "category": category,
                    "content": body_content,
                    "is_hidden": is_hidden,
                }
            )
        except Exception as e:
            # 记录错误但继续处理其他文件
            print(f"处理文件 {file_path} 时出错: {e}")

    return posts
