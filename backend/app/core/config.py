import os
from functools import lru_cache
from pathlib import Path
import sys
from typing import Literal

from loguru import logger
from pydantic import ValidationError, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # 应用
    NAME: str = "Seek2Game API"
    ENV: Literal["development", "testing", "production"] = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    API_PREFIX: str = "/api"
    SECRET_KEY: str  # !必须提供
    VERSION: str = "0.1.0"

    @computed_field
    @property
    def DEBUG(self) -> bool:
        # 开发模式下启动调试
        return True if self.ENV == "development" else False

    @computed_field
    @property
    def WORKERS(self) -> int:
        # 启动进程数
        return 4 if self.ENV == "production" else 1

    @computed_field
    @property
    def ALLOWED_HOSTS(self) -> list[str]:
        # 允许的主机列表 (用于 Trusted Host 中间件)
        return list({self.HOST, "localhost", "127.0.0.1"})

    # 前端 URL (用于 CORS 中间件)
    FRONTEND_URL: str = "http://localhost:5173"

    # 博主信息
    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # 文件路径配置
    APP_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = APP_DIR / "data"
    ASSETS_DIR: Path = DATA_DIR / "assets"
    POSTS_DIR: Path = DATA_DIR / "posts"
    PAGES_DIR: Path = DATA_DIR / "pages"
    DB_PATH: Path = DATA_DIR / "data.db"

    # 数据库配置
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        SQLITE_PREFIX = (
            "sqlite+aiosqlite:///" if sys.platform.startswith("win") else "sqlite:////"
        )
        return SQLITE_PREFIX + str(self.DB_PATH)


class ProductionSettings(Settings):
    """生产环境配置"""

    ENV: Literal["production"] = "production"


class DevelopmentSettings(Settings):
    """开发环境配置"""

    ENV: Literal["development"] = "development"


@lru_cache
def get_settings() -> Settings:
    """获取配置实例"""
    try:
        app_env = os.getenv("ENV", "development")
        if app_env not in ["production", "testing", "development"]:
            logger.error(f"无效的环境变量: '{app_env}'")
            exit(1)
        logger.info(f"当前环境: {app_env}")
        if app_env == "production":
            return ProductionSettings()
        else:
            return DevelopmentSettings()
    except ValidationError as e:
        logger.error(f"配置导入错误: {e}")
        missing_vars = []  # 缺失变量
        invalid_vars = []  # 无效变量
        for error in e.errors():
            field_name = error.get("loc", [""])[0] if error.get("loc") else ""
            error_type = error.get("type", "")
            if error_type == "missing":
                missing_vars.append(field_name)
            else:
                invalid_vars.append(f"{field_name}: {error.get('msg', '验证失败')}")
        if missing_vars:
            logger.error(
                f"[!] 缺少必需环境变量 [{', '.join(missing_vars)}]，请检查 .env 文件配置"
            )
        if invalid_vars:
            logger.error(f"[!] 环境变量值错误: {', '.join(invalid_vars)}")
        exit(1)
