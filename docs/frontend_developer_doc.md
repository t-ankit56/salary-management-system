# Frontend Build Guide

The frontend is built page by page. For each page: its static layout is built in Claude
Design and scaffolded here first (no behaviour, nothing to test), then it is wired to its
endpoints in a red-green cycle — write the failing test, confirm it fails for the expected
reason, implement the minimum that passes, commit both.

Scope and reasoning: `../docs/requirements.md`
Working agreement and domain invariants: root `CLAUDE.md`
API shapes used below were captured from the running backend, not inferred from serializer
code alone — see `../docs/backend_developer_doc.md` for how the backend itself is built.

Order matters. Login must exist before any other page can be integrated, since every other
endpoint requires a session and the central 403 handler is wired as part of it.

---

## Stack

React 19 · Vite · plain JavaScript (no TypeScript) · Tailwind CSS v4 (CSS-first config, no
`tailwind.config.js`) · fetch (no HTTP library) · Vitest · React Testing Library

Exact patch versions aren't pinned here the way the backend's are — nothing is installed
yet. Pin via `package-lock.json` on first `npm install` and treat that lockfile as the
source of truth from then on.

```
package.json        vite, react, react-dom, react-router-dom, tailwindcss, @tailwindcss/vite
                     vitest, @testing-library/react, @testing-library/jest-dom, jsdom (dev)
```

Tailwind is configured via `@import "tailwindcss";` in `src/index.css` plus the
`@tailwindcss/vite` plugin in `vite.config.js` — v4's content scanning is automatic, so there
is no `tailwind.config.js` and no explicit content glob to maintain.

## Layout

```
frontend/
  src/
    api/
      client.js          fetch wrapper: credentials, CSRF header, central 403 handling
      employees.js        employee + reference-data endpoint calls
      salary.js            salary change / correction / history endpoint calls
      reports.js            report endpoint calls
    hooks/
      useAuth.js           session state: current user, login, logout, mount-time check
      useEmployees.js      list with filters, search, pagination
      useEmployee.js       single employee fetch + update
      useSalaryHistory.js  salary periods + corrections for one employee
      useReports.js        all six reports for a given as-of date
    components/
      modals/
        SalaryChangeModal.jsx
        SalaryCorrectionModal.jsx
        StatusChangeModal.jsx      shared shape for deactivate and reactivate
    pages/
      LoginPage.jsx
      EmployeeListPage.jsx
      EmployeeDetailPage.jsx
      EmployeeFormPage.jsx         create and edit
      ReportsPage.jsx
    App.jsx
    main.jsx
  index.html
  vite.config.js
```

Each hook owns its own fetch calls and error state; pages read from hooks and render.
Modals are presentational plus their own submit handler, taking callbacks for
success/close so they don't know about routing.

---

## API conventions the frontend must handle

These apply across every endpoint below, so they're stated once here instead of repeated
per step.

**Authentication.** Every endpoint requires a session except `POST /api/auth/login/`. A
missing or expired session returns:

```
403 {"detail": "Authentication credentials were not provided."}
```

on *any* endpoint — this is what the central 403 handler in `api/client.js` catches: on any
403, clear local auth state and route to `/login`. `GET /api/auth/me/` is called once on app
mount to establish whether a session already exists; there is no polling.

**Login failure is 401 with an empty body**, not 400 and not 403 — it's a separate case from
everything else:

```
POST /api/auth/login/  (wrong password)
401  (no body)
```

Show a generic "Invalid email or password" message; there's no server message to surface.

**CSRF.** Session authentication means Django's CSRF protection applies to every mutating
request. Once a session exists, the browser holds a `csrftoken` cookie; every `POST` /
`PATCH` / `DELETE` must echo it back as an `X-CSRFToken` header, or the request fails
independently of application logic:

```
403 {"detail": "CSRF Failed: CSRF token missing."}
```

`GET` requests never need this. Build this into `api/client.js` once, not per call site.

**Two distinct 400 shapes.** Field validation errors and business-rule errors look
different, and the frontend must branch on which one it got:

```
// field validation (serializer-level)
{"email": ["This field is required."], "base": ["This field is required."]}

// business rule (service-level, caught in the view)
{"detail": "Cannot backdate a change before the current period's start"}
```

Rule: if the body has a `"detail"` key, show it as a single banner/toast message. Otherwise,
treat every key as a field name and its array as that field's error messages. The reports
endpoint adds a third key (`earliest_available_date`) alongside `detail` — see the Reports
step.

