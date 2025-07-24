from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from sqlalchemy.engine import URL
from sqlalchemy.exc import InterfaceError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from core import db_config, logger, SingletonMeta


class AsyncSessionFactory(metaclass=SingletonMeta):
    """Фабрика создания сессий с Postgres."""

    ERROR_EXC_TYPES = (InterfaceError, SQLAlchemyError)

    def __init__(self, *args, async_engine: AsyncEngine, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._engine: AsyncEngine = async_engine
        self._session_factory = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def context_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Асинхронный менеджер контекста по созданию асинхронной сессии к
        Postgres через фабрику async_sessionmaker.

        @rtype session: AsyncGenerator[AsyncSession, None]
        @return session:
        """
        session = self._session_factory()

        try:
            yield session

        except self.ERROR_EXC_TYPES as ex:
            logger.error(f"SQLAlchemy(Postgres) error: {ex}")

            if session:
                await session.rollback()

            raise

        except Exception as ex:
            logger.error(f"Not correct SQLAlchemy(Postgres) error: {ex}")

            if session:
                await session.rollback()

            raise

        finally:
            if session:
                await session.close()


URL_ = URL.create(
    drivername=db_config.pg_drivername,
    database=db_config.pg_database,
    username=db_config.pg_username,
    password=db_config.pg_password,
    host=db_config.pg_host,
    port=db_config.pg_port,
)


def create_sqlalchemy_async_engine(url: str | URL) -> AsyncEngine:
    """
    Создание асинхронного движка для подключения к Postgres.

    @type url: str | URL
    @param url:

    @rtype: AsyncEngine
    @return:
    """
    return create_async_engine(
        url=url,
        echo=db_config.pg_engine_echo,
        pool_pre_ping=db_config.pg_engine_pool_pre_ping,
        pool_recycle=db_config.pg_engine_pool_recycle,
        pool_size=db_config.pg_engine_pool_size,
        max_overflow=db_config.pg_engine_max_overflow,
    )


async_engine_ = create_sqlalchemy_async_engine(url=URL_)
pg_session_factory = AsyncSessionFactory(async_engine=async_engine_)


async def get_pg_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Асинхронный генератор для получения активной сессии с Postgres.

    @rtype session: AsyncGenerator[AsyncSession, Any]
    @return session:
    """
    async with pg_session_factory.context_session() as session:
        yield session
