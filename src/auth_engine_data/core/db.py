from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_engine.core.postgres import Base

from auth_engine_data.core.settings import settings

_connect_args: dict[str, str] = {}
if settings.POSTGRES_SSL:
    _connect_args["ssl"] = "require"

engine = create_async_engine(
    settings.POSTGRES_URL,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=_connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    import auth_engine.models  # noqa: F401 — register ORM metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_connection() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
