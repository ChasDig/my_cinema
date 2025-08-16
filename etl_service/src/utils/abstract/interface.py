from abc import ABC, abstractmethod
from typing import Any


class ETLSchedulerInterface(ABC):
    """Интерфейс для реализации ETL-процессов через AsyncIOScheduler."""

    @classmethod
    @abstractmethod
    def jobs(cls) -> list[dict[str, Any]]:
        """
        Метод получения всех задач (с заданными параметрами) для Scheduler.
        """

    @classmethod
    @abstractmethod
    async def run(cls) -> None:
        """Метод добавления всех задач в Scheduler."""
