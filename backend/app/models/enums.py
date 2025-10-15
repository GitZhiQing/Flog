from enum import StrEnum


class CommentStatusEnum(StrEnum):
    """评论状态"""

    HIDE = "hide"
    SHOW = "show"


class PostStatusEnum(StrEnum):
    """博文状态"""

    HIDE = "hide"
    SHOW = "show"
