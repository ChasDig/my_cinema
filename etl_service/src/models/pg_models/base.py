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
    Postgres mixin - время создания, обновления записи и удаления записи
    (мягкое удаление).
    """

    created_at: datetime = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Дата и время создания объекта",
    )
    updated_at: datetime = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Дата и время обновления объекта",
    )
    deleted_at: datetime = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Дата и время мягкого удаления объекта",
    )


class BaseDatetimeStamped(Base, DatetimeStampedMixin):
    """Postgres модель - Base + DatetimeStampedMixin."""

    pass
