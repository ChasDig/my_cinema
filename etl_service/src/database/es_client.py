import json
from functools import wraps
from typing import TypeVar

from core.app_config import config, db_config
from core.app_logger import logger
from elasticsearch import AsyncElasticsearch, NotFoundError

ESClient_T = TypeVar("ESClient_T", bound="AsyncESClient")


class AsyncESClient:
    """Async-клиент Elasticsearch."""

    def __init__(self):  # type: ignore
        self._client = AsyncElasticsearch(
            config.elastic_url,
            basic_auth=(config.elastic_name, config.elastic_password),
            max_retries=0,
            retry_on_timeout=False,
        )

    async def close_(self):  # type: ignore
        await self._client.close()

    async def create_index_with_ignore(self, index_, body=None):  # type: ignore  # noqa: E501
        if body:
            try:
                await self._client.search(index=index_)

            except NotFoundError:
                await self._client.indices.create(index=index_, body=body)

    async def insert_document(  # type: ignore
        self,
        index_,
        document,
        id_,
    ):
        result = {"status": True}
        response_ = await self._client.index(
            index=index_,
            document=document,
            id=id_,
        )

        if body := response_.get("body"):
            if error := body.get("error"):
                result["status"], result["message"] = False, error

        return result


class ESContextManager:
    """Контекстный менеджер по работе с RedisStorage."""

    def __init__(self):  # type: ignore
        self._client = None

    @property
    def client(self):  # type: ignore
        return self._client

    async def __aenter__(self):  # type: ignore
        self._client = AsyncESClient()  # type: ignore

        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self._client.close_()  # type: ignore


def es_indexes_mapping_checker(func):  # type: ignore
    @wraps(func)
    async def wrapper(*args, **kwargs):  # type: ignore
        async with ESContextManager() as es_client:  # type: ignore
            for index_name in db_config.es_indexes_name:
                try:
                    with open(index_name) as fp:
                        await es_client.create_index_with_ignore(
                            body=json.load(fp),
                            index_=index_name,
                        )

                except FileNotFoundError:
                    logger.warning(
                        f"[!] Index mapping '{index_name}' not found!"
                        " Mapping not created..."
                    )

        return await func(*args, **kwargs)

    return wrapper
