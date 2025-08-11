import enum
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
    """Postgres mixin - время создания и обновления записи."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Schemas(enum.Enum):
    """Postgres схемы."""

    users = "users"
