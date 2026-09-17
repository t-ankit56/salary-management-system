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


# Frontend

## Frontend Step 1 — Project skeleton

**Tool:** Claude Code (Sonnet) → `frontend/`

Before scaffolding, asked for the list of pages/modals `frontend_developer_doc.md` calls for
Claude Design to build, then for a ready-to-paste design prompt per page/modal — both done
by reading the doc alone, no code written yet.

**Conflicts it surfaced, all real drift between the doc and what actually installs today:**
- `create-vite`'s current React template pulls in `oxlint` and `@types/react`/
  `@types/react-dom`, none of which are in the doc's Step 1 dependency list.
- `npm install tailwindcss` installs v4 by default, which is CSS-first (`@import
  "tailwindcss"` + `@tailwindcss/vite`, content auto-detected) — no `tailwind.config.js`,
  contradicting the doc's explicit `tailwind.config.js` plus content-glob layout entry.
- The same scaffold installs React 19, while the Stack line said "React 18."
- `vitest run` exits 1 on zero test files by default, contradicting the doc's own "Done"
  criterion that `npm run test` runs zero tests *successfully*.

**My calls:**
- Strip `oxlint` and the `@types` packages rather than keep them — match the doc's dependency
  list exactly rather than accept the scaffold's defaults.
- Keep Tailwind v4 and React 19, both already installed with no conflict against anything
  else in the doc, and update `frontend_developer_doc.md`'s Stack/Layout sections to match,
  rather than downgrading to match the doc as originally written.

**Accepted:** added `passWithNoTests: true` to the Vitest config so the doc's zero-tests
"Done" criterion is literally true (exit code 0), not just true in spirit.

**Overrode:** nothing.


## Frontend Step 2 — Login: static layout

**Tool:** Claude Code (Sonnet) → `frontend/src/pages/LoginPage.jsx`

Asked where to place the finished design before it existed as a file; created a gitignored
`frontend/design/` staging folder once the format (exported HTML) was confirmed, rather than
guessing a location or having it land in shipped `src/`.

**Conflict it surfaced:** the exported file is a Claude Design `.dc.html` artboard — its own
component format (`x-dc`, `sc-if`, a `DCLogic` class) with a working fake submit handler,
local state, and a simulated 600ms failure response. Step 2's own text is explicit that this
step is layout only — "no form state beyond native inputs, no submit handler, no fetch" — so
none of that logic could be carried over as-is.

**Accepted:**
- Stripped the interactive scaffolding down to plain uncontrolled inputs — exactly what
  Step 2's own text specifies, not a judgment call, just a faithful reading of the doc.
- Translated the design's `oklch()` styling to the closest Tailwind palette (slate for
  neutrals, blue-700 for the primary action, red for the reserved error state) rather than
  carrying inline styles or arbitrary oklch values over verbatim, to keep the page idiomatic
  Tailwind like the rest of the app will be.

**Overrode:** nothing.


## Frontend Step 3 — Login: wire to API and central auth

**Tool:** Claude Code (Sonnet) → `api/client.js`, `hooks/useAuth.js`, `App.jsx`,
`pages/LoginPage.jsx`

Wrote all four of the doc's listed tests first in one `App.test.jsx`, ran them to confirm a
real failure (missing modules), committed red, then implemented to green — one cycle, per the
doc's own single red/green commit pair for this step.

**Conflict it surfaced:** `@testing-library/jest-dom`'s setup needs a global `expect` to
attach its matchers to; without `test.globals: true` in `vite.config.js` (not set in Step 1),
the very first test run failed with `ReferenceError: expect is not defined` before any of the
real assertions ran. Added the flag as part of the same red commit, since it's test
infrastructure the doc's Step 1 config simply hadn't needed yet.

**My call:** interrupted mid-flow — before showing the red commit message, started running
`git status`/`git diff` to inspect what would be staged. Corrected: show the proposed commit
message first, before running any git commands at all, not just before the `commit` itself.

