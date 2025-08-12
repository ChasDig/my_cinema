from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, DatetimeStampedMixin
from .pg_enums import person_type_enum
from .schemas import Schemas


class Movies(Base, DatetimeStampedMixin):
    """Postgres модель - Фильмы."""

    __tablename__ = "movies"
    __table_args__ = {"schema": Schemas.movies.name}

    name_ru: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
        doc="Наименование поля (ru)",
    )
    name_eng: Mapped[str] = mapped_column(
        nullable=True,
        unique=True,
        doc="Наименование поля (eng)",
    )
    release_date: Mapped[date] = mapped_column(
        nullable=False,
        doc="Дата релиза",
    )
    rating: Mapped[float] = mapped_column(default=0.0, doc="Рейтинг")
    age_rating: Mapped[int] = mapped_column(
        nullable=False,
        doc="Возрастной рейтинг (ограничение)",
    )

    def __repr__(self) -> str:
        return (
            f"{self.__tablename__} "
            f"'{self.name_eng if self.name_eng else self.name_ru}'"
        )


class Persons(Base, DatetimeStampedMixin):
    """Postgres модель - Персоны."""

    __tablename__ = "persons"
    __table_args__ = {"schema": Schemas.movies.name}

    first_name: Mapped[str] = mapped_column(nullable=False, doc="Имя")
    second_name: Mapped[str] = mapped_column(nullable=True, doc="Отчество")
    last_name: Mapped[str] = mapped_column(nullable=False, doc="Фамилия")
    birthday: Mapped[date] = mapped_column(nullable=False, doc="Дата рождения")
    place_of_birth: Mapped[str] = mapped_column(
        nullable=True,
        doc="Место рождения",
    )
    type_employment: Mapped[str] = mapped_column(
        person_type_enum,
        nullable=False,
        doc="Тип занятости (характер деятельности)",
    )

    def __repr__(self) -> str:
        return (
            f"{self.__tablename__} {self.first_name} {self.last_name} "
            f"({self.type_employment})"
        )


class Genres(Base, DatetimeStampedMixin):
    """Postgres модель - Персоны."""

    __tablename__ = "genres"
    __table_args__ = {"schema": Schemas.movies.name}

    title: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
        doc="Название",
    )
    description: Mapped[str] = mapped_column(nullable=True, doc="Описание")
    age_rating: Mapped[int] = mapped_column(
        nullable=False,
        doc="Возрастной рейтинг (ограничение)",
    )

    def __repr__(self) -> str:
        return f"{self.__tablename__} '{self.title}'"