**Money is always a JSON string** — `"65000.00"`, never `65000` — including in every report
figure. Never run it through `parseFloat`/arithmetic except immediately before formatting
for display; treat it as an opaque string everywhere else (forms submit it as a string too).

**Pagination.** List responses look like:

```
{"count": 30, "next": "http://.../api/employees/?page=2", "previous": null, "results": [...]}
```

Don't follow `next`/`previous` directly — they're absolute URLs built from the request host,
which may not match this deployment's origin (dev vs. same-origin-behind-nginx in
production). Track the `page` query param yourself and derive total pages from `count` and
the fixed page size of 25.

**CORS** only matters in local dev, where the backend's `CORS_ALLOWED_ORIGINS` must list the
Vite dev server's origin and every `fetch` must set `credentials: "include"`. In production
the frontend is served same-origin behind nginx, so this is a dev-only concern — don't build
anything that assumes CORS exists in production.

---

# Step 1 — Project skeleton

Scaffolding only.

**Vite + React**, plain JavaScript template. **Tailwind CSS v4** via `@tailwindcss/vite` and
`@import "tailwindcss";` in `src/index.css` (content scanning is automatic in v4, no
`tailwind.config.js`). **react-router-dom** for the routes (`/login`, `/employees`,
`/employees/:id`, `/employees/new`, `/employees/:id/edit`, `/reports`) plus a redirect from
`/` to `/employees`.

**Vitest + React Testing Library**: `vitest.config.js` (or a `test` block in
`vite.config.js`) with `environment: "jsdom"`, a setup file importing
`@testing-library/jest-dom`, and a `test` script in `package.json`.

An `.env` (gitignored) holding `VITE_API_BASE_URL`, empty in production (same-origin) and
pointing at the backend's local port in dev.

**Done:** `npm run dev` serves a blank routed shell; `npm run test` runs zero tests
successfully; `npm run build` produces a production bundle.
**Commit:** `chore(ui): frontend skeleton with vite, tailwind, router and vitest`

---

# Step 2 — Login: static layout

Built in Claude Design, scaffolded here as `LoginPage.jsx`: email field, password field,
submit button, a space reserved for an error message. No form state beyond native inputs,
no submit handler, no fetch.

**Done:** the page renders at `/login` and looks right; nothing is wired up.
**Commit:** `chore(ui): static login page`

---

# Step 3 — Login: wire to API and central auth

This step also builds the app-wide auth plumbing every later page depends on: the fetch
wrapper, the mount-time session check, and the central 403 handler. Build it here because
it's inseparable from "what does the app do when there's no session."

**`api/client.js`**: a wrapper around `fetch` that sets `credentials: "include"`, attaches
`X-CSRFToken` (read from the `csrftoken` cookie) on non-GET requests, parses the JSON body,
and on a `403` response dispatches a single `"auth:unauthorized"` event on `window` before
resolving — it does not redirect itself, so it stays usable from tests without a router.

**`useAuth.js`**: on mount, calls `GET /api/auth/me/`. A `200` sets `{email}` as the current
user; a `403` sets the user to `null` without treating it as an error (this is the expected
logged-out state, not a failure). Also listens for `"auth:unauthorized"` and clears the user
when it fires — this is what makes the handler "central": any page's fetch call can trigger
a logout, not just `/me/`. Exposes `login(email, password)` (`POST /api/auth/login/`) and
`logout()` (`POST /api/auth/logout/`).

`App.jsx` renders `LoginPage` when there is no user and the rest of the router when there
is, so a 403 anywhere in the app lands the user back on `/login`.

**Real responses:**

```
POST /api/auth/login/  {"email": "hr@acme.com", "password": "correct"}
200  {"email": "hr@acme.com"}

POST /api/auth/login/  {"email": "hr@acme.com", "password": "wrong"}
401  (empty body)

GET /api/auth/me/  (no session)
403  {"detail": "Authentication credentials were not provided."}

GET /api/auth/me/  (with session)
200  {"email": "hr@acme.com"}

POST /api/auth/logout/
200  (empty body)
```

**Tests (Vitest + RTL, mocking `fetch`):**
- submitting valid credentials calls `POST /api/auth/login/` with the entered email/password
  and, on 200, shows the authenticated app instead of the login form
- a 401 response shows "Invalid email or password" and does not navigate anywhere
- a `403` from *any* mocked fetch call dispatches the unauthorized event and the app renders
  `LoginPage`