**Accepted:** the fourth doc-listed test ("403 from any mocked fetch call") calls `apiFetch`
directly from the test rather than triggering it through a page, since no page fetches
anything yet at this point in the build (`EmployeeListPage` is still Step 1's static stub) —
still a faithful test of the *central* handler, which by design doesn't care which caller
triggered it.

**Overrode:** nothing.


## Frontend Step 4 — Employee list: static layout

**Tool:** Claude Code (Sonnet) → `frontend/src/pages/EmployeeListPage.jsx`

Same `.dc.html` translation pattern as Step 2: read the Claude Design export, stripped its
working state (page-click handlers, per-row dynamic badge-style computation) down to a static
layout with hardcoded rows and hardcoded filter options, per Step 4's own text.

**Conflict it surfaced:** the design rendered "New Employee" as a `<button>`, but the doc's
prose calls it a "link." Built it as a `react-router` `Link` to `/employees/new` rather than
a plain button, following the doc's wording over the design file's markup.

**Accepted:**
- Built "New Employee" as a `Link`, not a button — a direct doc read over the design file's
  markup, not a judgment call.
- Kept the design's 4 sample rows rather than trimming to "a couple," since the doc's own
  wording is approximate and the fuller set shows the badge/column layout better.

**Overrode:** nothing.


## Interlude — Frontend dev server

**Tool:** Claude Code (Sonnet) → background process only, no files changed

Asked to keep `npm run dev` running in the background so pages could be watched live in the
browser as each step landed, rather than started/stopped per step.

**Accepted:**
- Used the project's `run` skill, which found no project-specific launch skill for this repo
  and fell back to its generic "web server" pattern: background launch, then a `curl` smoke
  check against `/` and `/login` to confirm the app actually responds rather than just that
  the process started.
- Left the server running for the rest of the session rather than restarting it per step —
  Vite's dev server hot-reloads on file changes, so no restart is needed between steps.

**Overrode:** nothing.


## Frontend Step 5 — Employee list: wire to API

**Tool:** Claude Code (Sonnet) → `api/employees.js`, `hooks/useEmployees.js`,
`pages/EmployeeListPage.jsx`

**Conflicts it surfaced:**
- The static page's `Link` needs router context; the first test run failed on a router
  context error, not the intended assertion — fixed by wrapping the test's `render()` in
  `MemoryRouter`, then reran to confirm the *real* red (static content still showing).
- Wiring `EmployeeListPage` to real data broke two already-green `App.test.jsx` tests: once
  authenticated, the page now fires its own mount-time fetches (departments/roles/countries/
  employees) that the existing fixed-position/ordered mock queue never accounted for.
- One `EmployeeListPage.test.jsx` assertion (`getByText('Engineering')`) matched twice — the
  table cell and the closed-but-present `<option>` in the department filter both contain the
  literal text.

**Accepted:**
- Rewrote `App.test.jsx`'s mocks from an ordered `mockResolvedValueOnce` queue to a
  URL-matcher function, so future pages adding their own mount-time fetches won't break
  unrelated auth tests again the same way.
- Scoped the ambiguous assertion to `getByRole('cell', ...)` rather than loosening it to
  `getAllByText`, keeping the test specific to what's actually being checked (the table row).
- Paginate by tracking `page` in local filter state and deriving total pages from `count` at
  a fixed size of 25, never reading the response's `next`/`previous` URLs — exactly the doc's
  stated pagination convention, applied here for the first time.

**Overrode:** wrote `api/employees.js` and `hooks/useEmployees.js` before the test, breaking
red-first discipline — the same class of slip Step 8 made on the backend. Self-caught before
anything was committed: wrote the test next regardless, ran it against the still-static page
to confirm a real failure, and noted the out-of-order authoring in the red commit body rather
than pretending the order had been different.


## Frontend Step 6 — Employee detail: static layout

**Tool:** Claude Code (Sonnet) → `pages/EmployeeDetailPage.jsx`,
`components/modals/SalaryChangeModal.jsx`, `components/modals/SalaryCorrectionModal.jsx`,
`components/modals/StatusChangeModal.jsx`

**Conflict it surfaced:** I `/clear`ed the session mid-step, after the four `.dc.html` design
files had already been read and two gaps against the doc identified but before I'd recorded
the resolution anywhere. The recap I pasted back in on resume cut off before showing what I'd
actually decided, so rather than have Claude guess or fabricate my prior answers, it re-derived
both gaps from scratch by rereading the design files against the doc text, and I confirmed
them fresh.

**My call:**
- `EmployeeDetailPage.dc.html`'s header shows only name, code, and status badge; the doc's
  own Step 6 text also calls for department/role/country. Confirmed: add the three fields,
  following the doc's prose over the design markup — same precedent as Step 4's "New
  Employee" link/button call.
- `SalaryChangeModal.dc.html` has no Currency field, but Step 8's real API payload
  (`recordSalaryChange`) requires `currency` in the body. Confirmed: add a Currency field now
  during static scaffolding rather than deferring it to Step 8.
- Flagged a third gap after the page was scaffolded: whether other action buttons should also
  be `Link`s, same pattern as "New Employee." Checked Step 10's own test wording ("the button
  opens `StatusChangeModal`") and Steps 6/8/9's prose, which call Change Salary/Correct
  Salary/Deactivate-Reactivate "buttons" throughout since they open in-page modals rather than
  navigate — only Edit changes the URL (`/employees/:id/edit`). Confirmed: Edit only; the rest
  stay buttons, matching what was already scaffolded.

**Accepted:** Claude's own reasoning that Edit is the only one of the four action buttons that
navigates to a distinct route, and should be a `Link` rather than a `button` — it worked this
out from the doc's routing list before I asked, and I confirmed it without changes once
raised.

**Overrode:** nothing.


## Frontend Step 7 — Employee detail: fetch employee and salary history

**Tool:** Claude Code (Sonnet) → `api/employees.js`, `api/salary.js`, `hooks/useEmployee.js`,
`hooks/useSalaryHistory.js`, `pages/EmployeeDetailPage.jsx`, `pages/EmployeeDetailPage.test.jsx`

Wrote `EmployeeDetailPage.test.jsx` first against the still-static page (three cases:
mount-time fetch of employee + salary history, newest-first ordering with correction counts,
and clicking a nonzero-correction period fetching and showing its corrections log), ran it to
confirm a real red — the fetch-call assertion failed since the static page never calls
`fetch`, and the corrections-click assertion failed for lack of any interactive element.
Implemented `getEmployee` on `api/employees.js`, a new `api/salary.js` (`getSalaryHistory`,
`getCorrections`), and `useEmployee`/`useSalaryHistory` hooks fetching from the `:id` route
param, then wired `EmployeeDetailPage` to them.

**Accepted:**
- The doc doesn't specify how a period's corrections log should display once fetched — added
  a lightweight inline expanded row under the clicked period's `<tr>` (toggled via a
  `Fragment` per row) rather than a separate modal, since Steps 8-10 already own the three
  action modals and this is a read-only expansion, not another form.
