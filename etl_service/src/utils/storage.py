from asyncio import Queue

from core.app_config import config
from pydantic import BaseModel


class Storage:
    """Хранилище, предоставляет доступ к Queue, связывающие ETL-процессы."""

    # Требуется добавить в очередь флаг, сигнализирующий об окончании итерации
    # по очереди для указанной пачки
    CONCAT = 1

    def __init__(self) -> None:
        self.formatted_data_queue: dict[str, Queue[BaseModel | None]] = dict()

    def formatted_queue_by_type(self, type_: str) -> Queue[BaseModel | None]:
        """
        Получение данных из formatted_data_queue - очередь с готовыми данными
        для записи в Elasticsearch.
        Данная очередь используется в качестве Хранилища(связывающей шины)
        между Transform -> Load процессами.

        @type type_: str
        @param type_: Тип объекта, по которому хранятся данные в очереди.

        @rtype: Queue[BaseModel | None]
        @return:
        """
        if not self.formatted_data_queue.get(type_):
            self.formatted_data_queue[type_] = Queue(
                maxsize=config.etl_movies_select_limit + self.CONCAT,
            )

        return self.formatted_data_queue[type_]


storage = Storage()