- `useAuth`'s mount-time `GET /me/` returning 403 does not throw and leaves the user logged
  out silently (no error banner on first load)

**Commit:** `test: login submission, 401 handling and central 403 handling (red)` →
`feat: session login with central 403 handler`

---

# Step 4 — Employee list: static layout

Built in Claude Design, scaffolded as `EmployeeListPage.jsx`: search box, department/role/
country/status filter selects (options hardcoded for now), a table with columns for code,
name, department, role, country, status, and a "New Employee" link. Pagination controls at
the bottom. No fetching — the table renders a couple of hardcoded rows so the layout is
visible.

**Done:** page renders at `/employees` with static rows.
**Commit:** `chore(ui): static employee list page`

---

# Step 5 — Employee list: wire to API

**`api/employees.js`**: `listEmployees({department, role, country, status, search, page})`
building the query string, and `listDepartments()` / `listRoles()` / `listCountries()` for
filter options.

**`useEmployees.js`**: refetches whenever a filter, search term or page changes. The filter
selects populate from the three reference-data calls, run once on mount.

**Real responses:**

```
GET /api/employees/?department=3&status=active
200  {
  "count": 1, "next": null, "previous": null,
  "results": [{
    "id": 3, "employee_code": "E100", "first_name": "Jane", "last_name": "Doe",
    "email": "jane.doe@example.com",
    "department": 3, "department_name": "Engineering",
    "role": 3, "role_name": "Manager",
    "country": 3, "country_name": "India",
    "status": "active",
    "hire_date": "2022-01-15",
    "created_at": "2026-09-16T17:21:36.466778Z", "updated_at": "2026-09-16T17:21:36.466798Z"
  }]
}

GET /api/departments/
200  [{"id": 3, "name": "Engineering", "is_active": true}]
```

`status` is exactly `"active"` or `"inactive"` — render it as a badge directly, no mapping
needed. There's no error shape to handle here beyond the global 403 case, since GET requests
with valid query params don't fail validation.

**Tests:**
- selecting a department filter re-requests `/api/employees/?department=<id>` with the
  other params preserved
