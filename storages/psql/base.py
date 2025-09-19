from __future__ import annotations
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        values = ", ".join(
            [
                f"{column.name}={getattr(self, column.name)}"
                for column in self.__table__.columns.values()
            ],
        )
        return f"{self.__tablename__}({values})"


async def create_db_pool(
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine: AsyncEngine = create_async_engine(
        os.getenv("PSQL_DSN"),
        echo=int(os.getenv("PSQL_ECHO")==1),
        max_overflow=10,
        pool_size=100,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def close_db_pool(engine: AsyncEngine) -> None:
    await engine.dispose()