- Fixed a latent React key warning: the per-period `<>...</>` shorthand fragment in the
  `.map()` needs an explicit key once it wraps two sibling `<tr>`s (the data row and its
  conditional corrections row) — switched to `<Fragment key={period.id}>`.

**My call:** none — no correction needed this step.

**Overrode:** nothing.


## Fix — Employee list row navigation to detail page

**Tool:** Claude Code (Sonnet) → `pages/EmployeeListPage.jsx`, `pages/EmployeeListPage.test.jsx`

**Conflict it surfaced:** I noticed, after using the live detail page built in Steps 6-7, that
there was no way to reach `/employees/:id` from `/employees` except typing the URL directly,
and asked Claude how to get there — this gap wasn't caught during Steps 4-7 despite neither
the doc's Step 4 text nor `EmployeeListPage.dc.html`'s design script wiring row navigation.

**My call:** whole `<tr>` clickable via `useNavigate`, rather than turning just the employee
code/name cell into a `Link` — confirmed over the alternative when asked.

**Accepted:** wrote the failing test first (a second render helper mounting both `/employees`
and a `/employees/:id` stub route, clicking a row, asserting the stub route rendered) against
the unwired table, confirmed real red, then wired the `onClick`.

**Overrode:** nothing.


## Frontend Step 8 — Salary change modal

**Tool:** Claude Code (Sonnet) → `api/salary.js`, `hooks/useSalaryHistory.js`,
`components/modals/SalaryChangeModal.jsx`, `components/modals/SalaryChangeModal.test.jsx`,
`pages/EmployeeDetailPage.jsx`

Tested the modal in isolation this time (`SalaryChangeModal.test.jsx`, not a page-level test)
since Step 8's four cases are all about the modal's own form/error behaviour, not page wiring.
Wrote it first against the still-static modal, confirmed real red, then implemented
`recordSalaryChange` in `api/salary.js`, turned the modal into a controlled form with a
`{detail}`-banner/field-error split, and added `refetch` to `useSalaryHistory` (extracted via
`useCallback`) so the page can refresh history and close the modal together on success.

