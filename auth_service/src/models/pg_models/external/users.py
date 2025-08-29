from models.pg_models.base import Base, DatetimeStampedMixin, Schemas
from sqlalchemy.orm import Mapped, mapped_column


class Users(Base, DatetimeStampedMixin):
    """Postgres модель - Пользователи."""

    __tablename__ = "users"
    __table_args__ = {"schema": Schemas.users.name}

    nickname: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email_enc: Mapped[str] = mapped_column(nullable=False)
    email_hash: Mapped[str] = mapped_column(nullable=False, unique=True)

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"UserNickname '{self.nickname}'(ID: '{self.id}')"
