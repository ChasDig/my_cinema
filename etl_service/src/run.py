import asyncio

from scheduler import CinemaETLScheduler

if __name__ == "__main__":
    """
    Точка входа. Запуск планировщиков ETL-событий:
    - CinemaETLScheduler: ETL-обработчиков для Cinema Service.
    """
    current_event_loop = asyncio.get_event_loop()

    current_event_loop.run_until_complete(CinemaETLScheduler.run())

    current_event_loop.run_forever()
