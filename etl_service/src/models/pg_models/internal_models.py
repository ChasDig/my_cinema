from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .schemas import Schemas


class ETLReferenceTimestamp(Base):
    """
    Postgres модель - Модель хранит поле, по которому ETL-сервис сортирует
    объекты. Служит в качестве референсной точки для выборки данных
    в других операциях.
    """

    __tablename__ = "etl_reference_timestamp"
    __table_args__ = {"schema": Schemas.internal.name}

    model_name: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
        doc="Наименование таблицы в БД",
    )
    reference_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Референсная точка выборки",
    )

    def __repr__(self) -> str:
        return f"ReferenceTimestamp for '{self.model_name}'"