**Conflict it surfaced:** the URL assertion in the first test used strict
`.toBe('/api/employees/3/salary-changes/')`, which failed once run — this dev environment's
`VITE_API_BASE_URL` isn't empty, so `apiFetch` prefixes every call with `http://localhost:8000`.
Every other page test in the suite already uses `.toContain(...)` for exactly this reason;
fixed the assertion to match the established pattern rather than changing `apiFetch`.

**Overrode:** nothing.


## Frontend Step 9 — Salary correction modal

**Tool:** Claude Code (Sonnet) → `api/salary.js`, `components/modals/SalaryCorrectionModal.jsx`,
`components/modals/SalaryCorrectionModal.test.jsx`, `pages/EmployeeDetailPage.jsx`

**Conflict it surfaced:** flagged, before writing any code, that Step 9's text ("the modal is
opened from a specific history row, so `salary_period` comes from that row's id") contradicts
Step 6 and the design file, which both fix "Correct Salary" as one of four top-level buttons
with no row selected.

**My call:** chose a per-row trigger over deriving an implicit "current period" — removed the
top-level Correct Salary button from the header (three remain: Change Salary,
Deactivate/Reactivate, Edit) and added a Correct action to each salary history row instead, so
`salary_period` in the request body is that row's own id.

Wrote `SalaryCorrectionModal.test.jsx` first against the still-static modal, confirmed real
red, then implemented `correctSalaryPeriod` in `api/salary.js` and turned the modal into a
controlled form matching `SalaryChangeModal`'s error-handling pattern.

**Conflict it surfaced:** the reason `<textarea>` still carried the native `required`
attribute from Step 6's static scaffold. Once wired to a real submit handler, the browser's
constraint validation silently blocked the submit event before it reached the handler, so the
missing-reason test kept failing even after the rest of the wiring was correct — the server's
own `{"reason": ["This field may not be blank."]}` 400 never got a chance to run. Dropped
`required`, since the project's whole validation model relies on real API response shapes, not
client-side HTML validation.

**Overrode:** nothing.


## Frontend Step 10 — Deactivate and reactivate

**Tool:** Claude Code (Sonnet) → `api/employees.js`, `hooks/useEmployee.js`,
`components/modals/StatusChangeModal.jsx`, `pages/EmployeeDetailPage.jsx`,
`pages/EmployeeDetailPage.test.jsx`

Tested at the page level this time, not in isolation like Steps 8-9's modals — Step 10's three
cases (which mode a given employee's status opens, the employee refetch after success, the
banner error) all depend on `EmployeeDetailPage`'s own state (`employee.status`,
`useEmployee`'s refetch), not just the modal's own form. Wrote all four tests first
(mode/endpoint routing for both active and inactive employees, refetch-updates-badge, and the
already-inactive banner) against the still-demo modal, confirmed real red, then implemented
`deactivateEmployee`/`reactivateEmployee` in `api/employees.js`, added `refetch` to
`useEmployee` (same `useCallback` pattern Step 8 added to `useSalaryHistory`), and turned
`StatusChangeModal` into a controlled form.

