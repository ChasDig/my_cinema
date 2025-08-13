from datetime import datetime

from core import logger
from database import pg_session_factory
from models.pg_models import ETLReferenceTimestamp, Movies
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils import ETLComponent, storage
from utils.custom_exception import ProduceException

from .prducer_type_hints import ModelsByRuleT, PGModelsT, ProduceRuleResultT
from .producer_rules import MoviesRules


class CinemaProducer(ETLComponent):
    """Producer для Cinema Service."""

    def __init__(self) -> None:
        self.pg_session: AsyncSession | None = None

    @property
    def models_by_rules(self) -> ModelsByRuleT:
        return {
            Movies: MoviesRules.produce_rule,
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
                for model, rules in self.models_by_rules.items():
                    model_name = model.model_name()

                    etl_ref_ts = await self._etl_ref_timestamp(model_name)
                    ref_timestamp: datetime | None = (
                        etl_ref_ts.reference_timestamp if etl_ref_ts else None
                    )

                    if select_data := await rules(pg_session, ref_timestamp):
                        await self._put_raw_data_in_storage(
                            model=model,
                            select_data=select_data,
                        )
                        new_etl_ref_timestamp = (
                            await self._update_or_create_etl_ref_timestamp(
                                model_name,
                                etl_ref_ts,
                                select_data[-1].updated_at,
                            )
                        )
                        self._log_about_produce(
                            model,
                            new_etl_ref_timestamp,
                            len(select_data),
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
    async def _put_raw_data_in_storage(
        model: PGModelsT,
        select_data: ProduceRuleResultT,
    ) -> None:
        """
        Отправка сырых данных в Storage по указанной модели.

        @type model: PGModelsT
        @param model:
        @type select_data: ProduceRuleResultT
        @param select_data: Данные из выборки.

        @rtype: None
        @return:
        """
        type_ = model.model_name()
        await storage.raw_queue_by_type(type_=type_).put(select_data)

    async def _update_or_create_etl_ref_timestamp(
        self,
        model_name: str,
        old_etl_ref_timestamp: ETLReferenceTimestamp | None,
        new_ref_timestamp: datetime,
    ) -> ETLReferenceTimestamp | None:
        """
        Обновление/создание референсной модели для ETL-процесса.

        @type model_name: str
        @param model_name:
        @type old_etl_ref_timestamp: ETLReferenceTimestamp
        @param old_etl_ref_timestamp: Обновляемая сущность.
        @type new_ref_timestamp: datetime
        @param new_ref_timestamp: Данные для обновляемого параметра.

        @rtype updated_etl_ref_timestamp: ETLReferenceTimestamp | None
        @return updated_etl_ref_timestamp:
        """
        if self.pg_session is not None:
            if old_etl_ref_timestamp:
                stmt = (
                    update(
                        ETLReferenceTimestamp,
                    )
                    .where(
                        ETLReferenceTimestamp.model_name == model_name,
                    )
                    .values(
                        reference_timestamp=new_ref_timestamp,
                    )
                    .returning(ETLReferenceTimestamp)
                )

                result = await self.pg_session.execute(stmt)
                etl_ref_ts: ETLReferenceTimestamp = result.scalar_one_or_none()
                await self.pg_session.commit()

            else:
                etl_ref_ts = ETLReferenceTimestamp(
                    model_name=model_name,
                    reference_timestamp=new_ref_timestamp,
                )

                self.pg_session.add(etl_ref_ts)
                await self.pg_session.commit()
                await self.pg_session.refresh(etl_ref_ts)

            return etl_ref_ts

        return None

    @staticmethod
    def _log_about_produce(
        model: PGModelsT,
        etl_ref_timestamp: ETLReferenceTimestamp | None,
        count_: int,
    ) -> None:
        new_ref_timestamp = (
            etl_ref_timestamp.reference_timestamp if etl_ref_timestamp else "-"
        )

        logger.info(
            f"[*] {model.model_name()} was produce, "
            f"new_ref_timestamp: {new_ref_timestamp}, count: {count_}"
        )
