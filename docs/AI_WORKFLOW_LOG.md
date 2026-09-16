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


## Interlude — Local admin access

**Tool:** Claude Code (Sonnet) → migrations, `accounts/admin.py`, `employees/admin.py`

Requested outside the build guide's step sequence: real migrations applied to the dev
database (not just the ephemeral one pytest builds), a running server, and a superuser, so
the admin site could actually be checked by hand before starting Step 6.

**My call:** flagged that the admin site would come up empty without registrations — Django
doesn't auto-register a swapped-out custom user model, and nothing else was registered
either — and asked before adding them.

**Accepted:** the default `UserAdmin` references a `username` field our email-only model
doesn't have, so it needed a subclass overriding `fieldsets`/`add_fieldsets` rather than
plain registration.

**Noted for later:** a freshly created file isn't picked up by Django's autoreloader until
the next restart — it only watches already-imported modules — so the new `admin.py` needed
`docker compose restart web` before it took effect on the already-running server.

**Gap in its own verification:** it checked that the admin list pages loaded (200 for each
app's changelist) but never opened an actual change form. `date_joined` uses
`auto_now_add=True`, which Django makes non-editable, but `UserAdmin.fieldsets` still listed
it — a `ModelForm` error that only surfaces on the `User` change page specifically, which
its curl checks never hit. Found by hand, fixed by adding it to `readonly_fields`.


## Step 6 — Period constraints

**Tool:** Claude Code (Sonnet) → `employees/`, `salary/`, `common/constraints.py`

**Overrode:** started scaffolding the `salary` app's tests before `EmploymentPeriod` was
even implemented. Told to finish one model completely — tests, constraints, migration,
admin — before starting the other.

**Accepted:**
- `DateRangeFunc` lives in `common/constraints.py`, not duplicated in `employees` and
  `salary` — the exclusion constraint expression is identical for both models, and this is
  exactly what `common/` was scoped for in the build guide's Layout section.
- Hit a `CheckConstraint.check` deprecation warning (Django 5.2 deprecated `check=` for
  `condition=`); fixed it and regenerated the still-uncommitted migration cleanly rather
  than leaving the warning in place.
- Django's autodetector already chained the cross-app dependency correctly on its own —
  `salary`'s migration depends on `employees`'s latest migration at generation time, which
  transitively requires `btree_gist` — but added the explicit dependency on
  `0002_enable_btree_gist` anyway, per the build guide, so it's visible in the migration
  itself rather than relying on an implicit chain that could break under a future squash.

**My call:** for both models, required admin registration plus an actual end-to-end check —
list page, add-form render, *and* a real form submission — before commit, not just a
page-load check. Direct consequence of the `date_joined` bug slipping past a shallower
check earlier.


## Step 7 — As-of resolution

**Tool:** Claude Code (Sonnet) → `common/resolution.py`

Small, well-specified step — no build-guide gaps, no corrections needed.

**Accepted:** used `EmploymentPeriod` as the concrete test subject, since it's the model
already fully built, even though `resolve_as_of` itself is generic over any period-shaped
queryset — reusable for `SalaryPeriod` once reporting needs it.

**Overrode:** nothing.


## Step 8 — Creating an employee opens periods

**Tool:** Claude Code (Sonnet) → `employees/services.py`, `employees/serializers.py`

Flagged, unprompted, that `EmployeeListCreateView` never called `create_employee` —
`POST /api/employees/` created a bare `Employee` row with no periods, unlike Step 16's
roster upload and Step 17's seed command, both specified to open both periods on creation.
Checked Steps 9–18 to confirm the build guide never revisits this, then asked before fixing
it.

**My call:** wire it now rather than leave the inconsistency for a later step.

**Overrode:** told to wire the fix, it went straight to editing the serializer — skipping
its own established red-first discipline, and leaving Step 8's own green commit
unconfirmed in the process. Corrected: commit the still-pending `create_employee`
implementation first, then a dedicated red test proving the endpoint gap, *then* wire the
fix.

**Accepted:** the fix lives in `EmployeeSerializer.create()`, not the view — `base`,
`allowance`, `yearly_bonus`, `currency`, `salary_effective_from` added as declared
`write_only` serializer fields (not model fields), delegating to `create_employee`. Only
`create()` changes; `update()` (the `PATCH` path) is untouched.


## Step 9 — Recording a salary change

**Tool:** Claude Code (Sonnet) → `salary/services.py`, `salary/views.py`

**Accepted:**
- Applied the Step 8 lesson on its own this time — flagged the `salary-changes` endpoint
  gap unprompted, checked Steps 10–18 itself before reporting it, and followed its own
  red-first discipline for the endpoint fix without needing correction.
- `record_salary_change` normalizes `effective_from` via `DateField().to_python()` before
  comparing it to the open period's start, since callers (including tests) may pass a plain
  string rather than a `date`.

**Overrode:** nothing.


## Step 10 — Corrections

**Tool:** Claude Code (Sonnet) → `salary/models.py`, `salary/services.py`, `salary/views.py`

**My call:**
- Add `created_by` to `SalaryCorrection` — an audit log without attribution isn't much of
  an audit log. Not in the build guide's model definition; added mid-cycle, before any
  green implementation existed.
- Amend the red commit with that addition rather than create a separate one for it, since
  nothing had been built on top of it yet.

**Accepted:** flagged the third instance of the same class of gap (a documented endpoint
never wired to its service in any step) on its own, checked the remaining steps itself, and
followed its own red-first discipline for the fix without needing correction this time.

**Overrode:** nothing.


## Step 11 — Status changes

**Tool:** Claude Code (Sonnet) → `employees/services.py`, `employees/views.py`

**Accepted:**
- Unlike Steps 8–10, this step's endpoints are named directly in the build guide's own
  text, not a separately-discovered gap — built them as part of the same cycle instead of
  flagging them afterward.
- Tested both symmetric invariants from the prose ("cannot be deactivated when already
  inactive, or reactivated when already active"), even though the bullet list only names
  the deactivation side.

**Overrode:** nothing.


## Step 12 — Salary history endpoints

**Tool:** Claude Code (Sonnet) → `salary/views.py`, `salary/serializers.py`

Small, well-specified step — no build-guide gaps, no corrections needed.

**Accepted:** money already serialized as a string without any extra work — DRF's
`DecimalField` defaults to `COERCE_DECIMAL_TO_STRING=True`, and this project has never
configured `REST_FRAMEWORK` settings to override it. The test for this existed to prove the
behavior, not to drive new code.

**Overrode:** nothing.


## Step 13 — Employee list

**Tool:** Claude Code (Sonnet) → `employees/views.py`, `employees/filters.py`

Small, well-specified step — no build-guide gaps, no corrections needed.

**Accepted:**
- Scoped pagination, filtering and search to `EmployeeListCreateView` only, not globally —
  Department/Role/Country lists still return bare arrays, and a global default would have
  broken their existing tests.
- Caught and fixed `UnorderedObjectListWarning` on its own: the paginated queryset had no
  explicit ordering, which Postgres doesn't guarantee is stable across pages. Added
  `.order_by("employee_code")`.

**Overrode:** nothing.


## Step 14–15 — Reports

**Tool:** Claude Code (Sonnet) → `reporting/services.py`, `reporting/views.py`

Two build-guide steps handled together in this log, since they share one endpoint and one
internal helper.

**My call:**
- Deferred `GET /api/reports/{name}/` until Step 15's reports existed too, rather than
  building it half-finished against just Step 14's two reports.
- Gave `headcount_by_department` (and later `headcount_by_country`) an `excluded_count`
  field too, always `0`, even though neither needs salary resolution — the doc's "every
  response carries `excluded_count`" reads as a blanket rule, not one scoped to payroll
  cost specifically.

**Accepted:**
- Implemented the four Step 15 reports with DB-level `Avg`/`Count` aggregates via a new
  shared `_employed_salary_periods` helper, rather than repeating Step 14's per-employee
  `resolve_as_of` loop four more times — meaningfully more efficient at the project's
  stated ~10,000-employee scale.
- Asked whether to bring Step 14's `total_payroll_cost` onto the same helper for
  consistency; refactored it as its own commit once confirmed, with the existing test
  suite as the safety net — behaviour unchanged, all tests passed without modification.
- Money and the `as_of` date in the raw report-dict responses serialize correctly for
  free, since DRF's default `JSONEncoder` already handles `Decimal` and `date` — same
  story as Step 12's string-serialization test.


## Step 16 — Roster upload

**Tool:** Claude Code (Sonnet) → `imports/services.py`, `imports/views.py`

Picked up in a fresh session after a context clear; the service-level test scaffolding
(`imports/tests/test_services.py`, `conftest.py`, a stub `import_roster`) already existed on
disk, untracked, from earlier work this conversation has no record of. Ran it first to
confirm it still failed for the right reason (a stub returning `None`) before committing it
as red.

**Accepted:**
- Flagged the fourth instance of the same class of gap as Steps 8–10 — `POST
  /api/imports/roster/` is in the API table but Step 16's own text only specifies the
  service — checked Steps 17–18 itself to confirm the route is never wired later, and wired
  it as its own red-green cycle without asking, per Step 11's note that this class of gap
  stopped needing a check-in.
- Enforced the row cap off the sheet's dimension metadata (`ws.max_row`) rather than by
  counting through an iterator, so a 10,001-row file is rejected without reading any row
  data — matching the read-only-mode memory requirement rather than just satisfying it for
  valid files.
- Excluded `hire_date` from the "salary is not modified" carve-out on existing-code updates:
  the spec's exclusion list is base/allowance/yearly_bonus/salary_effective_from, and
  hire_date isn't a salary field, so it updates with the rest of the demographics.
- Reused `create_employee` for new rows instead of duplicating the
  employee-plus-two-periods logic — the same path Step 8 put behind `POST /api/employees/`,
  so roster-created employees open both periods identically to that endpoint.

**Overrode:** nothing.


## Step 17 — Seed data

**Tool:** Claude Code (Sonnet) → `employees/management/commands/seed_data.py`

Presented the command design before writing anything — location, what gets seeded and in
what order, how salary history and the active/inactive mix get built, and one explicit open
question — rather than building it and reporting back.

**My call:** whether `seed_data` should be safe to re-run against a non-empty dev database.
Chose clearing `Employee` and reference data first over failing loudly on non-empty tables —
convenience for repeated local resets outweighs the "employees are never deleted" domain
rule here, since that rule is about the API layer, not a dev-only reset tool.

**Accepted:**
- Deactivating a fixed ratio (every 7th employee) instead of a per-employee random draw —
  a Bernoulli coin flip at low `--count` values in tests risks a rare run with zero
  inactive employees, which would make the "mix of active and inactive" assertion flaky
  without being wrong.
- Capping every generated date (initial salary, later changes, deactivation) at today,
  which is what makes the zero-exclusion assertion hold without extra bookkeeping: a
  still-active employee's most recent salary period is never closed, so it always resolves
  as of today.
- Fixed lists for department and role names rather than Faker output — Faker has real
  country data but no provider for job-function department/role naming, and generating
  either from word-salad providers would produce nonsense reference data.
- Building emails from `first.last{index}` rather than Faker's `unique` email provider, so
  uniqueness holds by construction instead of by exhaustion risk at higher `--count` values.

**Overrode:** nothing.

**Overrode:** nothing.


## Frontend design — API gaps found while documenting

**Tool:** Claude Code (Sonnet) → `docs/frontend_developer_doc.md`, plus `employees/serializers.py`,
`config/settings.py`, `accounts/views.py`, `reporting/views.py`

Asked for a frontend build guide in the same ordered-steps format as the backend one,
reading the actual serializers and views for response shapes rather than inferring them,
with a real example response and both 400 shapes for every endpoint the frontend calls.

**Conflicts it surfaced, all real gaps against what the four pages need:**
- `EmployeeSerializer` returned bare department/role/country foreign-key ids and no status
  field at all — the employee list and detail pages need names and an active/inactive
  badge, and nothing in the API exposed either. Flagged before writing a line of the doc.
- No `REST_FRAMEWORK` default permission was ever set — only `/me/` and salary-corrections
  actually enforced `IsAuthenticated`; every other endpoint, including employee and salary
  writes, was `AllowAny` by omission, despite `requirements.md` scoping this to a single
  authenticated user.
- While capturing real examples against the running API instead of reading the serializer
  and guessing, it caught a third on its own: report endpoints return `Response(result)` on
  a plain dict, which skips `DecimalField`'s string coercion, so DRF's encoder silently
  falls back to `float(obj)` for any `Decimal` — the one place in the whole API where money
  crossed the wire as a JS float instead of a string.

**My calls:**
- All three: fix the backend now rather than just document the gap, test-first, one change
  at a time, each committed as its own red/green pair.
- The auth and report-money fixes are `fix:` commits, not `feat:` — both close a gap against
  behaviour the project already committed to (single authenticated user; money never a
  float), not new functionality.
- Resolved a contradiction in my own brief before it wrote anything: I'd asked both for the
  doc to interleave each page's static layout with its integration ("don't group all the
  static pages together") and for it to have two literal phases (all statics, then all
  integration). Picked interleaved steps, with "phase" as an explanatory note rather than a
  document section.

**Accepted:**
- Verified assumptions against the live dev containers rather than the code alone — logged
  in with a throwaway user, hit every endpoint with curl, and used the actual captured JSON
  (including exact DRF validation wording, e.g. "employee with this employee code already
  exists.") as the doc's examples, cleaning up the throwaway data afterward.
- Fixing the global-auth gap meant updating every existing test that called the API
  unauthenticated (35 call sites across 5 apps) to authenticate first, rather than weakening
  the new behaviour to keep them passing.
- Quantizing report averages to 2 decimal places before stringifying, since Postgres `AVG`
  widens scale (`50000.000000000000`) in a way a `DecimalField` would normally hide.

**Overrode:** nothing.