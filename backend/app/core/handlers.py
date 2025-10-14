from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BizException
from app.schemas.response import BaseResponse


def register_handlers(app: FastAPI):
    """注册异常处理器

    将所有异常统一响应格式，OAuth 2.0错误除外
    """

    @app.exception_handler(BizException)
    async def biz_exception_handler(
        request: Request,
        exc: BizException,
    ):
        """业务异常处理器

        捕获所有业务异常，并转换为统一的响应格式
        """
        response_content = BaseResponse.failed(code=exc.code, msg=exc.msg).model_dump()
        # 如果异常包含 headers（认证接口），则添加到响应中
        if hasattr(exc, "headers") and exc.headers:
            return JSONResponse(status_code=200, content=response_content, headers=exc.headers)
        return JSONResponse(status_code=200, content=response_content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,  # noqa: ARG001
        exc: RequestValidationError,
    ):
        """参数验证异常处理

        捕获所有参数验证异常，并转换为统一的响应格式
        """
        # FastAPI 生成的 OpenAPI 文档中，参数验证错误定义为 422 状态码且无法更改
        # 需要注意此处实际统一返回 200 状态码
        return JSONResponse(
            status_code=200,
            content=BaseResponse.failed(
                code=422, msg="Request validation error", data=exc.errors()
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,  # noqa: ARG001
        exc: StarletteHTTPException,
    ):
        """HTTP 异常处理

        捕获所有 HTTP 异常，并转换为统一的响应格式
        """
        return JSONResponse(
            status_code=200,
            content=BaseResponse.failed(code=exc.status_code, msg=exc.detail).model_dump(),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(
        request: Request,  # noqa: ARG001
        exc: Exception,
    ):
        """其他异常处理

        捕获所有内部异常，并转换为统一的响应格式
        """
        logger.error(f"服务器内部错误: {exc}")
        return JSONResponse(
            status_code=200,
            content=BaseResponse.failed(code=500, msg="Internal server error").model_dump(),
        )
