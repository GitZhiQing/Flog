from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings

settings = get_settings()


def register_middlewares(app: FastAPI):
    """注册中间件"""
    # CORS：允许指定前端地址跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_URL,  # 允许的前端地址列表
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有请求头
        allow_credentials=True,  # 允许携带 Cookie 等凭证
    )
    # GZIP：对大于 1024 字节(1KB)的响应进行压缩，提升传输效率
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1024,
    )
    # Trust Hosts：只允许配置中的主机名访问，防止 Host 头攻击
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
