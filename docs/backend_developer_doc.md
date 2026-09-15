# Backend Build Guide

The backend built as an ordered sequence of steps. Each step is one red-green-refactor
cycle: write the failing test and commit it red, implement the minimum that passes and commit
it green, then refactor as a separate commit if needed.

Scope and reasoning: `requirements.md`
Working agreement and domain invariants: root `CLAUDE.md` and `backend/CLAUDE.md`

Order matters. Later steps depend on invariants proven by earlier ones.

---

## Stack

Python 3.12 · Django 5.2 · DRF 3.18 · PostgreSQL 18 · psycopg 3 · pytest · ruff · Docker

```
requirements.txt      Django, djangorestframework, psycopg[binary],
                      django-cors-headers, django-filter, openpyxl,
                      gunicorn, python-dotenv
requirements-dev.txt  pytest, pytest-django, factory-boy, Faker, ruff
```

## Layout

```
backend/
  config/       settings, root urls, wsgi
  common/       shared interval logic — as-of resolution, overlap checks
  accounts/     User
  employees/    Employee, Department, Role, EmploymentPeriod
  salary/       SalaryPeriod, SalaryCorrection
  reporting/    report queries and views (no models)
  imports/      Excel roster upload (no models)
```

Each app: `models.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, `tests/`.
Business logic lives in `services.py`; views parse, delegate and serialise.

---

# Step 1 — Skeleton

Scaffolding only. No models, no migrations run.

**Django project.** `config` as the project package. Create all apps now so none has to be
added mid-build: `common`, `accounts`, `employees`, `salary`, `reporting`, `imports`.
Register them in `INSTALLED_APPS` along with `rest_framework`, `corsheaders` and
`django_filters`.

**`AUTH_USER_MODEL = "accounts.User"` in settings before anything else.** Django bakes the
user model into every migration that references it. Setting this after a migration has run
means dropping the database and starting over. The `accounts` app must exist now even though
the model arrives in step 2.

**Requirements files**, pinned exactly:

```
# requirements.txt
Django==5.2.17
djangorestframework==3.18.1
psycopg[binary]==3.3.5
django-cors-headers==4.9.0
django-filter==26.1
openpyxl==3.1.5
gunicorn==26.2.0
python-dotenv==1.2.3

# requirements-dev.txt
-r requirements.txt
pytest==9.1.1
pytest-django==4.14.0
factory-boy==3.3.3
Faker==40.39.0
ruff==0.16.7
```

**Docker.** `Dockerfile` on `python:3.12-slim`, installing both requirements files.
`docker-compose.yml` with two services:

- `db` — `postgres:18-alpine`, a named volume for data, credentials from environment
- `web` — built from the Dockerfile, bind-mounting the source for autoreload, depending on
  `db`, port 8000 exposed

**Database settings** read from environment variables. `DB_HOST` is the compose service
name `db`, not `localhost` — inside the network, `localhost` is the web container itself.
Use `python-dotenv` with a `.env` file, and add `.env` to `.gitignore`.

**pytest.** Configure in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["test_*.py"]
```

Without `DJANGO_SETTINGS_MODULE`, pytest cannot load Django and every test errors on import.

**ruff.** Configure in `pyproject.toml`: line length 100, target `py312`, and exclude
`migrations/`.

**Test:** one trivial test — asserting the Django settings load and the database connection
works.

**Done:** `docker compose up` brings both services up, `docker compose exec web pytest` runs
green, and `docker compose exec web ruff check .` is clean. Nothing has been migrated yet.

**Commit:** `chore: project skeleton with docker, pytest and ruff` (scaffolding only, no red commit)

---

# Step 2 — User

```python
class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
```

`REQUIRED_FIELDS` is empty because it means "in addition to `USERNAME_FIELD` and password".
Listing `email` there breaks `createsuperuser`.

No relationship to `Employee`. Employees do not log in.

**Tests:** email is normalised and password hashed; `create_superuser` sets both flags;
missing email raises `ValueError`; email is unique.
**Done:** `createsuperuser` works end to end. Verify this manually before moving on.
**Commit:** `test: user manager creates users and superusers (red)` → `feat: custom user model with email authentication`

---

# Step 3 — Authentication endpoints

Session authentication. `POST /api/auth/login/`, `POST /api/auth/logout/`,
`GET /api/auth/me/`.

Configure `django-cors-headers` with `CORS_ALLOW_CREDENTIALS = True` and the frontend
origin allowed.