- typing in search re-requests with `?search=<term>` (debounce not required by any test —
  don't test timing, test the request shape)
- the table renders `department_name`/`role_name`/`country_name`/`status` from the response,
  not the raw ids
- changing page re-requests `?page=<n>` and does not follow the `next` URL from the response

**Commit:** `test: employee list fetches, filters, search and pagination (red)` →
`feat: wire employee list to the API`

---

# Step 6 — Employee detail: static layout

Built in Claude Design, scaffolded as `EmployeeDetailPage.jsx`: employee header (name, code,
department/role/country, status badge), a salary history table (period dates, base,
allowance, yearly bonus, currency, correction count), and four action buttons — Change
Salary, Correct Salary, Deactivate/Reactivate (one button, label depends on status), and
Edit. Each button opens its modal shell (`SalaryChangeModal`, `SalaryCorrectionModal`,
`StatusChangeModal`), all static: fields present, no submit handler, no fetch. Deactivate and
Reactivate are the same `StatusChangeModal` component with a `mode` prop — same single
`effective_date` field either way.

Salary change and salary correction are separate buttons opening separate modals — never a
single "edit salary" form. This distinction is a domain invariant, not a layout choice.

**Done:** page renders at `/employees/:id` with static data and all four modals open/close
correctly with no submission.
**Commit:** `chore(ui): static employee detail page with salary and status modals`

---

# Step 7 — Employee detail: fetch employee and salary history

**`api/employees.js`**: `getEmployee(id)`. **`api/salary.js`**: `getSalaryHistory(id)` and
`getCorrections(employeeId, periodId)`.

**`useEmployee.js`** and **`useSalaryHistory.js`** fetch on mount from the route param.

**Real responses:**

```
GET /api/employees/3/
200  {
  "id": 3, "employee_code": "E100", "first_name": "Jane", "last_name": "Doe",
  "email": "jane.doe@example.com",
  "department": 3, "department_name": "Engineering",
  "role": 3, "role_name": "Manager",
  "country": 3, "country_name": "India",
  "status": "active", "hire_date": "2022-01-15",
  "created_at": "2026-09-16T17:21:36.466778Z", "updated_at": "2026-09-16T17:21:36.466798Z"
}

GET /api/employees/3/salary-periods/
200  [
  {"id": 3, "base": "65000.00", "allowance": "5000.00", "yearly_bonus": "3000.00",
   "currency": "USD", "effective_from": "2023-01-01", "effective_to": null,
   "correction_count": 0},
  {"id": 2, "base": "60000.00", "allowance": "5000.00", "yearly_bonus": "3000.00",
   "currency": "USD", "effective_from": "2022-01-15", "effective_to": "2023-01-01",
   "correction_count": 1}
]

GET /api/employees/3/salary-periods/2/corrections/
200  [{
  "id": 1, "salary_period": 2,
  "previous_base": "60000.00", "previous_allowance": "5000.00", "previous_yearly_bonus": "3000.00",
  "new_base": "61000.00", "new_allowance": "5000.00", "new_yearly_bonus": "3000.00",
  "reason": "Data entry error", "created_by": 3, "created_at": "2026-09-16T17:22:11.039274Z"
}]
```

Note this list is *not* paginated (plain array, not `{results: [...]}`) — don't reuse the
list page's pagination handling here.

**Tests:**
- the page requests `/api/employees/:id/` and `/api/employees/:id/salary-periods/` on mount
  and renders both the header and the history table from those responses
- history rows are ordered as returned (newest first) with their `correction_count`
- clicking a row with a nonzero correction count fetches and displays its corrections log

**Commit:** `test: employee detail fetches employee and salary history (red)` →
`feat: wire employee detail to the API`

---

# Step 8 — Salary change modal

**`api/salary.js`**: `recordSalaryChange(employeeId, {base, allowance, yearly_bonus, currency, effective_from})`.

**Real responses:**

```
POST /api/employees/3/salary-changes/
{"base": "65000", "allowance": "5000", "yearly_bonus": "3000", "currency": "USD", "effective_from": "2023-01-01"}
201  {"id": 3, "employee": 3, "base": "65000.00", "allowance": "5000.00",
      "yearly_bonus": "3000.00", "currency": "USD",
      "effective_from": "2023-01-01", "effective_to": null}

POST /api/employees/3/salary-changes/  {"base": "65000", "effective_from": "2022-06-01"}
400  {"detail": "Cannot backdate a change before the current period's start"}
```

A missing required field (e.g. no `effective_from`) returns the field-validation shape
instead: `{"effective_from": ["This field is required."]}`.

**Tests:**
- submitting the form calls `POST /api/employees/:id/salary-changes/` with the entered
  values as strings (not numbers) in the body
- on success, the modal closes and the salary history refetches so the new period appears
- a `{"detail": "..."}` 400 response shows that message as a banner inside the modal, form
  stays open
- a field-shaped 400 response (e.g. missing `effective_from`) highlights that field, not a
  generic banner

**Commit:** `test: salary change submission and error shapes (red)` →
`feat: wire salary change modal to the API`

---

# Step 9 — Salary correction modal

**`api/salary.js`**: `correctSalaryPeriod(employeeId, {salary_period, base, allowance, yearly_bonus, reason})`.
The modal is opened from a specific history row, so `salary_period` comes from that row's id,
not user input — the user only edits amounts and reason.

**Real responses:**

```
POST /api/employees/3/salary-corrections/
{"salary_period": 2, "base": "61000", "allowance": "5000", "yearly_bonus": "3000", "reason": "Data entry error"}
201  {"id": 1, "salary_period": 2,
      "previous_base": "60000.00", "previous_allowance": "5000.00", "previous_yearly_bonus": "3000.00",
      "new_base": "61000.00", "new_allowance": "5000.00", "new_yearly_bonus": "3000.00",
      "reason": "Data entry error", "created_by": 3, "created_at": "2026-09-16T17:22:11.039274Z"}

POST /api/employees/3/salary-corrections/  (reason omitted or blank)
400  {"reason": ["This field may not be blank."]}
```

**Tests:**
- submitting sends `salary_period` as the id of the row the modal was opened from, plus the
  edited amounts and reason
- a blank reason shows the field error under the reason input (from the real 400 shape
  above) and does not submit-and-fail silently
- on success, the modal closes and the corrected period's amounts and correction count
  refresh in the history table

**Commit:** `test: salary correction submission and missing-reason error (red)` →
`feat: wire salary correction modal to the API`

---

# Step 10 — Deactivate and reactivate

**`api/employees.js`**: `deactivateEmployee(id, effective_date)` and
`reactivateEmployee(id, effective_date)`. `StatusChangeModal` picks which one to call from
its `mode` prop, itself derived from the employee's current `status`.

**Real responses:**

```
POST /api/employees/3/deactivate/  {"effective_date": "2024-01-01"}
200  (empty body)

POST /api/employees/3/deactivate/  (already inactive)
400  {"detail": "Employee is already inactive"}

POST /api/employees/3/reactivate/  {"effective_date": "2024-06-01"}
200  (empty body)

POST /api/employees/3/reactivate/  (missing effective_date)
400  {"effective_date": ["This field is required."]}
```

Both endpoints return an empty 200 body on success — refetch the employee afterwards to get
the updated `status` rather than trying to derive it client-side.

**Tests:**
- when status is "active", the button opens `StatusChangeModal` in deactivate mode and posts
  to `.../deactivate/`; when "inactive", reactivate mode and `.../reactivate/`
- on success, the employee is refetched and the status badge/button label update
- a `{"detail": "..."}` 400 (e.g. already inactive) shows as a banner in the modal

**Commit:** `test: deactivate and reactivate submission and already-inactive error (red)` →
`feat: wire deactivate and reactivate to the API`

---

# Step 11 — Employee form: static layout

Built in Claude Design, scaffolded as `EmployeeFormPage.jsx`, used for both create and edit
at `/employees/new` and `/employees/:id/edit`. Fields: employee code, first name, last name,
email, department/role/country selects, hire date. Create-only fields, shown only when
there's no `:id` in the route: opening base, allowance, yearly bonus, currency, salary
effective-from. Editing salary happens through the detail page's modals, never through this
form once an employee exists — that's why those fields disappear on edit.

**Done:** both routes render the right field set with no submission wired up.
**Commit:** `chore(ui): static employee create/edit form`

---

# Step 12 — Employee form: create

**`api/employees.js`**: `createEmployee({...all fields including salary...})`.

**Real responses:**

```
POST /api/employees/
{"employee_code": "E100", "first_name": "Jane", "last_name": "Doe", "email": "jane.doe@example.com",
 "department": 3, "role": 3, "country": 3, "hire_date": "2022-01-15",
 "base": "60000", "allowance": "5000", "yearly_bonus": "3000", "currency": "USD",
 "salary_effective_from": "2022-01-15"}
201  {"id": 3, "employee_code": "E100", "first_name": "Jane", "last_name": "Doe",
      "email": "jane.doe@example.com",
      "department": 3, "department_name": "Engineering",
      "role": 3, "role_name": "Manager", "country": 3, "country_name": "India",
      "status": "active", "hire_date": "2022-01-15",
      "created_at": "2026-09-16T17:21:36.466778Z", "updated_at": "2026-09-16T17:21:36.466798Z"}

POST /api/employees/  (missing email and base)
400  {"email": ["This field is required."], "base": ["This field is required."]}

POST /api/employees/  (duplicate employee_code or email)
400  {"employee_code": ["employee with this employee code already exists."]}
```

**Tests:**
- submitting sends every field, with all money fields as strings, to `POST /api/employees/`
- on 201, navigates to `/employees/:new-id`
- a field-shaped 400 (missing fields, or a duplicate code/email) highlights each named field
  with its message; the form is not cleared and stays on the page

**Commit:** `test: employee creation submission and validation error mapping (red)` →
`feat: wire employee creation to the API`

---

# Step 13 — Employee form: edit

**`api/employees.js`**: `updateEmployee(id, {employee_code, first_name, last_name, email, department, role, country, hire_date})` —
a `PATCH`, demographic fields only, no salary fields in the body at all.

**Real response:**

```
PATCH /api/employees/3/  {"first_name": "Janet"}
200  {"id": 3, "employee_code": "E100", "first_name": "Janet", "last_name": "Doe",
      "email": "jane.doe@example.com",
      "department": 3, "department_name": "Engineering",
      "role": 3, "role_name": "Manager", "country": 3, "country_name": "India",
      "status": "active", "hire_date": "2022-01-15",
      "created_at": "2026-09-16T17:21:36.466778Z", "updated_at": "2026-09-16T17:22:40.001Z"}
```

Validation error shapes are the same family as create (field-keyed arrays); no new shape to
test here.

**Tests:**
- the edit form pre-fills from `GET /api/employees/:id/` and submits only the demographic
  fields as a `PATCH`, never `base`/`allowance`/`yearly_bonus`/`currency`/`salary_effective_from`
- on 200, navigates back to `/employees/:id` showing the updated fields

**Commit:** `test: employee edit submission excludes salary fields (red)` →
`feat: wire employee edit to the API`

---

# Step 14 — Reports: static layout

Built in Claude Design, scaffolded as `ReportsPage.jsx`: a single as-of date picker, and six
report cards/sections (total payroll cost, headcount by department, headcount by country,
average salary by department, average salary by country, average bonus by department), each
with a place to show its `excluded_count` and a shared place for a too-early-date error.
Static placeholder numbers, no fetching.

**Done:** page renders at `/reports` with the date picker and six static sections.
**Commit:** `chore(ui): static reports page`

---

# Step 15 — Reports: wire to API

**`api/reports.js`**: `getReport(name, asOf)` hitting `GET /api/reports/{name}/?as_of=...`.
**`useReports.js`** fires all six requests whenever `as_of` changes.

**Real responses:**

```
GET /api/reports/total_payroll_cost/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "total_payroll_cost": "73000.00", "excluded_count": 0}

GET /api/reports/headcount_by_department/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "headcount_by_department": {"Engineering": 1}, "excluded_count": 0}

GET /api/reports/average_salary_by_department/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "average_salary_by_department": {"Engineering": "73000.00"}, "excluded_count": 0}

GET /api/reports/average_salary_by_country/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "average_salary_by_country": {"India": "73000.00"}, "excluded_count": 0}

GET /api/reports/average_bonus_by_department/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "average_bonus_by_department": {"Engineering": "3000.00"}, "excluded_count": 0}

GET /api/reports/headcount_by_country/?as_of=2026-09-16
200  {"as_of": "2026-09-16", "headcount_by_country": {"India": 1}, "excluded_count": 0}

GET /api/reports/total_payroll_cost/?as_of=2020-01-01  (before earliest salary data)
400  {"detail": "No salary data available before 2022-01-15", "earliest_available_date": "2022-01-15"}
```

All six report money values are quoted strings, same as everywhere else in the API. The
headcount reports carry no money, only integer counts. All six share the same `as_of` /
too-early-date behaviour, so the too-early-date error is handled once, not per report.

Each report returns its payload under a key equal to the report name requested
(`total_payroll_cost`, `headcount_by_department`, and so on), alongside the shared `as_of`
and `excluded_count`. Read it dynamically as `res[name]` in `getReport` — do not write six
per-report accessors.

**Tests:**
- changing the as-of date re-requests all six report endpoints with that date
- every card renders its `excluded_count`, including when it's `0`
- a too-early-date 400 on any report shows `earliest_available_date` in the error message
  and does not render stale/partial data for that report
- a report money value is rendered from the string as given, not run through arithmetic
  first (guards against a future regression back to floats)

**Commit:** `test: report fetching, excluded_count display and too-early rejection (red)` →
`feat: wire reports page to the API`

---

# Step 16 — Deployment

Production build (`npm run build`) served as static files by nginx, same origin as the
Django backend — no `VITE_API_BASE_URL` needed in production since requests are relative.
Nginx routes `/api/` and `/admin/` to the Django app and everything else to the built
`index.html` (client-side routing needs the SPA fallback).

**Done:** a production build served behind nginx reaches every page and every endpoint
without CORS being involved at all.
**Commit:** `chore: production frontend build and nginx routing`

---

# Endpoints used, by page

| Page | Endpoints |
|---|---|
| Login | `POST /api/auth/login/`, `GET /api/auth/me/`, `POST /api/auth/logout/` |
| Employee list | `GET /api/employees/`, `GET /api/departments/`, `GET /api/roles/`, `GET /api/countries/` |
| Employee detail | `GET /api/employees/{id}/`, `GET /api/employees/{id}/salary-periods/`, `GET /api/employees/{id}/salary-periods/{pid}/corrections/`, `POST /api/employees/{id}/salary-changes/`, `POST /api/employees/{id}/salary-corrections/`, `POST /api/employees/{id}/deactivate/`, `POST /api/employees/{id}/reactivate/` |
| Employee form | `POST /api/employees/`, `PATCH /api/employees/{id}/`, plus the same reference-data GETs as the list page |
| Reports | `GET /api/reports/{name}/` × 6 |

Not used by the frontend: `PATCH` on departments/roles/countries, and the roster upload
endpoint — both out of scope per the decisions above.
