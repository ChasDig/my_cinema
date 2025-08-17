from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

PDModelsT = TypeVar("PDModelsT", bound=BaseModel)


class BaseLoad(ABC, Generic[PDModelsT]):
    """Интерфейс для указания правил Loader."""

    @abstractmethod
    async def run(self, formatted_data: PDModelsT) -> list[PDModelsT]:
        pass
