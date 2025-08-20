import logging

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

    formatter = logging.Formatter(
        config.log_format,
    )

    console_handler.setFormatter(formatter)
    logger_.addHandler(console_handler)

    return logger_


logger = get_logger()
