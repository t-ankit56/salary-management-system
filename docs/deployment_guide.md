# Deployment Guide

## Local development

```
docker compose up -d                            # start db and web (Django runserver)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data --count 200   # local dev data
docker compose exec web pytest                  # backend tests
cd frontend && npm install && npm run dev        # frontend dev server (Vite)
```

Backend: http://localhost:8000. Frontend dev server: http://localhost:5173.

## Production

Architecture: Docker Compose runs Postgres and a gunicorn-served Django app on the host,
both bound to `127.0.0.1` only. nginx runs directly on the host (not containerized) and is
the only thing exposed publicly — it reverse-proxies `/api/` and `/admin/` to gunicorn,
serves `/static/` from a bind-mounted `staticfiles` folder, and serves the built React app
for everything else with SPA fallback to `index.html`. TLS is handled by Let's Encrypt via
`certbot --nginx`.

### One-time host setup

1. Install Docker Engine + the compose plugin (see Docker's official apt repo
   instructions), plus `nginx`, `certbot`, and `python3-certbot-nginx`.
2. Clone this repo to `/opt/salary-manager`.
3. Create `/opt/salary-manager/.env` (never committed) with production values:
   ```
   DJANGO_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(50))">
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=<your domain>
   DB_NAME=salary_management
   DB_USER=postgres
   DB_PASSWORD=<generate a strong password>
   DB_HOST=db
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=
   CSRF_TRUSTED_ORIGINS=https://<your domain>
   ```
   `CORS_ALLOWED_ORIGINS` stays empty in production: nginx serves the frontend and API
   from the same origin, so no cross-origin requests need allowing.

### Deploy / redeploy

```
cd /opt/salary-manager
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

First deploy only — seed data and create the admin login:

```
docker compose -f docker-compose.prod.yml exec web python manage.py seed_data --count 10000
docker compose -f docker-compose.prod.yml exec \
  -e DJANGO_SUPERUSER_EMAIL=<admin email> \
  -e DJANGO_SUPERUSER_PASSWORD=<generated password> \
  web python manage.py createsuperuser --noinput
```

`seed_data` always creates four labeled demo employees alongside the random ones —
`DEMO001` (full multi-year salary history), `DEMO002` (a raise effective in the future, so
"current salary" and "most recent record" deliberately disagree), `DEMO003` (a correction
applied to a past period), and `DEMO004` (deactivated, not deleted). Search for `DEMO` in
the employee list to find them.

Build the frontend (no Node install needed on the host — runs in a throwaway container):

```
docker run --rm -v /opt/salary-manager/frontend:/app -w /app node:20 sh -c "npm ci && npm run build"
```

### nginx + TLS

```
sudo cp deploy/nginx.conf /etc/nginx/sites-available/salary-manager
sudo ln -s /etc/nginx/sites-available/salary-manager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d <your domain>
```

`certbot --nginx` rewrites the site config to add the HTTPS server block and HTTP→HTTPS
redirect, and installs a systemd timer for renewal.

### Firewall

```
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Verify

- `docker compose -f docker-compose.prod.yml ps` — both containers `Up`.
- `curl -I https://<your domain>/` — 200/301 over HTTPS.
- Log into `/admin/` with the superuser; load the app and confirm login + API calls work.
- Restart resilience: `docker compose -f docker-compose.prod.yml restart` (or a VM reboot)
  brings both containers back up automatically (`restart: unless-stopped`).
