# auth-engine-data

Seed data tooling for **AuthEngine** — RBAC catalogue, super-admin provisioning, and optional platform-tenant config.

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

Standalone CLI for seeding roles, permissions, the super admin, and (optionally) platform-tenant email, SMS, social OAuth, and password policy. It depends on **[auth-engine](https://github.com/auth-engine/auth-engine)** as a **library** (ORM models, security helpers) but uses its **own** `.env.local` — it does not read `auth-engine/.env.local`.

Run explicitly after Alembic migrations; all operations are idempotent. No Dockerfile — use as a one-off job (init container, CI step, or manual command).

### Package layout

```text
auth_engine_data/
├── seed.py              # CLI entry point
├── core/
│   ├── settings.py      # SeedSettings (.env.local)
│   ├── db.py            # PostgreSQL engine + session
│   └── runtime.py       # auth_engine import bootstrap (internal)
└── seeds/
    ├── rbac_seed.py
    ├── super_admin_seed.py
    └── platform_config_seed.py
```

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

**Configure** — copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

| Variable | Required | Notes |
|----------|----------|-------|
| `POSTGRES_URL` | Yes | Same database as auth-engine |
| `SECRET_KEY` | Yes | Must match auth-engine `SECRET_KEY` when using `platform-config` |
| `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` | Yes | Super admin credentials |
| `EMAIL_*`, `SMS_*`, `GOOGLE_*`, `AUTHENGINE_*`, `PASSWORD_*` | No | One-time platform-tenant seed (see `.env.example` comments) |

For hosted Postgres, set `POSTGRES_SSL=true` in `.env.local`.

**Run** (after `auth-engine migrate` in the auth-engine repo):

```bash
uv run auth-engine-data all                 # roles + super admin + platform config
uv run auth-engine-data roles
uv run auth-engine-data superadmin          # requires roles first
uv run auth-engine-data platform-config     # email / SMS / social / password policy only
```

Use `--create-tables` only for local experiments **without** Alembic — not after `auth-engine migrate`:

```bash
uv run auth-engine-data all --create-tables # local dev only — skip if migrate already ran
```

(If installed with pip, drop the `uv run` prefix.)

After seeding, manage platform email, SMS, OAuth, and password policy in the **dashboard** (Communications / Auth settings).

### Production seeding (K8s / Helm)

On first deploy, enable the Helm seed Job or run manually:

```bash
# Helm values (first install only)
seed:
  enabled: true
  superadminEmail: "admin@example.com"
  superadminPassword: "<strong-password>"

# Or from auth-engine-infra:
./deploy/auth-engine-deploy.sh k8s-seed
```

Requires `POSTGRES_URL` and `SECRET_KEY` matching the Helm chart secrets. See [deployment guide](https://docs.authengine.org/deployment/).

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
