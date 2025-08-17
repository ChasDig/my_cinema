from loaders.base import BaseLoad, PDModelsT
from models.pydantic_models import MoviesProducerModel


class MoviesLoaderRule(BaseLoad[MoviesProducerModel]):
    """Правило для сохранения форматированных данных в ES по Movies."""

    # TODO:
    async def run(self, formatted_data: PDModelsT) -> list[PDModelsT]:  # type: ignore  # noqa: E501
        pass
