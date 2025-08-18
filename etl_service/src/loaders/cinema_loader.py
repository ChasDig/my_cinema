from datetime import datetime
from typing import Mapping, Type

from core.app_logger import logger
from database import pg_session_factory
from database.es_client import ESContextManager, es_indexes_mapping_checker
from models.pg_models import ETLReferenceTimestamp, Movies
from models.pydantic_models import MoviesProducerModel
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from utils import storage
from utils.custom_exception import LoadException
from utils.etl_type_hints import PGModelsT


class CinemaLoader:
    """Loader для Cinema Service."""

    @property
    def pg_models_by_es_models(
        self,
    ) -> Mapping[Type[PGModelsT], Type[BaseModel]]:
        return {
            Movies: MoviesProducerModel,
        }

    @es_indexes_mapping_checker
    async def run(self) -> None:
        """
        Запуск ETL-компонента - Loader.

        @rtype: None
        @return:
        """
        async with ESContextManager() as es_client:  # type: ignore
            for pg_model, es_model in self.pg_models_by_es_models.items():
                etl_ref_timestamp = list()
                model_name = pg_model.model_name()
                queue_by_type = storage.formatted_queue_by_type(model_name)

                while True:
                    formatted_data = await queue_by_type.get()

                    try:
                        if formatted_data is None:
                            break

                        fd_id = getattr(formatted_data, "id_", None)
                        await es_client.insert_document(
                            index_=model_name,
                            document=formatted_data.dict(),
                            id_=fd_id,
                        )
                        etl_ref_timestamp.append(formatted_data.updated_at)

                    except LoadException as ex:
                        logger.error(
                            f"[!] Error Load data for '{model_name}'"
                            f"(ID={fd_id}): {ex}"
                        )

                    finally:
                        queue_by_type.task_done()

                if etl_ref_timestamp:
                    await self._update_or_create_etl_ref_timestamp(
                        model_name=model_name,
                        etl_ref_timestamp=max(etl_ref_timestamp),
                    )

                await queue_by_type.join()
                logger.info(f"[*] '{model_name}' was load...")

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
