from typing import TypeVar

from models.pg_models import Base
from pydantic import BaseModel

PGModelsT = TypeVar("PGModelsT", bound=Base)
PDModelsT = TypeVar("PDModelsT", bound=BaseModel)
