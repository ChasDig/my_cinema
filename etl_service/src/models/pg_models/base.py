import uuid
from datetime import datetime

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Postgres модель - базовая."""

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    @classmethod
    def model_name(cls) -> str:
        return getattr(cls, "__tablename__", "")


class DatetimeStampedMixin:
    """
    Postgres mixin - время создания, обновления записи.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Дата и время создания объекта",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Дата и время обновления объекта",
    )


class ActiveMixin:
    """Postgres mixin - определяет активность записи."""

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        doc="Флаг - активна или нет запись",
    )
