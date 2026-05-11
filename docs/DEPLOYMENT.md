# Deployment Guide

## Recommended First Host

Use Render or Railway for the first hosted version. The included `render.yaml` targets Render with:

- Python web service
- `uvicorn ayen_ode.server:app`
- persistent disk mounted at `/var/data`
- `AYEN_ODE_DB_PATH=/var/data/ayen_ode.db`

SQLite is a good v1 choice because it keeps setup simple. The important production requirement is that the database file lives on a persistent disk, not the disposable app filesystem.

## Environment Variables

Required for hosted deployment:

```text
ANTHROPIC_API_KEY=sk-ant-...
AYEN_ODE_DB_PATH=/var/data/ayen_ode.db
```

Optional:

```text
APP_USERNAME=
APP_PASSWORD=
ALLOWED_IPS=
AYEN_ODE_HOST=0.0.0.0
AYEN_ODE_PORT=8000
AYEN_ODE_RELOAD=0
PORT=8000
```

Most hosts set `PORT` automatically. Disable uvicorn auto-reload in production with `AYEN_ODE_RELOAD=0`.

## Expected URLs

Health check:

```text
https://<your-domain>/health
```

Login page:

```text
https://<your-domain>/
```

Dashboard (after login):

```text
https://<your-domain>/dashboard
```

## Security Notes

V1 is intended for private testing. Before other users connect:

- add OAuth or another supported authentication layer
- add rate limiting
- separate data by user/account
- create regular backups of the SQLite file

## Smoke Test

After deploying, hit the health endpoint and one read-only API route:

```powershell
curl https://<your-domain>/health
curl -H "Authorization: Bearer <APP_PASSWORD>" https://<your-domain>/api/worlds
```
