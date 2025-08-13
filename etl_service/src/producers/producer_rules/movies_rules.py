from datetime import datetime

from producers.prducer_type_hints import ProduceRuleResultT
from sqlalchemy.ext.asyncio import AsyncSession


class MoviesRules:
    """Правило для выборки данных по Movies."""

    # TODO:
    @staticmethod
    async def produce_rule(  # type: ignore
        pg_session: AsyncSession,
        ref_timestamp: datetime | None,
    ) -> ProduceRuleResultT:
        pass