**Accepted:** the trigger button and the modal's confirm button share the same label
("Deactivate"/"Reactivate" — the design's own choice, not something added this step), so once
the modal is open there are two same-named buttons in the DOM. Disambiguated in tests with
`getAllByRole(...).at(-1)` rather than adding an unrequested `role="dialog"` wrapper to the
component just to make testing easier.

**Overrode:** nothing.


## Frontend Step 11 — Employee form: static layout

**Tool:** Claude Code (Sonnet) → `pages/EmployeeFormPage.jsx`

Asked to do Steps 11-13 in one pass rather than stopping after each for confirmation. Read
`EmployeeFormPage.dc.html`, translated it to the same design-token pattern used everywhere
else. No submission wired, no tests (matching Steps 2/4/6's no-test precedent for static
layouts).

**Accepted:**
- The design's currency options (USD/GBP/INR/BRL) don't match `SalaryChangeModal`'s
  (USD/EUR/GBP/INR) from Step 8 — used the Step 8 list here instead of the design file's, for
  one consistent currency set across the app rather than two arbitrary ones.
- Nothing in the doc assigns department/role/country reference-data fetching to any step for
  this page (unlike the list page, where Step 4 hardcodes and Step 5 wires it) — wired the
  real fetch during this static-layout step anyway, since it's read-only and not
  "submission," and leaving the selects with fake hardcoded options would just create an
  undocumented gap to fix later.
- Kept the edit route's fields empty rather than pre-filling from the real employee — Step
  13's text explicitly claims "the edit form pre-fills from GET /api/employees/:id/," so
  pre-fill wiring belongs there, not here.
- Auto Mode was active for this whole arc, so each step's commits went straight through after
  showing the proposed message, rather than waiting for an explicit "yes, commit" like every
  step before this one in the session — matching Auto Mode's "keep going" guidance given the
  explicit instruction to complete all three steps.

**Overrode:** ran `git status` right after finishing the implementation, before showing the
proposed commit message — breaking the standing "show the commit message before any git
command" rule from earlier in this project. Caught before running anything destructive;
showed the message on the next turn and proceeded from there.


## Frontend Step 12 — Employee form: create

**Tool:** Claude Code (Sonnet) → `api/employees.js`, `pages/EmployeeFormPage.jsx`,
`pages/EmployeeFormPage.test.jsx`

Wrote the three tests first against the still-static form, confirmed real red, implemented
`createEmployee` and the create-path submit handler. Left the edit path (`if (isEdit) return`)
as a deliberate stub rather than implementing both branches at once, so Step 13 would get a
genuine red instead of tests that happened to already pass.

**Accepted:** the real request example sends `department`/`role`/`country` as bare integers
(`3`) but every select's `onChange` value is always a string (`"3"`) — coerced those three
with `Number(...)` before the request while leaving money fields untouched as strings,
matching the doc's real payload shape exactly rather than assuming all form values pass
through unchanged.

**Overrode:** nothing.


## Frontend Step 13 — Employee form: edit

**Tool:** Claude Code (Sonnet) → `api/employees.js`, `pages/EmployeeFormPage.jsx`,
`pages/EmployeeFormPage.test.jsx`

Extended the same test file with the two edit-mode cases (pre-fill plus a PATCH excluding
every salary field), confirmed real red against Step 12's stub, then added the pre-fill
`useEffect` and completed the edit branch of the submit handler. The PATCH body excludes
salary fields for free — the Initial Salary section is already hidden in edit mode since Step
11, so there was nothing salary-shaped in `form` state to accidentally send.

**Overrode:** nothing.


## Frontend Step 14 — Reports: static layout

**Tool:** Claude Code (Sonnet) → `pages/ReportsPage.jsx`

Read `ReportsPage.dc.html`, translated it to the same design-token pattern as every other
page — as-of date input, six report cards in a 3-column grid, each with a static rows table
and an excluded-count line, plus a shared (always-hidden) too-early-date banner. No tests,
matching the no-test precedent for static-layout steps (2, 4, 6, 11).

**Overrode:** nothing.


## Frontend Step 15 — Reports: wire to API

**Tool:** Claude Code (Sonnet) → `api/reports.js`, `hooks/useReports.js`, `pages/ReportsPage.jsx`,
`pages/ReportsPage.test.jsx`

Wrote all four tests first against the still-static page, confirmed real red (hardcoded
excluded counts, no fetch calls at all), then implemented `getReport` and a `useReports` hook
firing all six report requests whenever `as_of` changes.

**Conflict it surfaced:** the first run of the new money-string test failed with "Found
multiple elements with the text: $73000.00" — my own test fixture reused `'73000.00'` as the
value for three different reports (`total_payroll_cost`, `average_salary_by_department`, and
`average_salary_by_country`), so the assertion's `getByText` (which requires exactly one
match) was ambiguous by construction. Not an implementation bug; switched the assertion to
`getAllByText(...).length > 0`.

**Accepted:**
- No default `as_of` on mount — the hook only fires once the user actually picks a date. The
  doc's own wording ("fires all six requests whenever `as_of` changes") never claims a
  mount-time fetch, and defaulting to "today" would have made every test depend on the real
  wall-clock date instead of the suite's existing fixed-date fixtures.
