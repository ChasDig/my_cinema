from asyncio import Queue
from typing import Any

from core.app_config import config


class Storage:
    """Хранилище, предоставляет доступ к Queue, связывающие ETL-процессы."""

    def __init__(self) -> None:
        self.raw_data_queue: dict[str, Queue[Any]] = dict()
        self.formatted_data_queue: dict[str, Queue[Any]] = dict()

    def raw_queue_by_type(self, type_: str) -> Queue[Any]:
        """
        Получение данных из raw_data_queue - очередь с сырыми данными из
        Postgres.
        Данная очередь используется в качестве Хранилища(связывающей шины)
        между Extract -> Transform процессами.

        @type type_: str
        @param type_: Тип объекта, по которому хранятся данные в очереди.

        @rtype: Queue[Any]
        @return:
        """
        if not self.raw_data_queue.get(type_):
            self.raw_data_queue[type_] = Queue(
                maxsize=config.etl_movies_select_limit,
            )

        return self.raw_data_queue[type_]

    def formatted_queue_by_type(self, type_: str) -> Queue[Any]:
        """
        Получение данных из formatted_data_queue - очередь с готовыми данными
        для записи в Elasticsearch.
        Данная очередь используется в качестве Хранилища(связывающей шины)
        между Transform -> Load процессами.

        @type type_: str
        @param type_: Тип объекта, по которому хранятся данные в очереди.

        @rtype: Queue[Any]
        @return:
        """
        if not self.formatted_data_queue.get(type_):
            self.formatted_data_queue[type_] = Queue(
                maxsize=config.etl_movies_select_limit,
            )

        return self.formatted_data_queue[type_]


storage = Storage()
