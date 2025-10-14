from fastapi import HTTPException


class BizException(HTTPException):
    """业务错误

    统一覆盖 HTTP Status Code 为 200
    """

    def __init__(self, code: int = 400, msg: str = "Bissiness error"):
        super().__init__(status_code=200)
        self.code = code
        self.msg = msg


class PermissionDeniedException(BizException):
    """权限拒绝异常"""

    def __init__(self, msg: str = "Permission denied"):
        super().__init__(msg=msg, code=403)


class NotFoundException(BizException):
    """未找到"""

    def __init__(self, msg: str = "Item not found"):
        super().__init__(code=404, msg=msg)


class RequestTimeoutException(BizException):
    """请求超时"""

    def __init__(self, msg: str = "Request timeout"):
        super().__init__(code=408, msg=msg)


class ConflictException(BizException):
    """资源冲突"""

    def __init__(self, msg: str = "Resource conflict"):
        super().__init__(code=409, msg=msg)


class PayloadTooLargeException(BizException):
    """请求体过大"""

    def __init__(self, msg: str = "Payload too large"):
        super().__init__(code=413, msg=msg)


class DataValidationException(BizException):
    """数据验证失败"""

    def __init__(self, msg: str = "Data validation failed"):
        super().__init__(code=422, msg=msg)


class InternalServerException(BizException):
    """服务器内部错误"""

    def __init__(self, msg: str = "Internal server error"):
        super().__init__(code=500, msg=msg)
