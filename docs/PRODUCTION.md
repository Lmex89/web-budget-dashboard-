# Production Guide

Self-hosted deployment with Docker Compose. See [DEVELOPMENT.md](DEVELOPMENT.md) for local setup.

## Topology

| Service | Build | Host port | Notes |
|---|---|---|---|
| `frontend` | `frontend/Dockerfile.prod` (node build → nginx alpine) | `5173` | Serves the built SPA; `read_only` container, `/health` endpoint |
| `backend` | `backend/Dockerfile` (FastAPI + uvicorn) | `8003` | API and `/docs` |
| `db` | `mariadb:10.11` | `3308` | Timezone `America/Merida` |

## 1. Configure

```bash
cp .env.docker.example .env.docker
ln -sf .env.docker .env       # required: Compose reads build args (VITE_API_BASE_URL) from .env
```

Edit `.env.docker`:

| Variable | Production guidance |
|---|---|
| `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD` | Strong unique values |
| `DATABASE_URL` | Must match the `MYSQL_*` values (`@db:3306`) |
| `SECRET_KEY` | Long random string; rotating it invalidates all sessions |
| `VITE_API_BASE_URL` | Public API URL, e.g. `https://api.example.com` — baked into the bundle at build time |
| `BACKEND_CORS_ORIGINS` | Comma-separated public frontend origins, e.g. `https://budget.example.com` |
| `ENABLE_GLOBAL_TENANT_GUARD` | Keep `false` until validated in staging, then enable |
| `BACK_BLAZE_*` | Optional offsite backups (see the README) |
| `EMAIL_PROVIDER` | `brevo` to send real email, `console` to log only, `disabled` to turn off |
| `EMAIL_FROM_EMAIL` / `EMAIL_FROM_NAME` | Sender identity; the address must be verified in Brevo (Senders & Domains) |
| `EMAIL_API_KEY` (or `BREVO_API_KEY` / legacy `APIKEY_BREVO`) | Brevo API key with transactional email permission |
| `APP_BASE_URL` | Public frontend URL used for links inside emails |

## 2. Build and start

```bash
docker compose up -d --build
docker compose exec backend python -m migrations.run_migrations
docker compose exec backend python -m migrations.seed   # first deploy only
```

Open http://<host>:5173 and change the seeded admin credentials (`admin@family.com`).

## 3. Updates

```bash
git pull
docker compose up -d --build
docker compose exec backend python -m migrations.run_migrations
```

- Changing `VITE_API_BASE_URL` requires a frontend rebuild: `docker compose up -d --build frontend`.
- The migration runner re-applies every SQL file and is **not** idempotent. For an existing database,
  apply only the new file:

```bash
docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' \
  < backend/migrations/sql/NNN_name.sql
```

## 4. Hardening

- The Compose `backend` service overrides the image `CMD` with `--reload` and bind-mounts `./backend`
  for local development. On a production host, remove the `volumes:` mount and `command:` override
  so the image default runs: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Terminate TLS at a reverse proxy (nginx, Caddy, Traefik) in front of the frontend and API. Set
  `VITE_API_BASE_URL` and `BACKEND_CORS_ORIGINS` to the public HTTPS origins and rebuild the frontend.
- Do not expose the database (`3308`) or backend (`8003`) to the public internet.
- Restrict or disable `/docs` publicly if the API is internet-facing.
- Change the seeded admin credentials and remove any test data.

## 5. Health and logs

```bash
docker compose ps                 # db and frontend healthchecks
docker compose logs -f backend
curl http://localhost:8003/docs   # API docs
```

## 6. Backups

See [README → Database Backup & Restore](../README.md#database-backup--restore). Daily cron template:
`crontab-entry.txt`; scripts: `backup-db.sh`, `backup-db.fish`, `restore-db.sh`.
