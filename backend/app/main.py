import json

from fastapi import FastAPI

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
    )
    register_middlewares(app)  # 注册中间件
    register_handlers(app)  # 注册异常处理器

    @app.get("/", tags=["root"])
    async def read_root():
        # 读取平台配置
        try:
            with open(settings.DATA_DIR / "config.json", encoding="utf-8") as f:
                platform_config = json.load(f)
        except FileNotFoundError:
            platform_config = {"error": "Platform configuration file not found"}
        except json.JSONDecodeError:
            platform_config = {"error": "Invalid platform configuration format"}

        # 构建 API 信息
        api_info = {
            "name": settings.NAME,
            "environment": settings.ENV,
            "host": settings.HOST,
            "port": settings.PORT,
            "api_prefix": settings.API_PREFIX,
            "version": settings.VERSION,
        }

        # 组合响应数据
        data = {"api": api_info, "platform": platform_config}

        return BaseResponse.success(data=data)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
