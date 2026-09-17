# Trade-offs and Performance

`requirements.md`'s "Key decisions and reasoning" covers the scope-level calls (currency,
salary structure, database choice, time-aware reporting). This doc goes one level deeper —
the performance-specific reasoning and the trade-offs made to get there, at the scale the
brief actually states: ~10,000 employees.

## Reports: database aggregation, not a per-employee loop

Every report that touches salary (`total_payroll_cost`, both `average_salary_by_*`,
`average_bonus_by_department`) shares one helper, `_employed_salary_periods`
(`reporting/services.py`), which resolves "who's employed and what's their salary as of
this date" as a single filtered queryset, then lets Postgres do the aggregation
(`Sum`/`Avg`/`Count`) in the database. The alternative — resolving each employee's salary in
a Python loop via `resolve_as_of` and summing in application code — is what the first report
(`total_payroll_cost`) was originally built with; every report after it was built on the
shared DB-aggregation helper instead, and `total_payroll_cost` was refactored onto it too
once the pattern existed, with the existing test suite as the safety net. At 10,000
employees, one aggregate query beats 10,000 individual resolutions every time a report is
requested.

## Overlap prevention: a database constraint, not application validation

`EmploymentPeriod` and `SalaryPeriod` both carry a Postgres `GiST` exclusion constraint
(`common/constraints.py`) guaranteeing no two periods for the same employee ever overlap.
This was a deliberate choice over validating in Python at the service layer: a constraint
holds no matter which code path writes the row — the API, the admin site, the roster
upload, or the seed script — while application-level validation has to be reimplemented (and
kept in sync) everywhere a row can be written. The cost is a `btree_gist` extension and a
constraint definition that isn't Django's default `UniqueConstraint`; both are one-time
setup, and the resulting guarantee is unconditional.

## Half-open snapshot periods, not computed diffs

Salary and employment history are stored as end-dated snapshot rows, not as a sequence of
deltas that would need to be replayed to answer "what was true on date X." Resolving a
point-in-time value is one indexed range lookup
(`effective_from <= as_of AND (effective_to IS NULL OR effective_to > as_of)`), not a
walk through history — the only shape that scales to reporting over 10,000 employees on
demand. The cost is storage: every raise writes a full new row rather than a delta, which is
negligible at this scale and is also exactly what "full salary history" requires anyway.

## Pagination: fixed page size, and a UI that doesn't scale linearly with page count

The employee list uses a fixed page size (25) with `page` tracked as frontend state and
`count` from the response used to derive total pages — the frontend never follows DRF's own
`next`/`previous` URLs directly, so its routing doesn't couple to a backend-controlled URL
shape.

A real problem this surfaced at full scale: with 10,000 employees, `count / 25` is 400
pages, and the original pager rendered one button per page — 400 DOM nodes, visibly
overflowing the layout. Fixed with a windowed page-number algorithm (first, last, the
current page's two neighbors, `…` for the gaps — the same shape Django's own admin uses)
instead of listing every page, bounding the pager to a handful of elements regardless of how
many pages exist (`pages/EmployeeListPage.jsx`).

## Roster upload: reject early, all-or-nothing

`import_roster` (`imports/services.py`) opens the workbook in `read_only=True` mode and
enforces the 10,000-row cap from the sheet's dimension metadata (`ws.max_row`) *before*
iterating a single row — an oversized file is rejected without reading any row data, not
after partially parsing it. Validation for every row is collected before anything is
written: on failure, the response lists every failing row and its error, not just the
first, and nothing is saved. The alternative — partial success, saving whatever rows
validated and reporting the rest as failed — was deliberately rejected: it gives a simpler
mental model at 10,000-row scale ("fix the file, upload again") over a harder one ("which
rows made it in, and how do I retry just the rest").

## Money: `Decimal` end-to-end, serialized as a string

Every money field is `Decimal` in Python and `NUMERIC` in Postgres, and DRF's
`DecimalField` defaults to serializing it as a string, not a JSON number — the one place
this slipped was the raw-dict report responses (`Response(result)` on a plain dict skips
`DecimalField` entirely), which silently fell back to `float(obj)` in DRF's JSON encoder.
Caught while writing the frontend build guide against the live API rather than the
serializer source, and fixed by stringifying `Decimal` values explicitly before responding
(`reporting/views.py`). At the aggregate scale this system reports at, a float rounding
error is not cosmetic — it changes a payroll total.

## Session auth, not JWT

The brief scopes this to a single authenticated user with one deployment — no statelessness
requirement, no second backend needing to verify a token independently. A session cookie
plus CSRF protection is simpler to reason about and revocable server-side (logout actually
ends the session, rather than waiting out a token's expiry). JWT would be the right call the
moment there's more than one backend verifying identity; nothing here needs that yet.

## Production sizing: a 1-vCPU/2GB VM

gunicorn runs with 2 workers, not the `2 * cores + 1` formula's default of 3 — chosen for
the VM's actual RAM headroom alongside Postgres and nginx, not the CPU count alone. Postgres
and gunicorn are both bound to `127.0.0.1` (never exposed directly) with nginx as the only
public surface, and the frontend is built via a throwaway `node:20` container rather than
installing Node permanently — the always-on footprint stays just nginx, Postgres, and one
Django process.

## Seed data: deterministic where it matters, random everywhere else

`seed_data` (`employees/management/commands/seed_data.py`) uses fixed lists for department
and role names (Faker has no sensible provider for job-function naming) but real Faker
country data, and randomizes everything about each generated employee except a fixed
deactivation ratio (every 7th employee) — a per-employee coin flip risks a rare run with
zero inactive employees at low `--count`, making test assertions about "a mix of active and
inactive" flaky without being wrong. Four employees (`DEMO001`-`DEMO004`) are seeded
deterministically on top of the random batch specifically so a demo or a manual QA pass has
fixed, known-shape cases to point at — a full salary history, a future-dated raise, a
correction, and a deactivation — rather than having to search 10,000 random rows for an
example of each.
