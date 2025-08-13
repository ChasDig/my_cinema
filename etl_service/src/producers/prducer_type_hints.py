from datetime import datetime
from typing import Any, Callable, Coroutine, Type

from models.pg_models import BaseDatetimeStamped
from sqlalchemy.ext.asyncio import AsyncSession

# CinemaProducer:
PGModelsT = Type[BaseDatetimeStamped]
ProduceRuleResultT = list[PGModelsT]
ProduceRuleFuncT = Callable[
    [AsyncSession, datetime | None],
    Coroutine[Any, Any, list[PGModelsT]],
]
ModelsByRuleT = dict[PGModelsT, ProduceRuleFuncT]
