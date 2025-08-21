from asyncio import Queue
from datetime import datetime
from typing import Mapping, Type

from core.app_logger import logger
from database import pg_session_factory
from models.pg_models import ETLReferenceTimestamp, Movies
from producers.base import BaseRule
from producers.producer_rules import MoviesProduceAndTransformRule
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import ETLComponent, storage
from utils.custom_exception import ProduceException
from utils.etl_type_hints import PGModelsT


class CinemaProducer(ETLComponent):
    """Producer для Cinema Service."""

    def __init__(self) -> None:
        self.pg_session: AsyncSession | None = None

    @property
    def models_by_rules(self) -> Mapping[
        Type[PGModelsT],
        Type[BaseRule[BaseModel]],
    ]:
        return {
            Movies: MoviesProduceAndTransformRule,
        }

    async def run(self) -> None:
        """
        Запуск ETL-компонента - Producer.

        @rtype: None
        @return:
        """
        async with pg_session_factory.context_session() as pg_session:
            self.pg_session = pg_session

            try:
                for model, rule_cls in self.models_by_rules.items():
                    model_name = model.model_name()
                    formatted_q = storage.formatted_queue_by_type(model_name)

                    if formatted_q.full():
                        logger.warning(
                            f"[*] '{model_name}' full, model was not produce"
                        )
                        break

                    etl_ref_ts = await self._etl_ref_timestamp(model_name)
                    ref_timestamp: datetime | None = (
                        etl_ref_ts.reference_timestamp if etl_ref_ts else None
                    )

                    if select_data := await rule_cls().run(
                        pg_session,
                        ref_timestamp,
                    ):
                        await self._put_formatted_data_in_storage(
                            formatted_queue=formatted_q,
                            select_data=select_data,
                        )
                        logger.info(
                            f"[*] '{model_name}' was produce, count: "
                            f"{len(select_data)}"
                        )

                    else:
                        logger.info(f"[*] Not select-data for {model_name}...")

            except ProduceException as ex:
                logger.error(f"[!] Error Produce data for {model_name}: {ex}")

            finally:
                self.pg_session = None

    async def _etl_ref_timestamp(
        self,
        model_name: str,
    ) -> ETLReferenceTimestamp | None:
        """
        Получение референсной модели для ETL-процесса.

        @type model_name: str
        @param model_name:

        @rtype: ETLReferenceTimestamp | None
        @return:
        """
        if self.pg_session is not None:
            stmt = select(
                ETLReferenceTimestamp,
            ).where(
                ETLReferenceTimestamp.model_name == model_name,
            )
            result = await self.pg_session.execute(stmt)

            etl_ref_timestamp: ETLReferenceTimestamp | None = (
                result.scalar_one_or_none()
            )
            return etl_ref_timestamp

        return None

    @staticmethod
    async def _put_formatted_data_in_storage(
        formatted_queue: Queue[BaseModel | None],
        select_data: list[BaseModel],
    ) -> None:
        """
        Отправка готовых для записи данных в Storage по указанной модели.

        @type formatted_q: Queue[BaseModel | None]
        @param formatted_q:
        @type select_data: list[BaseModel]
        @param select_data: Данные из выборки.

        @rtype: None
        @return:
        """
        for row in select_data:
            await formatted_queue.put(row)

        # None - сигнал об окончании данной пачки
        await formatted_queue.put(None)
