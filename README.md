# auth-engine-data

Seed data and bootstrap tooling for **AuthEngine**, kept separate from the
`auth-engine` service repository.

It contains the role/permission catalogue (`rbac_seed`) and the super-admin
bootstrap (`bootstrap`) that used to live inside `auth_engine.core`. The service
no longer seeds on startup — run this tool explicitly after the database schema
is in place.

## How it works

This package depends on `auth-engine` as a **library** so the ORM models,
settings and security helpers remain the single source of truth. It opens its
own async session against the same database and applies the seeds idempotently.

## Install

Requires Python 3.12+. Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
cd auth-engine-data
uv sync            # resolves the local ../auth-engine path dependency
```

Or with pip + a virtualenv:

```bash
cd auth-engine-data
python -m venv .venv && source .venv/bin/activate
pip install -e ../auth-engine
pip install -e .
```

## Configure

Configuration is read through `auth_engine`'s settings, which load `.env.local`
from the current working directory:

```bash
cp .env.example .env.local
# edit .env.local — at minimum POSTGRES_URL, SECRET_KEY, JWT_SECRET_KEY,
# MONGODB_URL, REDIS_URL and the SUPERADMIN_* values
```

## Run

```bash
# Seed roles & permissions, then bootstrap the super admin
uv run auth-engine-data all

# Optionally create tables first (metadata create_all) for a fresh DB
uv run auth-engine-data all --create-tables

# Individual steps
uv run auth-engine-data roles
uv run auth-engine-data superadmin
```

(If installed with pip, drop the `uv run` prefix.)

> Order matters: `superadmin` requires the `SUPER_ADMIN` role, so run `roles`
> (or `all`) first.

## Deployment note

Because seeding is no longer part of the API server's startup, run
`auth-engine-data all` as a one-off job after migrations whenever you stand up a
new environment (e.g. an init container, a CI step, or a manual command).
