import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth_engine.models.permission import PermissionORM
from auth_engine.models.role import RoleORM, RoleScope
from auth_engine.models.role_permission import RolePermissionORM

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    ("SUPER_ADMIN", "Full platform control", RoleScope.PLATFORM, 100, False),
    ("PLATFORM_ADMIN", "Manage organizations", RoleScope.PLATFORM, 80, False),
    ("TENANT_OWNER", "Owner of organization", RoleScope.TENANT, 60, True),
    ("TENANT_ADMIN", "Admin inside tenant", RoleScope.TENANT, 50, True),
    ("TENANT_MANAGER", "Manager inside tenant", RoleScope.TENANT, 30, True),
    ("TENANT_USER", "Standard tenant user", RoleScope.TENANT, 10, True),
]

DEFAULT_PERMISSIONS = [
    ("platform.users.view", "View all users globally"),
    ("platform.users.manage", "Manage all users globally"),
    ("platform.roles.assign", "Assign platform-level roles"),
    ("platform.tenants.view", "View all tenants globally"),
    ("platform.tenants.manage", "Manage all tenants globally"),
    ("platform.audit.view", "View all audit logs globally"),
    ("platform.leads.view", "View marketing contact form leads"),
    ("tenant.view", "View tenant details"),
    ("tenant.update", "Update tenant details"),
    ("tenant.delete", "Delete tenant"),
    ("tenant.users.view", "View users in tenant"),
    ("tenant.users.manage", "Manage users in tenant"),
    ("tenant.roles.view", "View roles in tenant"),
    ("tenant.roles.assign", "Assign roles in tenant"),
    ("tenant.roles.manage", "Create and manage roles in tenant"),
    ("auth.tokens.request", "Request authentication and verification tokens"),
    ("auth.password.reset", "Initiate and perform password reset"),
    ("auth.email.verify", "Perform email verification"),
    ("auth.phone.verify", "Perform phone verification"),
    ("auth.tokens.refresh", "Refresh authentication tokens"),
]

ROLE_PERMISSIONS = {
    "SUPER_ADMIN": [p[0] for p in DEFAULT_PERMISSIONS],
    "PLATFORM_ADMIN": [
        "platform.users.view",
        "platform.tenants.view",
        "platform.tenants.manage",
        "platform.roles.assign",
        "platform.audit.view",
        "platform.leads.view",
        "tenant.view",
        "tenant.update",
        "tenant.delete",
        "tenant.users.view",
        "auth.tokens.request",
        "auth.password.reset",
        "auth.email.verify",
        "auth.phone.verify",
        "auth.tokens.refresh",
    ],
    "TENANT_OWNER": [
        "tenant.view",
        "tenant.update",
        "tenant.delete",
        "tenant.users.view",
        "tenant.users.manage",
        "tenant.roles.view",
        "tenant.roles.assign",
        "tenant.roles.manage",
        "auth.tokens.request",
        "auth.password.reset",
        "auth.email.verify",
        "auth.phone.verify",
        "auth.tokens.refresh",
    ],
    "TENANT_ADMIN": [
        "tenant.view",
        "tenant.update",
        "tenant.users.view",
        "tenant.users.manage",
        "tenant.roles.view",
        "tenant.roles.assign",
        "tenant.roles.manage",
        "auth.tokens.request",
        "auth.password.reset",
        "auth.email.verify",
        "auth.phone.verify",
        "auth.tokens.refresh",
    ],
    "TENANT_MANAGER": [
        "tenant.view",
        "tenant.users.view",
        "tenant.roles.view",
        "tenant.roles.assign",
        "auth.tokens.request",
        "auth.password.reset",
        "auth.email.verify",
        "auth.phone.verify",
        "auth.tokens.refresh",
    ],
    "TENANT_USER": [
        "tenant.view",
        "auth.tokens.request",
        "auth.password.reset",
        "auth.email.verify",
        "auth.phone.verify",
        "auth.tokens.refresh",
    ],
}


async def _upsert_role(
    db: AsyncSession,
    *,
    name: str,
    description: str,
    scope: RoleScope,
    level: int,
    is_template: bool,
) -> RoleORM:
    if scope == RoleScope.PLATFORM:
        result = await db.execute(
            select(RoleORM).where(
                RoleORM.name == name,
                RoleORM.scope == RoleScope.PLATFORM,
                RoleORM.tenant_id.is_(None),
            )
        )
    else:
        result = await db.execute(
            select(RoleORM).where(
                RoleORM.name == name,
                RoleORM.is_template.is_(True),
                RoleORM.tenant_id.is_(None),
            )
        )

    role = result.scalar_one_or_none()
    if role:
        role.description = description
        role.level = level
        role.is_template = is_template
        return role

    role = RoleORM(
        name=name,
        description=description,
        scope=scope,
        level=level,
        is_template=is_template,
        tenant_id=None,
    )
    db.add(role)
    await db.flush()
    return role


async def seed_roles(db: AsyncSession) -> None:
    for name, desc, scope, level, is_template in DEFAULT_ROLES:
        await _upsert_role(
            db,
            name=name,
            description=desc,
            scope=scope,
            level=level,
            is_template=is_template,
        )

    perm_rows = [{"name": name, "description": desc} for name, desc in DEFAULT_PERMISSIONS]
    await db.execute(
        insert(PermissionORM)
        .values(perm_rows)
        .on_conflict_do_update(
            index_elements=["name"],
            set_={"description": insert(PermissionORM).excluded.description},
        )
    )

    await db.flush()

    roles = {
        r.name: r
        for r in (await db.execute(select(RoleORM).where(RoleORM.tenant_id.is_(None))))
        .scalars()
        .all()
    }
    perms = {p.name: p for p in (await db.execute(select(PermissionORM))).scalars().all()}

    assoc_rows = [
        {"role_id": roles[role_name].id, "permission_id": perms[perm_name].id}
        for role_name, perm_names in ROLE_PERMISSIONS.items()
        for perm_name in perm_names
        if role_name in roles and perm_name in perms
    ]

    if assoc_rows:
        await db.execute(insert(RolePermissionORM).values(assoc_rows).on_conflict_do_nothing())

    await db.commit()
    logger.info("Roles and permissions seeded successfully")
