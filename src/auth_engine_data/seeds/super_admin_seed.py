import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth_engine.core.security import security as security_utils
from auth_engine.models import RoleORM, TenantORM, UserORM, UserRoleORM
from auth_engine.models.tenant import TenantType
from auth_engine.models.tenant_auth_config import TenantAuthConfigORM
from auth_engine.schemas.user import AuthStrategy, UserStatus

from auth_engine_data.core.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_PLATFORM_ALLOWED_METHODS = ["email_password"]
DEFAULT_PLATFORM_PASSWORD_POLICY = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_special": True,
}


async def _ensure_platform_auth_config(db: AsyncSession, platform_id) -> None:
    auth_config = await db.scalar(
        select(TenantAuthConfigORM).where(TenantAuthConfigORM.tenant_id == platform_id)
    )
    if auth_config:
        if "email_password" not in (auth_config.allowed_methods or []):
            auth_config.allowed_methods = [
                "email_password",
                *(auth_config.allowed_methods or []),
            ]
        return

    db.add(
        TenantAuthConfigORM(
            tenant_id=platform_id,
            allowed_methods=DEFAULT_PLATFORM_ALLOWED_METHODS.copy(),
            mfa_required=False,
            password_policy=DEFAULT_PLATFORM_PASSWORD_POLICY.copy(),
            session_ttl_seconds=3600,
            allowed_domains=[],
        )
    )


async def seed_super_admin(db: AsyncSession) -> None:
    """Create the super admin user, platform tenant, and role assignment if missing."""
    super_admin_role = await db.scalar(
        select(RoleORM).where(
            RoleORM.name == "SUPER_ADMIN",
            RoleORM.tenant_id.is_(None),
        )
    )
    if not super_admin_role:
        logger.warning("SUPER_ADMIN role not found — run auth-engine-data roles first")
        return

    user = await db.scalar(select(UserORM).where(UserORM.email == settings.SUPERADMIN_EMAIL))
    platform = await db.scalar(
        select(TenantORM)
        .where(TenantORM.type == TenantType.PLATFORM)
        .order_by(TenantORM.created_at.asc())
        .limit(1)
    )

    if user and platform:
        assignment = await db.scalar(
            select(UserRoleORM.user_id).where(
                UserRoleORM.user_id == user.id,
                UserRoleORM.role_id == super_admin_role.id,
                UserRoleORM.tenant_id == platform.id,
            )
        )
        if assignment:
            await _ensure_platform_auth_config(db, platform.id)
            await db.commit()
            logger.info("Super admin already seeded — skipping")
            return

    logger.info("Seeding super admin...")
    now = datetime.now(UTC)

    if not user:
        user = UserORM(
            email=settings.SUPERADMIN_EMAIL,
            is_email_verified=True,
            phone_number="+91 9999999999",
            is_phone_verified=True,
            username="super_admin",
            password_hash=security_utils.hash_password(settings.SUPERADMIN_PASSWORD),
            first_name="Super",
            last_name="Admin",
            status=UserStatus.ACTIVE,
            auth_strategies=[AuthStrategy.EMAIL_PASSWORD],
            created_at=now,
            updated_at=now,
        )
        db.add(user)
        await db.flush()
        logger.info("Created super admin user: %s", settings.SUPERADMIN_EMAIL)

    if not platform:
        platform = TenantORM(
            name="Platform",
            type=TenantType.PLATFORM,
            description="System platform tenant",
            owner_id=user.id,
            created_by=user.id,
        )
        db.add(platform)
        await db.flush()
        logger.info("Created platform tenant")

    await _ensure_platform_auth_config(db, platform.id)

    await db.execute(
        insert(UserRoleORM)
        .values(
            user_id=user.id,
            role_id=super_admin_role.id,
            tenant_id=platform.id,
        )
        .on_conflict_do_nothing()
    )

    await db.commit()
    logger.info("Super admin seed complete")
