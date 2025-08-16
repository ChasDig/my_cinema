from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

PDModelsT = TypeVar("PDModelsT", bound=BaseModel)


class BaseRule(ABC, Generic[PDModelsT]):
    """Интерфейс для указания правил Producer."""

    @abstractmethod
    async def run(
        self,
        session: AsyncSession,
        ref_dt: datetime | None,
    ) -> list[PDModelsT]:
        pass
