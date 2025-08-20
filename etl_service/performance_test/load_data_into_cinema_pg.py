import asyncio
import random
import string
import uuid
from datetime import datetime, timezone
from typing import Callable, Generator, TypeAlias

import psycopg
from config import config
from logger_ import logger
from psycopg import AsyncConnection

InsertDataT: TypeAlias = list[tuple[str | int | float | bool, ...]]


class DataForTestsGen:
    """Класс для генерации тестовых данных в ETL-процессе."""

    @property
    def models_by_schemas(self) -> dict[str, tuple[str, ...]]:
        return {
            "movies": (
                "movies",
                "persons",
                "genres",
                "movies_persons_association",
                "movies_genres_association",
            )
        }

    async def gen(self) -> None:
        async with await psycopg.AsyncConnection.connect(
            config.pg_url_connection
        ) as pg_connect:
            for schema, models in self.models_by_schemas.items():
                for model in models:
                    if insert_chain := self._get_insert_chain(schema, model):
                        try:
                            gen_insert_data = self._gen_insert_data(
                                schema=schema,
                                model=model,
                            )
                            await self._execute_insert(
                                pg_connect=pg_connect,
                                gen_insert_data=gen_insert_data,
                                insert_chain=insert_chain,
                            )

                        except Exception as ex:
                            logger.error(f"[!] Error: {ex}")

                    await pg_connect.commit()

    @staticmethod
    def _get_insert_chain(schema: str, model: str) -> str | None:
        insert_chains = {
            "movies": {
                "movies": (
                    f"INSERT INTO {schema}.{model} "
                    f"(id, name_ru, name_eng, release_date, rating, "
                    f"age_rating, description, is_active) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                ),
            },
        }

        return insert_chains.get(schema, {}).get(model)

    @staticmethod
    def _gen_insert_data(
        schema: str,
        model: str,
    ) -> Generator[InsertDataT, None, None]:
        strategies_gen_data = {
            "movies": StrategyGenDataByMoviesSchema,
        }

        strategy = strategies_gen_data[schema]
        return strategy.execute(model)

    @staticmethod
    async def _execute_insert(
        pg_connect: AsyncConnection,
        gen_insert_data: Generator[InsertDataT, None, None],
        insert_chain: str,
    ) -> None:
        async with pg_connect.cursor() as cursor:
            for insert_data in gen_insert_data:
                await cursor.executemany(insert_chain, insert_data)


class StrategyGenDataByMoviesSchema:
    """Стратегия по генерации данных для схемы 'movies'."""

    CONCAT = 2
    LENGTH_ELEMENTS = 10

    @staticmethod
    def _ascii_gen(length_: int) -> Generator[str, None, None]:
        return (random.choice(string.ascii_letters) for _ in range(length_))

    @classmethod
    def _get_template_data(
        cls,
        model: str,
    ) -> Callable[[int], InsertDataT] | None:
        templates_data = {
            "movies": cls._gen_movies_data,
        }

        return templates_data.get(model)

    @classmethod
    def execute(cls, model: str) -> Generator[InsertDataT, None, None]:
        count_generated_data = 0
        count_gen_for_data, chunk = config.count_gen_data, config.size_chunk

        if data_template := cls._get_template_data(model):
            while count_generated_data < count_gen_for_data:
                yield data_template(chunk)

                count_generated_data += chunk

    @classmethod
    def _gen_movies_data(cls, chunk: int) -> InsertDataT:
        return [
            (
                str(uuid.uuid4()),
                "".join(cls._ascii_gen(cls.LENGTH_ELEMENTS)),
                "".join(cls._ascii_gen(cls.LENGTH_ELEMENTS)),
                datetime.now(timezone.utc).date().isoformat(),
                round(random.uniform(1, 10), 2),
                random.randint(0, 18),
                "".join(cls._ascii_gen(cls.LENGTH_ELEMENTS * cls.CONCAT)),
                True,
            )
            for _ in range(chunk)
        ]


if __name__ == "__main__":
    asyncio.run(DataForTestsGen().gen())
