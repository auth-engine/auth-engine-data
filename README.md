# auth-engine-data

Database seeding CLI for **AuthEngine** — roles & permissions, super admin, platform tenant, and optional email/SMS/social/password config.

Uses [auth-engine](https://github.com/auth-engine/auth-engine) as a library (ORM, security). Has its own `.env.local` — separate from `auth-engine/.env.local`. All commands are idempotent.

Run **after** `auth-engine migrate`. The API does not seed on startup.

## Seed data

### Local (API running on host)

```bash
cd auth-engine-data
uv sync
cp .env.example .env.local    # POSTGRES_URL → localhost, SECRET_KEY matches auth-engine
uv run auth-engine-data all   # roles + super admin + platform config
```

Individual commands: `roles` · `superadmin` · `platform-config`

### Compose (databases in Docker)

```bash
cd auth-engine-infra/compose
docker compose up -d
docker exec authengine-api auth-engine migrate

cd ../../auth-engine-data
uv sync && cp .env.example .env.local
# .env.example already uses localhost:5432 for compose Postgres
uv run auth-engine-data all
```

### Production (Kubernetes)

Enable in Helm values (`seed.enabled: true`) or run via [auth-engine-infra/scripts](https://github.com/auth-engine/auth-engine-infra/tree/main/scripts). `SECRET_KEY` must match the API deployment.

## Documentation

| Guide | Link |
|-------|------|
| Quick Start | [docs.authengine.org/quick-start](https://docs.authengine.org/quick-start/) |
| Deployment | [docs.authengine.org/deployment](https://docs.authengine.org/deployment/) |
| Architecture | [docs.authengine.org/architecture](https://docs.authengine.org/architecture/) |

## Related repositories

[auth-engine](https://github.com/auth-engine/auth-engine) · [auth-engine-dashboard](https://github.com/auth-engine/auth-engine-dashboard) · [auth-engine-infra](https://github.com/auth-engine/auth-engine-infra) · [auth-engine-docs](https://github.com/auth-engine/auth-engine-docs)
