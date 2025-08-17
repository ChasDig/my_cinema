from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.app_config import config
from loaders import CinemaLoader
from producers import CinemaProducer
from utils.abstract import ETLSchedulerInterface


class CinemaETLScheduler(ETLSchedulerInterface):
    """Планировщик ETL-событий для Cinema Service."""

    @classmethod
    def jobs(cls) -> list[dict[str, Any]]:
        return [
            {
                "cls_job": CinemaProducer,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": CinemaLoader,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
        ]

    @classmethod
    async def run(cls) -> None:
        scheduler_ = AsyncIOScheduler()

        for job_ in cls.jobs():
            scheduler_.add_job(job_["cls_job"]().run, **job_["job_params"])

        scheduler_.start()
