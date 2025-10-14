from app.crud.base import CRUDBase
from app.crud.comment import crud_comment
from app.crud.platform import crud_platform
from app.crud.post import crud_post

__all__ = ["CRUDBase", "crud_post", "crud_comment", "crud_platform"]