**Tests:** valid credentials establish a session; invalid returns 401; `me` returns the user
when authenticated and 403 when not; logout ends the session.
**Commit:** `test: login, logout and current user (red)` → `feat: session authentication endpoints`

---

# Step 4 — Reference data

```python
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
```

```python
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
```

All three share the same shape for consistency: one reference pattern for the frontend, one
validation path in the upload.

`is_active` controls visibility in selection lists. It is not a soft delete — deletion of an
entry in use is prevented by `PROTECT` on the foreign key, added in the next step.

Endpoints: list and create for departments and roles; list only for countries, which are
seeded rather than user-managed. Retrieve and update by id for all three.

**Tests:** names unique; inactive entries excluded from list responses; countries has no
create route.
**Commit:** `test: reference data uniqueness and active filtering (red)` → `feat: department, role and country reference data`

---

# Step 5 — Employee

```python
class Employee(models.Model):
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="employees")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="employees")

    hire_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

`employee_code` is the business key — what bulk upload matches on and what the HR Manager
recognises. The database `id` is internal.

Endpoints: `GET, POST /api/employees/` and `GET, PATCH /api/employees/{id}/`. No DELETE
route. Generic views, URLs declared by hand so the absence of DELETE is visible in
`urls.py`.

**Tests:** `employee_code` and `email` unique; a department in use cannot be deleted; DELETE
on an employee returns 405.
**Commit:** `test: employee uniqueness and protected reference data (red)` → `feat: employee records`

---

# Step 6 — Period constraints

This is the foundation for everything after it. Do not proceed until every test here passes.

Two models with identical interval shape:

```python
class EmploymentPeriod(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employment_periods")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SalaryPeriod(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_periods")

    base = models.DecimalField(max_digits=12, decimal_places=2)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")

    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

`SalaryPeriod` is a snapshot: each row holds complete compensation for its period, not a
delta. Resolving a salary for a date is therefore one row lookup.

Enable `btree_gist` in its own migration. `makemigrations` cannot generate this — there is
no model change to detect — so create it empty and fill it in:

```
python manage.py makemigrations employees --empty --name enable_btree_gist
```

```python
from django.contrib.postgres.operations import BtreeGistExtension

class Migration(migrations.Migration):
    dependencies = [("employees", "<previous migration>")]
    operations = [BtreeGistExtension()]
```

**Both constraint migrations must declare this as a dependency, added by hand.** Django
orders migrations by the dependency graph, not by filename, and `makemigrations` has no way
to know the constraints need the extension. Without the dependency it may still work
locally, because a fresh database happens to apply them in order, and then fail on another
machine or on deployment.

In the generated `employees` constraint migration:

```python
dependencies = [("employees", "000X_enable_btree_gist")]
```

And in the generated `salary` one, a cross-app dependency:

```python
dependencies = [
    ("salary", "<previous migration>"),
    ("employees", "000X_enable_btree_gist"),
]
```

Editing freshly generated migrations before committing them is routine. The rule against
editing migrations applies to ones already committed and applied.

Three constraints on each model:

```python
CheckConstraint(
    check=Q(effective_to__isnull=True) | Q(effective_to__gt=F("effective_from")),
    name="<table>_end_after_start",
)

UniqueConstraint(
    fields=["employee"],
    condition=Q(effective_to__isnull=True),
    name="one_open_<table>_per_employee",
)

ExclusionConstraint(
    name="no_overlapping_<table>",
    expressions=[
        ("employee", RangeOperators.EQUAL),
        (DateRangeFunc("effective_from", "effective_to", Value("[)")), RangeOperators.OVERLAPS),
    ],
)
```

```python
class DateRangeFunc(Func):
    function = "daterange"
    output_field = DateRangeField()
```

An exclusion constraint generalises `UNIQUE`: it rejects a row when all listed operators
hold against an existing row — here, same employee *and* overlapping period. It is backed by
a GiST index, which understands range overlap; btree does not. `btree_gist` supplies the
integer-equality operator class GiST lacks, letting both comparisons share one index.

The partial unique index enforces the single-open-period invariant and is also the index
used to resolve current salary, so it serves twice.

**Tests, at database level, for both models:** overlapping periods rejected; a second open
period rejected; `effective_to` before `effective_from` rejected; adjacent half-open periods
sharing a boundary date accepted; different employees' overlapping periods accepted.

**Commit:** `test: period overlap, single open period and bounds (red)` → `feat: salary and employment period constraints`

---

# Step 7 — As-of resolution

Shared function in `common/`. For an employee and date D, the applicable period satisfies
`effective_from <= D` and (`effective_to` is null or `effective_to > D`).

