# Backend — Conventions

Django REST API for the salary management system. Project-wide standards, including the
working agreement and shared domain rules, are in the root `CLAUDE.md`.

Data model, domain operations and API surface: `../docs/backend_developer_doc.md`

---

## Stack

Python 3.12 · Django · Django REST Framework · PostgreSQL · pytest · ruff

Everything runs in Docker. Tests, migrations and shells run inside the container, never on
the host.

## Structure

```
backend/
  config/               Django project package — settings, urls, wsgi, asgi
  common/               shared app; currently holds the Step 1 smoke tests
  accounts/             accounts.User stub (fields only; manager arrives in Step 2)
  employees/            registered in INSTALLED_APPS, no files yet
  salary/               registered in INSTALLED_APPS, no files yet
  reporting/            registered in INSTALLED_APPS, no files yet
  imports/              registered in INSTALLED_APPS, no files yet
  manage.py
  requirements.txt
  requirements-dev.txt
  pyproject.toml        pytest and ruff configuration
  Dockerfile
  .dockerignore
```

`docker-compose.yml` and `.env` / `.env.example` live at the repo root, one level up —
`docker-compose.yml` builds `web` from `backend/` but is shared across services (a future
frontend included).

## Commands

Everything runs through `docker compose exec`, from the repo root — never on the host.

```
docker compose up -d                            # start db and web
docker compose down                             # stop and remove containers
docker compose exec web pytest                  # run the test suite
docker compose exec web ruff check .             # lint
docker compose exec web ruff format .            # format
docker compose exec web ruff format --check .    # check formatting without writing
docker compose exec web python manage.py shell -c "<code>"   # one-off shell commands
```

## Data integrity

The following are enforced by database constraints, not by application code alone:

- No overlapping salary periods per employee — exclusion constraint, requires `btree_gist`.
- Exactly one open-ended period per employee — partial unique index on open periods.
- `effective_to` is null or after `effective_from` — check constraint.
- Company employee ID is unique.

Do not relax or remove a constraint to work around a failing test. They are load-bearing:
they guarantee correctness regardless of which code path writes the data, including the
seed script and bulk upload.

Salary periods are half-open: `effective_from` is included, `effective_to` is the first day
not covered. A raise on date D closes the previous period at D and opens the new one at D,
with no date arithmetic.

Recording a salary change closes one period and opens another in a single transaction. A
partially applied change leaves an overlap or a gap.

## Code conventions

- Business logic lives in a service layer, not in views, serializers or model methods.
  Services own transaction boundaries and are testable without HTTP.
- Views stay thin: parse, delegate to a service, serialise the result.
- Money is `Decimal` in Python and `NUMERIC` in Postgres. Serialise as a string, not a JSON
  number.
- Type hints on service functions and public interfaces. Documentation, not enforced —
  there is no type checker in this project.
- Python 3.12 syntax: `X | None`, built-in generics (`list[str]`), no `typing.List` or
  `typing.Optional`.
- `ruff check` for linting, `ruff format` for formatting. Both run before committing.
- Tests mirror the structure of the code they cover.

## Out of bounds

- Do not edit migrations that are already committed. Write a new one.
