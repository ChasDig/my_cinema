from asyncio import Queue
from typing import Any


class Storage:
    """Хранилище, предоставляет доступ к Queue, связывающие ETL-процессы."""

    def __init__(self) -> None:
        self.raw_data_queue: dict[str, Queue[Any]] = dict()
        self.formatted_data_queue: dict[str, Queue[Any]] = dict()

    def get_raw_queue_by_type(self, type_: str) -> Queue[Any] | None:
        """
        Получение данных из raw_data_queue - очередь с сырыми данными из
        Postgres.
        Данная очередь используется в качестве Хранилища(связывающей шины)
        между Extract -> Transform процессами.

        @type type_: str
        @param type_: Тип объекта, по которому хранятся данные в очереди.

        @rtype: Queue[Any] | None
        @return:
        """
        if not self.raw_data_queue.get(type_):
            self.raw_data_queue[type_] = Queue()

        return self.raw_data_queue[type_]

    def get_formatted_queue_by_type(self, type_: str) -> Queue[Any] | None:
        """
        Получение данных из formatted_data_queue - очередь с готовыми данными
        для записи в Elasticsearch.
        Данная очередь используется в качестве Хранилища(связывающей шины)
        между Transform -> Load процессами.

        @type type_: str
        @param type_: Тип объекта, по которому хранятся данные в очереди.

        @rtype: Queue[Any] | None
        @return:
        """
        if not self.formatted_data_queue.get(type_):
            self.formatted_data_queue[type_] = Queue()

        return self.formatted_data_queue[type_]
