from pydantic import BaseModel, Field


class PlatformBase(BaseModel):
    """平台配置基础模型"""

    title: str = Field(..., description="网站标题")
    description: str | None = Field(None, description="网站描述")
    footer: str | None = Field(None, description="页脚信息")


class PlatformCreate(PlatformBase):
    """创建平台配置模型"""

    pass


class PlatformUpdate(BaseModel):
    """更新平台配置模型"""

    title: str | None = Field(None, description="网站标题")
    description: str | None = Field(None, description="网站描述")
    footer: str | None = Field(None, description="页脚信息")


class PlatformInDB(PlatformBase):
    """数据库中的平台配置模型"""

    id: int

    class Config:
        from_attributes = True


class Platform(PlatformInDB):
    """平台配置响应模型"""

    pass


class PlatformInfo(BaseModel):
    """平台信息模型"""

    title: str
    description: str | None
    footer: str | None

    class Config:
        from_attributes = True
