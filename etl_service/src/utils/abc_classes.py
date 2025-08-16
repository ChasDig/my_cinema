from abc import ABC, abstractmethod
from typing import Any


class ETLComponent(ABC):
    """Интерфейс для основных ETL-компонентов."""

    @abstractmethod
    async def run(self) -> Any:
        pass
