from typing import Mapping, Type, TypeVar

from models.pg_models import Base
from producers.base import BaseRule
from pydantic import BaseModel

PGModelsT = TypeVar("PGModelsT", bound=Base)
PDModelsT = TypeVar("PDModelsT", bound=BaseModel)

ModelsByRuleT = Mapping[
    Type[PGModelsT],
    Type[BaseRule[BaseModel]],
]