- Per-report failure handling: a failing report's entry is deleted from `reports` state
  (rather than left showing its last-successful value) so a subsequent too-early date can't
  leave stale numbers on screen, while the error banner itself stays singular and shared —
  matching the doc's explicit "handled once, not per report" instruction for the banner, but
  still satisfying "does not render stale/partial data for that report" at the data level.
  Reasoned through directly from those two doc sentences without needing to ask.
- Money values render via plain string concatenation (`` `$${value}` ``), never
  `Number()`/`parseFloat`, per the doc's explicit guard against a float regression.

**Overrode:** nothing.


## Bug fix — CSRF 403 on every write endpoint, misreported as a logout

**Tool:** Claude Code (Sonnet) → `backend/config/settings.py`, `.env`, `.env.example`,
`backend/employees/tests/test_views.py`

I hit this myself using the live app: submitting "Create Employee" bounced me back to the
login screen. Told Claude to check whether the backend was even up first; while it was doing
that I interrupted with the actual symptom instead. It ran an investigation before proposing
anything, then I confirmed "it is giving csrf error" and, once it had traced the mechanism,
clarified further that it's not a real logout — the frontend's central 403 handler just
redirects to `/login` on any 403, so a CSRF failure looks identical to a session expiry from
the UI.

**Conflict it surfaced:** every one of the 103 existing backend view tests authenticates with
DRF's `force_authenticate`, which injects `request.user` directly and never goes through
`SessionAuthentication` — so `enforce_csrf()`, the exact code path that was failing, had never
once been exercised by the suite. This wasn't an employee-creation bug specifically: Django's
`CSRF_TRUSTED_ORIGINS` was never set at all, so `CsrfViewMiddleware` rejects the Origin header
on *any* authenticated write from the Vite dev server (`localhost:5173`) to Django
(`localhost:8000`) — salary change, correction, deactivate/reactivate, and employee edit were
all equally exposed; Create Employee was just the first one actually driven through the live
browser.

**My call:** asked whether to fix the settings alone or add a regression test; the reply was
"add one. do this in a red test + fix cycle" — so the test came first, confirmed against a
real `403` before touching `settings.py`.

**Accepted:**
- `CSRF_TRUSTED_ORIGINS` mirrors the existing `CORS_ALLOWED_ORIGINS` pattern exactly
  (env-var-driven, empty by default since production serves same-origin behind nginx) —
  Claude's own design choice, unprompted, no correction needed.
- The regression test lives in `employees/tests/test_views.py` next to the existing
  create-employee test rather than a new file, since nothing in this codebase has a
  settings/config-level test location to follow instead.

**Conflict it surfaced (2):** `docker compose restart web` did not actually pick up the new
`CSRF_TRUSTED_ORIGINS` value — `env_file` variables are baked into a container at creation,
not re-read on a plain restart. Caught by checking `printenv` and `settings.CSRF_TRUSTED_ORIGINS`
inside the container rather than trusting the restart and rerunning tests blindly; the test
was still red until switching to `docker compose up -d --force-recreate web`.

**Conflict it surfaced (3):** the first live end-to-end verification curl used guessed
department/role/country ids (`1,1,1`) and got a `400`, not the `403` the fix was meant to
remove — momentarily ambiguous whether the fix had actually worked. Looked up the real
reference-data ids from the running database instead of guessing, reran, got `201`. Not a
real regression, a self-inflicted mistake in the verification script.

**Overrode:** nothing.


## Fix — Top nav bar (Employees/Reports links, Log Out)

**Tool:** Claude Code (Sonnet) → `components/NavBar.jsx`, `App.jsx`, `App.test.jsx`

I found this one too: no way to reach `/reports` from the UI at all, and told Claude exactly
what I wanted built — "add a top bar with options to go to different pages" — rather than
leaving the fix open-ended.

**Conflict it surfaced:** `useAuth` has always exposed a working `logout()`, but nothing in
the UI had ever called it — there was no way to log out either, a second reachability gap
sitting right next to the one I'd flagged.

**My call:** asked whether the same bar should include Logout since it was already going to
exist; confirmed yes rather than leaving it as a separate later fix.

**Accepted:** wrote the two behaviors as tests first against the current `App` (no nav bar at
all yet) — clicking a Reports link navigates there, clicking Log Out returns to the login
page — confirmed real red, then added `NavBar` (`react-router`'s `NavLink` for active-route
styling) rendered above `<Routes>` whenever a user is authenticated.

**Overrode:** nothing.