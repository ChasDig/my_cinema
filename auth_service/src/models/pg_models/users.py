from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, DatetimeStampedMixin, Schemas


class Users(Base, DatetimeStampedMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": Schemas.users.name}

    nickname: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"UserNickname '{self.nickname}'(ID: '{self.id}')"