The constraints guarantee at most one match. Zero matches is possible and callers must
handle it.

Current state is D = today. The most recent row is **not** a substitute — a future-dated
change makes those different answers.

**Tests:** a date inside a closed period; a date inside the open period; a boundary date
resolves to the later period; a date before all periods returns nothing; a future-dated
period is not returned for today.
**Commit:** `test: period resolution by date (red)` → `feat: as-of-date period resolution`

---

# Step 8 — Creating an employee opens periods

Creating an employee opens an `EmploymentPeriod` at their hire date. Employee creation also
accepts opening salary values and a salary effective date, opening a `SalaryPeriod`.

Both in the service layer, in one transaction with the employee row.

**Tests:** creating an employee produces an open employment period starting at hire date;
opening salary produces an open salary period; a failure creates none of the three.
**Commit:** `test: employee creation opens both periods (red)` → `feat: open employment and salary periods on employee creation`

---

# Step 9 — Recording a salary change

Service function, transactional.

A change applies from a date forward. Close the open period by setting `effective_to` to
that date, then insert a new open period with `effective_from` set to the same date. Same
value on both — half-open periods mean no date arithmetic.

**Close before inserting.** The reverse order creates a transient overlap that trips the
exclusion constraint mid-transaction.

A change may be backdated, but not earlier than the current open period's start. Rewriting a
settled period is a correction, not a change.

Catch `IntegrityError`, match on constraint name, return a 400 with a readable message. The
service validates for overlap first — the constraint is the guarantee, not the error
message.

**Tests:** the open period is closed at the effective date; a new open period is created;
both visible in one transaction; a failure leaves neither; backdating before the open
period's start is rejected; a forward-dated change does not alter today's resolved salary.
**Commit:** `test: salary change closes and opens periods atomically (red)` → `feat: record salary change`

---

# Step 10 — Corrections

