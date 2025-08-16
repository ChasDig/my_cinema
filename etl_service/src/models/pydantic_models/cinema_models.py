from datetime import date, datetime

from pydantic import BaseModel, Field


class PersonsProducerModel(BaseModel):
    """Информация по Person (используется для Producer)."""

    first_name: str
    last_name: str
    birthday: date

    second_name: str | None = Field(default=None)
    place_of_birth: str | None = Field(default=None)


class GenresProducerModel(BaseModel):
    """Информация по Genre (используется для Producer)."""

    title: str
    age_rating: int
    description: str | None = Field(default=None)


class MoviesProducerModel(BaseModel):
    """
    Общая информация по Movie (включая связанные сущности, используется для
    Producer).
    """

    # Meta:
    updated_at: datetime

    # Movies
    name_ru: str
    release_date: date
    age_rating: int
    name_eng: str | None = Field(default=None)
    rating: float = Field(default=0.0)

    # Persons
    actors_name: list[str] = Field(default_factory=list)
    producers_name: list[str] = Field(default_factory=list)
    directors_name: list[str] = Field(default_factory=list)

    persons: list[PersonsProducerModel] = Field(default_factory=list)

    # Genres
    genres_title: list[str] = Field(default_factory=list)

    genres: list[GenresProducerModel] = Field(default_factory=list)
