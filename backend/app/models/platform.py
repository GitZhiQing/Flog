from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Platform(Base):
    """平台配置模型"""

    __tablename__ = "platform"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Flog", comment="网站标题"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="网站描述")
    footer: Mapped[str] = mapped_column(Text, nullable=True, comment="页脚信息")

    def __repr__(self):
        return f"<Platform(id={self.id}, title='{self.title}')>"
