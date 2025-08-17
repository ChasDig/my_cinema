from datetime import datetime
from typing import Mapping, Type

from core.app_logger import logger
from database import pg_session_factory
from loaders.base import BaseLoad
from loaders.loader_rules import MoviesLoaderRule
from models.pg_models import ETLReferenceTimestamp, Movies
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from utils import storage
from utils.custom_exception import LoadException
from utils.etl_type_hints import PGModelsT


class CinemaLoader:
    """Loader для Cinema Service."""

    @property
    def models_by_rules(self) -> Mapping[
        Type[PGModelsT],
        Type[BaseLoad[BaseModel]],
    ]:
        return {
            Movies: MoviesLoaderRule,
        }

    async def run(self) -> None:
        """
        Запуск ETL-компонента - Loader.

        @rtype: None
        @return:
        """
        for model, rule_cls in self.models_by_rules.items():
            etl_ref_timestamp = list()
            rule_cls_init = rule_cls()
            model_name = model.model_name()
            queue_by_type = storage.formatted_queue_by_type(type_=model_name)

            while True:
                formatted_data = await queue_by_type.get()

                try:
                    if formatted_data is None:
                        break

                    await rule_cls_init.run(formatted_data=formatted_data)
                    etl_ref_timestamp.append(formatted_data.updated_at)

                except LoadException as ex:
                    logger.error(
                        f"[!] Error Load data for {model_name}"
                        f"(ID={getattr(formatted_data, 'id_', '-')}): {ex}"
                    )

                finally:
                    queue_by_type.task_done()

            if etl_ref_timestamp:
                await self._update_or_create_etl_ref_timestamp(
                    model_name=model_name,
                    etl_ref_timestamp=max(etl_ref_timestamp),
                )

            await queue_by_type.join()
            logger.info(f"[*] {model_name} was load...")

    @staticmethod
    async def _update_or_create_etl_ref_timestamp(
        model_name: str,
        etl_ref_timestamp: datetime,
    ) -> None:
        """
        Обновление/создание референсной модели для ETL-процесса.

        @type model_name: str
        @param model_name:
        @type etl_ref_timestamp: datetime
        @param etl_ref_timestamp: Данные для обновляемого/создаваемого
        параметра.

        @rtype: None
        @return:
        """
        async with pg_session_factory.context_session() as pg_session:
            insert_stmt = pg_insert(
                ETLReferenceTimestamp,
            ).values(
                model_name=model_name,
                reference_timestamp=etl_ref_timestamp,
            )
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=["model_name"],
                set_={"reference_timestamp": etl_ref_timestamp},
            )

            try:
                await pg_session.execute(upsert_stmt)
                await pg_session.commit()

                logger.info(
                    "[*] ETL reference_timestamp was update/insert for "
                    f"'{model_name}': {etl_ref_timestamp}"
                )

            except SQLAlchemyError as ex:
                logger.error(
                    "[!] Error update/insert reference_timestamp for "
                    f"'{model_name}': {ex}"
                )
                await pg_session.rollback()
