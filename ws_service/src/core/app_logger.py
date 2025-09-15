import logging
import pathlib

from core.app_config import config


def get_logger() -> logging.Logger:
    """
    Получение Logger-а.

    @rtype logger_: logging.Logger
    @return logger_:
    """
    logger_ = logging.getLogger()
    logger_.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()

    pathlib.Path(
        f"{config.base_dir}/logs/",
    ).mkdir(
        exist_ok=True,
    )
    file_handler = logging.FileHandler(
        f"{config.base_dir}/logs/app.log",
    )
    formatter = logging.Formatter(
        config.log_format,
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger_.addHandler(console_handler)
    logger_.addHandler(file_handler)

    return logger_


logger = get_logger()
