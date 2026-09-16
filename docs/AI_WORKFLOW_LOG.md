# AI Workflow Log

Running record of AI use: what I asked for, what I kept, what I overrode.

---

## Requirements

**Tool:** Claude Opus 5 (conversational) → `requirements.md`

Used as an adversarial reviewer rather than a generator. I brought my draft scope and the
client's reply confirming currency, salary structure, salary history and reporting scope
were mine to decide; worked through each until settled.

**Accepted:**
- Flat 10% deduction with no threshold — my original threshold created a cliff where an
  employee just above it takes home less.
- Reports fail loudly on missing history rather than silently omitting employees. I'd
  argued this was the uploader's problem; behaviour on bad input is the system's.
- Change vs correction as two distinct operations, since only one rewrites history.
- Allowance instead of HRA, which is India-specific in a multi-country org.

**Overrode:**
- Cut the document from eight pages to one. The brief asked for a one-pager and Claude
  optimised for completeness against an explicit constraint.
- Rejected a denormalised current-salary pointer I'd proposed, then caught Claude writing
  it back in after misreading me. Generated docs need reading, not skimming.
- Removed a section defending an unchallenged decision — padding in a one-page doc.
- Kept implementation detail (testing, money types, hosting) out of requirements; it
  belongs in the developer docs.

**My calls:**
- Time-aware reporting, accepting the added scope, because point-in-time reporting is what
  the spreadsheet can't do.
- Gross for all aggregates; net only on individual records.
- Cut historical salary import on time grounds, documented with reasoning.


## Project standards

**Tool:** Claude Opus 5 (conversational) → `CLAUDE.md`, `backend/CLAUDE.md`

Defined the working agreement, domain invariants and code conventions before writing any
code, so the rules exist ahead of the tooling that follows them.

**My calls:**
- Monorepo with nested context files — root for shared rules, `backend/` for stack
  specifics. Keeps each file short and scoped to what a reader is touching.
- Service layer for domain logic. The salary operations aren't CRUD and shouldn't sit in
  views or model methods.
- Type hints as documentation, no type checker. Scoped mypy over a Django codebase costs
  more than it returns on a build this size.
- Commit at green, not at red. Red commits would make the TDD cycle visible but leave
  broken states in history; small green commits carry the same signal without that cost.

**Practice:** tests written first, committed at green alongside the implementation that
satisfies them, refactors as separate commits.


## Backend design

**Tool:** Claude Opus (conversational) → `docs/backend_developer_doc.md`

Worked through the schema and API surface, then wrote the backend doc as an ordered build
sequence rather than a specification — each step being one red-green cycle with its tests
and acceptance stated.

**Accepted:**
- Separate `EmploymentPeriod` table rather than a boolean flag, so historical headcount
  resolves status as of the reported date instead of today's.
- Exclusion constraints with `btree_gist`. I initially wanted to skip them as unfamiliar and
  validate in Python; the constraint holds regardless of write path, which Python validation
  doesn't.
- Corrections amend amounts only. Editing period dates is inherently a multi-period
  operation and became a documented scope exclusion.
- `AbstractBaseUser` with a custom manager, no link to `Employee` — employees are records,
  not accounts.

**Overrode:**
- Rejected the first draft's specification format. A build sequence suits how the work is
  actually done and produces commit history sized to one behaviour.
- Switched to committing failing tests before implementation, against the advice to commit
  at green. Broken commits in history are a real cost; visible TDD is worth more here.
- Country as a reference table rather than choices, for consistency with department and
  role across the API, frontend and upload validation.

**My calls:**
- Generic views for CRUD, APIViews for operations and reports, URLs declared by hand so the
  absence of DELETE routes is visible.
- Session auth over JWT — statelessness and multiple clients are both out of scope.
- Apps split by domain with a shared `common/` for interval logic used by both period models.


## Step 1 — Skeleton

**Tool:** Claude Code (Sonnet) → project scaffolding

**Overrode:** Nothing. It stopped twice rather than guessing, which is what CLAUDE.md asks
for.

**Conflicts it surfaced, both real gaps in my build guide:**
- Django cannot boot with `AUTH_USER_MODEL` pointing at a model that does not exist —
  `contrib.auth`'s `AppConfig.ready()` calls `get_user_model()` unconditionally. My step 1
  specified the setting with no model. Resolved with a field-only stub; the manager stays
  test-driven in step 2.
