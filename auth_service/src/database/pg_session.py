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

from core import config, logger, SingletonMeta


class AsyncSessionFactory(metaclass=SingletonMeta):
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
    drivername=config.pg_drivername,
    database=config.pg_database,
    username=config.pg_username,
    password=config.pg_password,
    host=config.pg_host,
    port=config.pg_port,
)


def create_sqlalchemy_async_engine(url: str | URL) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=config.pg_engine_echo,
        pool_pre_ping=config.pg_engine_pool_pre_ping,
        pool_recycle=config.pg_engine_pool_recycle,
        pool_size=config.pg_engine_pool_size,
        max_overflow=config.pg_engine_max_overflow,
    )


async_engine_ = create_sqlalchemy_async_engine(url=URL_)
pg_session_factory = AsyncSessionFactory(async_engine=async_engine_)


async def get_pg_session() -> AsyncGenerator[AsyncSession, Any]:
    async with pg_session_factory.context_session() as session:
        yield session
