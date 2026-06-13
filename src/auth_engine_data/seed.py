import asyncio
import logging

import typer

from auth_engine.core.postgres import AsyncSessionLocal, init_db

from auth_engine_data.bootstrap import seed_super_admin
from auth_engine_data.rbac_seed import seed_roles

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

app = typer.Typer(help="AuthEngine data seeding — roles, permissions and super admin.")


async def _run(create_tables: bool, roles: bool, superadmin: bool) -> None:
    if create_tables:
        await init_db()
    async with AsyncSessionLocal() as session:
        if roles:
            await seed_roles(session)
        if superadmin:
            await seed_super_admin(session)


@app.command(name="all")
def seed_all(
    create_tables: bool = typer.Option(
        False, "--create-tables", help="Run metadata create_all before seeding."
    ),
) -> None:
    """Seed roles & permissions, then bootstrap the super admin."""
    asyncio.run(_run(create_tables, roles=True, superadmin=True))


@app.command()
def roles() -> None:
    """Seed only roles & permissions."""
    asyncio.run(_run(create_tables=False, roles=True, superadmin=False))


@app.command()
def superadmin() -> None:
    """Bootstrap only the super admin (requires roles to exist first)."""
    asyncio.run(_run(create_tables=False, roles=False, superadmin=True))


if __name__ == "__main__":
    app()
