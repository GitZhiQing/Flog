from fastapi import FastAPI
from fastapi.openapi.utils import validation_error_response_definition

from app.api.routes import admin_api_router, api_router
from app.core.config import get_settings
from app.core.handlers import register_handlers
from app.core.lifecycle import lifespan
from app.core.middlewares import register_middlewares
from app.schemas.response import BaseResponse


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.NAME,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
        debug=settings.DEBUG,
        # 覆盖参数验证错误的响应定义，确保 API 文档正确
        validation_error_response_definition=validation_error_response_definition,
    )
    register_middlewares(app)  # 注册中间件
    register_handlers(app)  # 注册异常处理器

    @app.get("/", tags=["root"])
    async def read_root():
        # 返回 AppInfo 信息
        app_info = {
            "name": settings.NAME,
            "environment": settings.ENV,
            "host": settings.HOST,
            "port": settings.PORT,
            "api_prefix": settings.API_PREFIX,
            "version": settings.VERSION,
        }
        return BaseResponse.success(data=app_info)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    app.include_router(admin_api_router, prefix=f"{settings.API_PREFIX}/admin")
    return app


app = create_app()
