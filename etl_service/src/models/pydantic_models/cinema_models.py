from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PersonsProducerModel(BaseModel):
    """Информация по Person (используется для Producer)."""

    id_: UUID | str
    full_name: str
    birthday: date
    place_of_birth: str = Field(default="")


class GenresProducerModel(BaseModel):
    """Информация по Genre (используется для Producer)."""

    id_: UUID | str
    title: str
    age_rating: int
    description: str = Field(default="")


class MoviesProducerModel(BaseModel):
    """
    Общая информация по Movie (включая связанные сущности, используется для
    Producer).
    """

    # Meta:
    updated_at: datetime
    created_at: datetime

    # Movies
    id_: UUID | str
    name_ru: str
    release_date: date
    age_rating: int
    name_eng: str = Field(default="")
    rating: float = Field(default=0.0)
    description: str = Field(default="")

    # Persons
    actors_name: str
    producers_name: str
    directors_name: str

    actors: list[PersonsProducerModel] = Field(default_factory=list)
    producers: list[PersonsProducerModel] = Field(default_factory=list)
    directors: list[PersonsProducerModel] = Field(default_factory=list)

    # Genres
    genres_title: str

    genres: list[GenresProducerModel] = Field(default_factory=list)
