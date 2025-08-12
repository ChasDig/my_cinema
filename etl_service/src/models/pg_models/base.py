import uuid
from datetime import datetime

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Postgres модель - базовая."""

    id: Mapped[uuid.UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    @classmethod
    def model_name(cls) -> str | None:
        return getattr(cls, "__tablename__", None)


class DatetimeStampedMixin:
    """
    Postgres mixin - время создания, обновления записи и удаления записи
    (мягкое удаление).
    """

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        doc="Дата и время создания объекта",
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        doc="Дата и время обновления объекта",
    )
    deleted_at: Mapped[datetime] = mapped_column(
        nullable=True,
        doc="Дата и время мягкого удаления объекта",
    )
