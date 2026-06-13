# auth-engine-data

Seed data and bootstrap tooling for **AuthEngine** — RBAC catalogue and super-admin provisioning.

**Documentation:** [auth-engine-docs](https://github.com/auth-engine/auth-engine-docs) · published at [docs.authengine.org](https://docs.authengine.org)

| Guide | Link |
|-------|------|
| Quick Start | [quick-start.md](https://docs.authengine.org/quick-start/) |
| OAuth2 / OIDC | [oauth2-oidc-guides.md](https://docs.authengine.org/oauth2-oidc-guides/) |
| API Reference | [api-reference.md](https://docs.authengine.org/api-reference/) |
| Architecture | [architecture.md](https://docs.authengine.org/architecture/) |
| Deployment | [deployment.md](https://docs.authengine.org/deployment/) |
| Security | [security-overview.md](https://docs.authengine.org/security-overview/) |

## What this repository is

Standalone CLI for seeding roles, permissions, and the super admin. It depends on **[auth-engine](https://github.com/auth-engine/auth-engine)** as a library so ORM models and settings stay the single source of truth. Run explicitly after migrations; all operations are idempotent. There is no Dockerfile — use as a one-off job (init container, CI step, or manual command).

## Install, configure & run

Requires Python **3.12+**. The default `uv` setup expects `auth-engine` as a sibling directory (`../auth-engine`).

**Install** with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
cd auth-engine-data
uv sync
```

Or with pip:

```bash
cd auth-engine-data
python -m venv .venv && source .venv/bin/activate
pip install -e ../auth-engine
pip install -e .
```

**Configure** — settings load `.env.local` from the current working directory:

```bash
cp .env.example .env.local
# POSTGRES_URL, SECRET_KEY, JWT_SECRET_KEY, MONGODB_URL, REDIS_URL, SUPERADMIN_*
```

**Run:**

```bash
uv run auth-engine-data all
uv run auth-engine-data all --create-tables   # fresh DB only (create_all, not Alembic)
uv run auth-engine-data roles
uv run auth-engine-data superadmin            # requires roles first
```

(If installed with pip, drop the `uv run` prefix.)

## Production

| Host | Role |
|------|------|
| [api.authengine.org](https://api.authengine.org) | API + Swagger |
| [auth.authengine.org](https://auth.authengine.org) | OIDC / login UI |
| [app.authengine.org](https://app.authengine.org) | Admin dashboard |
| [docs.authengine.org](https://docs.authengine.org) | Documentation |

## Contributing

See [Contributing](https://docs.authengine.org/contributing/) or [CONTRIBUTING.md](CONTRIBUTING.md). Report security issues per [Security Policy](https://docs.authengine.org/security-policy/) — not via public issues.

## Related repositories

| Repository | Role |
|------------|------|
| [auth-engine](https://github.com/auth-engine/auth-engine) | FastAPI backend — IAM, OIDC, introspection |
| [auth-engine-dashboard](https://github.com/auth-engine/auth-engine-dashboard) | Next.js admin dashboard |
| [auth-engine-docs](https://github.com/auth-engine/auth-engine-docs) | Platform documentation |
| [auth-engine-infra](https://github.com/auth-engine/auth-engine-infra) | Terraform & Docker Compose |
| [.github](https://github.com/auth-engine/.github) | Org profile, contributing & security policy |
