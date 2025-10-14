import fastapi_cdn_host
from fastapi import FastAPI
from fastapi.openapi.utils import validation_error_response_definition
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
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
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    fastapi_cdn_host.patch_docs(app)
    return app


app = create_app()
