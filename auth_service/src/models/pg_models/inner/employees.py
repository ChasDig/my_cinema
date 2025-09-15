from models.pg_models.base import Base, DatetimeStampedMixin, Schemas
from sqlalchemy.orm import Mapped, mapped_column


class Employees(Base, DatetimeStampedMixin):
    """Postgres модель - Сотрудники."""

    __tablename__ = "employees"
    __table_args__ = {"schema": Schemas.employees.name}

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email_enc: Mapped[str] = mapped_column(nullable=False)
    email_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Employer '{self.name}'(ID: '{self.id}')"
