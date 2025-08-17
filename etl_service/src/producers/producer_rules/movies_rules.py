from datetime import datetime
from typing import Any, Generator, Sequence

from core.app_config import config
from models.pg_models import (
    Genres,
    Movies,
    MoviesGenresAssociation,
    MoviesPersonsAssociation,
    Persons,
    PersonsAssociationEnum,
)
from models.pydantic_models import (
    GenresProducerModel,
    MoviesProducerModel,
    PersonsProducerModel,
)
from producers.base import BaseRule
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.selectable import Select


class MoviesProduceAndTransformRule(BaseRule[MoviesProducerModel]):
    """Правило для выборки данных и форматированию для ES по Movies."""

    @staticmethod
    def _get_persons_gen(movie: Movies) -> Generator[Persons, Any, None]:
        return (mpa.person for mpa in movie.movie_person_ass)

    @staticmethod
    def _get_genres_gen(movie: Movies) -> Generator[Genres, Any, None]:
        return (mga.genre for mga in movie.movie_genre_ass)

    async def run(
        self,
        pg_session: AsyncSession,
        ref_timestamp: datetime | None = None,
    ) -> list[MoviesProducerModel]:
        """
        Выборка данных по Movies и связанным сущностям: Persons, Genres.

        @type pg_session: AsyncSession
        @param pg_session:
        @type ref_timestamp: datetime | None
        @param ref_timestamp:

        @rtype: list[MoviesProducerModel]
        @return: movies_pm
        """
        stmt = self._get_movie_stmt()

        if ref_timestamp:
            stmt = stmt.where(
                Movies.updated_at >= ref_timestamp,
            )

        result = await pg_session.execute(stmt)
        movies: Sequence[Movies] = result.scalars().all()

        movies_pm = [self._create_movie_pm(movie=movie) for movie in movies]
        return movies_pm

    @staticmethod
    def _get_movie_stmt() -> Select[tuple[Movies]]:
        return (
            select(
                Movies,
            )
            .join(
                MoviesPersonsAssociation,
                Movies.id == MoviesPersonsAssociation.movie_id,
            )
            .join(
                MoviesGenresAssociation,
                Movies.id == MoviesGenresAssociation.movie_id,
            )
            .join(
                Persons,
                MoviesPersonsAssociation.person_id == Persons.id,
            )
            .join(
                Genres,
                MoviesGenresAssociation.genre_id == Genres.id,
            )
            .where(
                Movies.is_active.is_(True),
                MoviesPersonsAssociation.is_active.is_(True),
                MoviesGenresAssociation.is_active.is_(True),
                Persons.is_active.is_(True),
                Genres.is_active.is_(True),
            )
            .options(
                selectinload(
                    Movies.movie_person_ass,
                ).selectinload(
                    MoviesPersonsAssociation.person,
                ),
                selectinload(
                    Movies.movie_genre_ass,
                ).selectinload(
                    MoviesGenresAssociation.genre,
                ),
            )
            .order_by(
                Movies.updated_at.asc(),
            )
            .limit(
                config.etl_select_limit,
            )
        )

    def _create_movie_pm(self, movie: Movies) -> MoviesProducerModel:
        return MoviesProducerModel(
            id_=movie.id,
            name_ru=movie.name_ru,
            name_eng=movie.name_eng,
            release_date=movie.release_date,
            age_rating=movie.age_rating,
            rating=movie.rating,
            actors_name=self._get_persons_name_by_association(
                persons=self._get_persons_gen(movie),
                association=PersonsAssociationEnum.actor.name,
            ),
            producers_name=self._get_persons_name_by_association(
                persons=self._get_persons_gen(movie),
                association=PersonsAssociationEnum.producer.name,
            ),
            directors_name=self._get_persons_name_by_association(
                persons=self._get_persons_gen(movie),
                association=PersonsAssociationEnum.director.name,
            ),
            persons=[
                self._create_person_pm(p) for p in self._get_persons_gen(movie)
            ],  # noqa: E501
            genres_title=[
                genre.title for genre in self._get_genres_gen(movie)
            ],  # noqa: E501
            genres=[
                self._create_genre_pm(g) for g in self._get_genres_gen(movie)
            ],  # noqa: E501
            updated_at=movie.updated_at,
        )

    @staticmethod
    def _get_persons_name_by_association(
        association: str,
        persons: Generator[Persons, Any, None],
    ) -> list[str]:
        return [
            person.get_person_name()
            for person in persons
            if person.type_employment == association
        ]

    @staticmethod
    def _create_person_pm(person: Persons) -> PersonsProducerModel:
        return PersonsProducerModel(
            id_=person.id,
            first_name=person.first_name,
            second_name=person.second_name,
            last_name=person.last_name,
            birthday=person.birthday,
            place_of_birth=person.place_of_birth,
        )

    @staticmethod
    def _create_genre_pm(genre: Genres) -> GenresProducerModel:
        return GenresProducerModel(
            id_=genre.id,
            title=genre.title,
            age_rating=genre.age_rating,
            description=genre.description,
        )
