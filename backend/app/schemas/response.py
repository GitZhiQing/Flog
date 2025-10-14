from typing import Any

import ujson
from pydantic import BaseModel


class BaseResponse[DataType](BaseModel):
    """通用 API 响应模型"""

    code: int = 200
    msg: str = "success"
    data: DataType | None = None

    @staticmethod
    def success(code: int = 200, msg: str = "success", data: Any = None) -> "BaseResponse":
        return BaseResponse(code=code, msg=msg, data=data)

    @staticmethod
    def failed(code: int = 400, msg: str = "failed", data: Any = None) -> "BaseResponse":
        return BaseResponse(code=code, msg=msg, data=data)

    def __repr__(self) -> str:
        # 当直接输出对象时，返回格式化的JSON字符串
        return ujson.dumps(self.model_dump(), indent=2, ensure_ascii=False)


class PageResult[ItemType](BaseModel):
    """分页查询数据结果模型"""

    total: int  # 总记录数
    page: int  # 当前页码
    size: int  # 每页大小
    items: list[ItemType]  # 当前页数据列表


class PageResponse[ItemType](BaseResponse[PageResult[ItemType]]):
    """分页查询数据结果响应模型"""

    pass