- The database smoke test used `@pytest.mark.django_db`, which builds a test database via
  migrate — contradicting "no migrations in step 1". Rewritten as a plain psycopg
  connection using the same settings, which still proves `DB_HOST` resolves.

**My call:** accepted a stub model in step 1 rather than revising the build guide. A bare
class declaration is scaffolding, not behaviour, so nothing testable was written without a
test.


## Step 2 — User model

**Tool:** Claude Code (Sonnet) → `accounts/`

**Conflict it surfaced:** three of the four tests errored during test-database setup rather
than failing on the assertion — `accounts` had no migration, so `PermissionsMixin`'s M2M
tables were created by syncdb before `auth`'s own migrations ran. Step 1 forbade
`makemigrations` and Step 2 was silent on it, so it stopped and asked.

**My call:** authorised the initial migration. The Step 1 prohibition existed to stop
`AUTH_USER_MODEL` being baked into a migration before the setting was correct; that was
settled, so the prohibition had outlived its purpose. A build-guide gap, not an overreach.

**Overrode:** nothing.


## Step 3 — Session authentication endpoints

**Tool:** Claude Code (Sonnet) → `accounts/` (views, urls, services), `config/` (urls,
settings)

**My call:** built one endpoint at a time — login, then `me`, then `logout` — each reviewed
and committed green on its own, rather than the build guide's single red/green pair for the
whole step. Smaller review surface per commit.

**Accepted:**
- The 401-vs-403 question on `me` settled by checking DRF's actual source rather than by
  recollection: `get_authenticate_header` only consults the first configured authenticator,
  and `SessionAuthentication` returns no challenge header, so plain `IsAuthenticated` gives
  403 for anonymous requests with no extra settings needed.
- `CORS_ALLOWED_ORIGINS` read from an env var, empty by default — a decision made back
  during Step 1 planning (production serves the frontend same-origin behind nginx), carried
  forward and implemented here.

**Overrode:** it reused the `ClassVar` annotation from Step 2's `REQUIRED_FIELDS` fix to
silence ruff's RUF012 on DRF's `permission_classes`, without checking whether it still fit.
It doesn't — no DRF code annotates declarative class attributes that way, and the same
pattern (`permission_classes`, serializer `fields`, filterset fields) recurs constantly in a
Django/DRF codebase. Ignored RUF012 project-wide instead of annotating every occurrence.

Two process rules added along the way, now in root `CLAUDE.md`: every commit needs a body,
not just a subject line; and the assistant shows the proposed commit message up front rather
than waiting to be asked.


## Step 4 — Reference data

**Tool:** Claude Code (Sonnet) → `employees/` (models, serializers, views, urls)

Another build-guide gap, smaller than Steps 1–2: `Country` isn't listed anywhere in the
Layout section's app breakdown, unlike `Department`/`Role` which are explicitly placed under
`employees/`. It flagged this and asked before writing anything.

**My call:**
- `Country` lives in `employees/` too — the same app as `Department`/`Role`, and where
  `Employee`'s FK to it lands in Step 5 anyway.
- Split the step in two: models and their tests first, endpoints afterwards, continuing the
  one-piece-at-a-time rhythm from Step 3.

**Accepted:** no migration needed for any of the three models — none has a cross-app
dependency, so `syncdb` builds their tables cleanly for the test database without one, unlike
`accounts` in Step 2.

**Overrode:** nothing.


## Step 5 — Employee

**Tool:** Claude Code (Sonnet) → `employees/` (models, serializers, views, urls)

**Overrode:** asked for "a basic Employee model class so tests fail on assertion, not import
error," it wrote the full model from the build guide instead of a literal empty stub —
reading "basic" as "the straightforward one," not "the minimal one." Corrected to a bare
`class Employee(models.Model): pass`, which is what actually made the point: import
succeeds, and whichever tests aren't satisfied yet fail on real assertions instead of a
collection error.

**My call:** asked up front for the endpoints to be built and committed one at a time,
rather than letting that pacing get discovered mid-step the way it was in Step 3.

**Accepted:** no migration needed for `Employee` either — its three foreign keys
(department, role, country) are all intra-app, so `syncdb` orders table creation the same
way it did for Step 4's reference tables.