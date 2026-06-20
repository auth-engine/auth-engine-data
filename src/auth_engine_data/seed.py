from auth_engine_data.core.runtime import configure_library_runtime
from auth_engine_data.core.settings import settings as seed_settings

configure_library_runtime(seed_settings)

import asyncio
import logging

import typer

from auth_engine_data.core.db import AsyncSessionLocal, init_db
from auth_engine_data.seeds.platform_config_seed import seed_platform_config
from auth_engine_data.seeds.rbac_seed import seed_roles
from auth_engine_data.seeds.super_admin_seed import seed_super_admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(
    help="AuthEngine data seeding — roles, super admin, and platform tenant config."
)


async def _run(create_tables: bool, roles: bool, superadmin: bool, platform_config: bool) -> None:
    if create_tables:
        logger.info("Creating database tables from models...")
        await init_db()
        logger.info("Database tables ready")
    async with AsyncSessionLocal() as session:
        if roles:
            await seed_roles(session)
        if superadmin:
            await seed_super_admin(session)
        if platform_config:
            await seed_platform_config(session)
    logger.info("Seed run finished")


@app.command(name="all")
def seed_all(
    create_tables: bool = typer.Option(
        False,
        "--create-tables",
        help="Create tables via SQLAlchemy create_all. Skip this when you already ran auth-engine migrate.",
    ),
) -> None:
    """Seed roles, super admin, and platform tenant config (email/SMS/social/password)."""
    if create_tables:
        logger.warning(
            "--create-tables uses create_all and bypasses Alembic. "
            "If you already ran auth-engine migrate, omit this flag and use: auth-engine-data all"
        )
    asyncio.run(_run(create_tables, roles=True, superadmin=True, platform_config=True))


@app.command()
def roles() -> None:
    """Seed only roles & permissions."""
    asyncio.run(_run(create_tables=False, roles=True, superadmin=False, platform_config=False))


@app.command()
def superadmin() -> None:
    """Seed only the super admin (requires roles to exist first)."""
    asyncio.run(_run(create_tables=False, roles=False, superadmin=True, platform_config=False))


@app.command(name="platform-config")
def platform_config_cmd() -> None:
    """Seed platform tenant email, SMS, social providers, and password policy from env."""
    asyncio.run(_run(create_tables=False, roles=False, superadmin=False, platform_config=True))


if __name__ == "__main__":
    app()
