"""数据库表基类"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}  # 覆盖默认命名规则


class Base(DeclarativeBase):
    """建所有ORM模型基类"""

    metadata = MetaData(naming_convention=convention)


class IdMixin:
    """Mixin ID字段"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class TimestampMixin:
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    update_tiem: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