```python
class SalaryCorrection(models.Model):
    salary_period = models.ForeignKey(SalaryPeriod, on_delete=models.CASCADE, related_name="corrections")

    previous_base = models.DecimalField(max_digits=12, decimal_places=2)
    previous_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    previous_yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2)

    new_base = models.DecimalField(max_digits=12, decimal_places=2)
    new_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    new_yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2)

    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

A correction amends amounts in place and writes a log row. Dates are never changed — no new
period, no boundary adjustment. Reason is required.

Amounts only are logged, because dates are immutable.

**Tests:** amounts updated in place; dates unchanged; a correction row written with previous
and new values; missing reason rejected; a past-date report reflects the corrected amounts.
**Commit:** `test: corrections amend amounts and log previous values (red)` → `feat: salary corrections with audit log`

---

# Step 11 — Status changes

Deactivate closes the open `EmploymentPeriod` at an effective date. Reactivate opens a new
one. An employee cannot be deactivated when already inactive, or reactivated when already
active.

Endpoints: `POST /api/employees/{id}/deactivate/` and `.../reactivate/`, both requiring an
effective date.

**Tests:** deactivation closes the open period; reactivation opens a new one; deactivating an
inactive employee is rejected; status resolves correctly before, during and after a gap.
**Commit:** `test: status transitions and resolution across gaps (red)` → `feat: employee deactivation and reactivation`

---

# Step 12 — Salary history endpoints

`GET /api/employees/{id}/salary-periods/` returning periods with a correction count per
period, and `GET /api/employees/{id}/salary-periods/{pid}/corrections/` returning the log
for one period.

Correction counts are annotated, not fetched per row. The log itself loads on demand.

Money serialises as a string, not a JSON number — JSON numbers are floats in JavaScript.

**Tests:** periods returned newest first with correct counts; corrections endpoint returns
the log; amounts serialise as strings.
**Commit:** `test: salary history with correction counts (red)` → `feat: salary history endpoints`

---

# Step 13 — Employee list

Pagination (default 25), filters on `department`, `role`, `country` and `status`, search
over name and `employee_code`. Use `django-filter`.

Status is resolved as of today via the employment period, not a stored flag.

**Tests:** each filter; search matches both name and code; page size honoured; an inactive
employee appears only under the matching status filter.
**Commit:** `test: employee list filters, search and pagination (red)` → `feat: employee list filtering, search and pagination`

---

# Step 14 — First two reports

Build `total_payroll_cost` and `headcount_by_department` first. Between them they exercise
salary resolution, status resolution and the exclusion rule, so the remaining reports are
variations on proven machinery.

Every report takes an optional `as_of` date, defaulting to today. An employee is included
only if employed on that date with a hire date on or before it.

Gross = base + allowance + yearly_bonus. All aggregates use gross.

**Incomplete data.** Reports never return a figure over a silent subset:

- A date earlier than the earliest `SalaryPeriod.effective_from` is rejected with 400,
  naming the earliest available date.
- An employee employed on the date but with no salary period covering it is excluded and
  counted. Every response carries `excluded_count`.

**Tests:** correct aggregate against a known fixture; `as_of` in the past returns the
historical figure; an inactive employee is excluded; a too-early date returns 400; a missing
salary period increments `excluded_count` rather than being dropped.
**Commit:** `test: payroll cost and headcount with exclusions (red)` → `feat: payroll cost and headcount reports`

---

# Step 15 — Remaining reports

Average salary by department, average salary by country, average bonus by department,
headcount by country. Same resolution and exclusion rules.

**Tests:** per report, correct aggregate and correct grouping.
**Commit:** `test: average salary and bonus aggregates (red)` → `feat: remaining aggregate reports`

---

# Step 16 — Roster upload

`POST /api/imports/roster/`, multipart, synchronous, capped at 10,000 rows.

Columns: `employee_code`, `first_name`, `last_name`, `email`, `department`, `country`,
`role`, `hire_date`, `base`, `allowance`, `yearly_bonus`, `salary_effective_from`.

`salary_effective_from` is required. Without it an imported employee's history begins at the
import date, making every past-date report wrong from the first day.

Upsert on `employee_code`:

- **Not present** — create the employee, open an employment period at hire date, open a
  salary period at `salary_effective_from`.
- **Present** — update demographic fields only. Salary is not modified; salary changes go
  through the salary endpoints.

The upload cannot deactivate an employee.

Validate the whole file before any write: required columns present; no duplicate
`employee_code` or `email` in the file; no `email` belonging to a different employee;
department, role and country match existing records by name; dates parse;
amounts numeric and non-negative; `salary_effective_from` on or after `hire_date`.

All-or-nothing. Errors return row numbers and reasons.

Read with `openpyxl` in read-only mode so memory is proportional to rows, not file size.
Apply in one `atomic()` block.

**Tests:** each validation failure returns a row number; one bad row writes nothing; a valid
file creates employees with both periods; an existing code updates demographics and leaves
salary untouched; a file over the cap is rejected.
**Commit:** `test: roster upload validation and upsert (red)` → `feat: excel roster upload`

---

# Step 17 — Seed data

Faker-based management command. Seeds reference data first — departments, roles and
countries — then employees across them, with several salary periods each and a mix of active
and inactive.

**Tests:** generated data satisfies every constraint; reports run against it with zero
exclusions.
**Commit:** `test: seed data satisfies all constraints (red)` → `feat: faker seed command`

---

# Step 18 — Deployment

Gunicorn with worker timeout raised to 120s. Nginx with `client_max_body_size` and
`proxy_read_timeout` set for the row cap — nginx defaults to 1 MB and will reject uploads
before Django sees them. Static files, environment configuration, production settings.

Verify `btree_gist` can be created on the deployment database. The database user needs
extension-creation privileges.

**Done:** live URL reachable, seed data loaded, an upload completes within the timeout.
**Commit:** `chore: production deployment configuration`

---

# API surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login/` | Log in |
| POST | `/api/auth/logout/` | Log out |
| GET | `/api/auth/me/` | Current user |
| GET, POST | `/api/departments/` | List, create |
| GET, PATCH | `/api/departments/{id}/` | Retrieve, update |
| GET, POST | `/api/roles/` | List, create |
| GET, PATCH | `/api/roles/{id}/` | Retrieve, update |
| GET | `/api/countries/` | List countries |
| GET, POST | `/api/employees/` | List (paginated, filterable), create |
| GET, PATCH | `/api/employees/{id}/` | Retrieve, update demographics |
| GET | `/api/employees/{id}/salary-periods/` | Salary history with correction counts |
| POST | `/api/employees/{id}/salary-changes/` | Record a salary change |
| GET | `/api/employees/{id}/salary-periods/{pid}/corrections/` | Correction log |
| POST | `/api/employees/{id}/salary-corrections/` | Correct a salary period |
| POST | `/api/employees/{id}/deactivate/` | Deactivate |
| POST | `/api/employees/{id}/reactivate/` | Reactivate |
| POST | `/api/imports/roster/` | Excel roster upload |
| GET | `/api/reports/{name}/` | Report, optional `as_of` |

No DELETE on any resource. No PUT or PATCH on salary periods. This is the immutability rule
expressed at the API surface.
