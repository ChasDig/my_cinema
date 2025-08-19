import json
from functools import wraps
from json import JSONDecodeError
from typing import Any, Awaitable, Callable

from core.app_config import db_config
from core.app_logger import logger
from elasticsearch import AsyncElasticsearch


class AsyncESClient:
    """Async-клиент Elasticsearch."""

    def __init__(self) -> None:
        self._client: AsyncElasticsearch = AsyncElasticsearch(
            db_config.elastic_url,
            basic_auth=(db_config.elastic_name, db_config.elastic_password),
            max_retries=0,
            retry_on_timeout=False,
        )

    async def close_(self) -> None:
        await self._client.close()

    async def create_index_with_ignore(
        self,
        index_: str,
        body: dict[str, Any] | None = None,
    ) -> None:
        """
        Создание индекса к ES.

        @type index_: str
        @param index_:
        @type body: dict[str, Any] | None
        @param body:

        @rtype: None
        @return:
        """
        if body:
            exists = await self._client.indices.exists(index=index_)

            if not exists:
                await self._client.indices.create(index=index_, body=body)

    async def insert_document(
        self,
        index_: str,
        document: dict[str, Any],
        id_: str | None,
    ) -> dict[str, bool]:
        """
        Создание/обновление документа.

        @type index_: str
        @param index_:
        @type document: dict[str, Any]
        @param document:
        @type id_: str | None
        @param id_:

        @rtype: dict[str, bool]
        @return result:
        """
        result = {"status": True}
        response_ = await self._client.index(
            index=index_,
            document=document,
            id=id_,
        )

        if "error" in response_:
            result["status"], result["message"] = False, response_.get("error")

        return result


class ESContextManager:
    """Контекстный менеджер по работе с AsyncESClient."""

    def __init__(self) -> None:
        self._client: None | AsyncESClient = None

    @property
    def client(self) -> AsyncESClient | None:
        return self._client

    async def __aenter__(self) -> AsyncESClient:
        self._client = AsyncESClient()

        return self._client

    async def __aexit__(
        self,
        exc_type: str,
        exc_val: Any,
        exc_tb: str,
    ) -> None:
        if self._client is not None:
            await self._client.close_()


def es_indexes_mapping_checker(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """
    Декоратор, проверка наличия индексов в ES (создание при необходимости).

    @type func: Callable[..., Awaitable[Any]]
    @param func:

    @rtype: Callable[..., Awaitable[Any]]
    @return wrapper:
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with ESContextManager() as es_client:
            for index_path, index_name in db_config.es_indexes_path:
                try:
                    with open(index_path) as fp:
                        await es_client.create_index_with_ignore(
                            body=json.load(fp),
                            index_=index_name,
                        )

                except FileNotFoundError:
                    logger.warning(
                        f"[!] Index mapping '{index_path}' not found!"
                        " Mapping not created..."
                    )

                except JSONDecodeError as ex:
                    logger.warning(
                        f"[!] Index mapping '{index_path}' not correct!"
                        f" Mapping not created: {ex}"
                    )

        return await func(*args, **kwargs)

    return wrapper
