# AI Prompts

Literal prompts as given to AI tools, logged as used.

---

## Step 1 — Skeleton

**Claude Code (Sonnet)**

> Read CLAUDE.md, backend/CLAUDE.md, and docs/backend_developer_doc.md before doing anything.
>
> We are building Step 1 only — the project skeleton. Do not start Step 2 or create any models.
>
> Before writing any files, show me your plan: the files you will create, and the contents of config/settings.py, docker-compose.yml, and the Dockerfile. I want to review before you write.
>
> Two things I will be checking:
> - AUTH_USER_MODEL = "accounts.User" is set in settings before any migration exists
> - DB_HOST is the compose service name, not localhost
>
> Do not run makemigrations or migrate in this step.
> 


*Asked where the Docker files should live:*

> Repo root for docker-compose.yml. Dockerfile and .dockerignore in backend/.
> Build context ./backend, bind-mount ./backend to /app.

> CORS_ALLOWED_ORIGINS should come from an environment variable, not be hardcoded.
> In production the frontend is served same-origin behind nginx, so it will be empty there.


*It stopped and flagged that Django cannot boot with AUTH_USER_MODEL set to a model that
does not exist — contrib.auth's AppConfig.ready() calls get_user_model() unconditionally —
and asked whether to add a stub or revise the build guide:*

> Option 1. Write the stub as the field declaration only — no manager, no create_user,
> no create_superuser:
>
> class User(AbstractBaseUser, PermissionsMixin):
>     email = models.EmailField(unique=True)
>     USERNAME_FIELD = "email"
>     REQUIRED_FIELDS = []
>
> That is the minimum needed for Django to boot. The manager and remaining fields are
> Step 2 and get test-driven there.
>
> Still no makemigrations or migrate in this step.


---

## Step 2 — User model

**Claude Code (Sonnet)**

> Step 2. accounts/models.py already has a field-only stub from Step 1 — extend it, don't
> start over.
>
> Write the failing tests first and stop. Do not implement yet.

It stopped and flagged that 3 out of 4 tests cannot run without creating migrations. 
> Yes, run makemigrations accounts and then show me that all 4 test are failing for the right reasons 

> now implement the manager to make them pass



## Step 3 — Session authentication endpoints

**Claude Code (Sonnet)**

> now let's start with step 3 now

Wrote the failing tests for login, me and logout, ran them to confirm all five 404 (no
routes registered yet), committed red.

> now implement the login view first and pass its test

> now implement the me view and pass its test

*Interrupted mid-`me`-view work, since login had passed but not yet been committed:*

> befor implementing me view commit the login view as green

While implementing `me`, it reused the `ClassVar` annotation from Step 2 to silence ruff on
DRF's `permission_classes`, without checking whether it still fit:

> why are you using ClassVar

> yes, ignore RUF012 in pyproject.toml

*Asked to commit, then to split the two concerns:*

> split the ruff config change in its chore

> now implement the logout view and pass its test

*New standing rule, stated once here and formalised into `CLAUDE.md` afterwards:*

> when you are ready for commit show the commit message and description

> now implement the CORS config

> write a rule in claude.md that whenever you are ready for commit show the commit message
> and description automatically


## Step 4 — Reference data

**Claude Code (Sonnet)**

> let's start with step 4 now

*Two file-creation attempts were rejected with no error explaining why, then:*

> what is happening?

> lets start step 4 fresh

*Presented the plan before writing anything this time — model shape, the tests to be
written, and one build-guide gap: `Country` isn't mentioned anywhere in the Layout section's
app listing, unlike `Department`/`Role` which are explicitly under `employees/`. Asked where
it should live:*

> country will also be in employees

> first implement the models and pass their tests. Endpoints comes later

> now implement the endpoints and pass their tests


## Step 5 — Employee

**Claude Code (Sonnet)**

> let's start with step 5 now

> First right a basic Employee model class so that the test fail because of assertion not
> because of an import error

*Wrote the full model from the build guide instead of a literal empty stub:*

> you are writing the whole model. write just an empty class so that test can run

> now implement the full model and pass its tests

> now implement the endpoints and pass their tests one at a time


## Interlude — Local admin access (before Step 6)

**Claude Code (Sonnet)**

> now before starting step 6 lets make all migrations migrate them and run server. Create a
> superuser so that I can check django admin

*Flagged that the admin site would come up empty — no app has `admin.py` yet, so nothing is
registered, not even the custom `User` model:*

> yes, add admin.py registrations for accounts and employees

> change the superuser password to 1234

*Reported an actual admin error hit while using it:*

> 'date_joined' cannot be specified for User model form as it is a non-editable field. Check
> fields/fieldsets/exclude attributes of class UserAdmin.
> an error I am getting in admin


## Step 6 — Period constraints

**Claude Code (Sonnet)**

> let's start with step 6 now

*Started scaffolding the salary app's tests before EmploymentPeriod was even implemented:*

> lets pass the employment period tests first then go to salary perioid

> now implement the full model and pass its tests

> implement admin page too for this model before commit

> now implement the salary period tests

> now implement the full model and pass its tests

> add yhis model in admin too before commit


## Step 7 — As-of resolution

**Claude Code (Sonnet)**

> let's start with step 7 now

> now implement the full function and pass its tests


## Step 8 — Creating an employee opens periods

**Claude Code (Sonnet)**

> let's start with step 8 now

> now implement the full function and pass its tests

*Flagged, unprompted, that the actual `POST /api/employees/` endpoint bypasses
`create_employee` entirely — not part of Step 8's test list, but inconsistent with Step 16's
roster upload and Step 17's seed command, both specified to open both periods on creation:*

> is it wired in any other step of the doc?

*Checked Steps 9–18: never revisited. Reported back and asked whether to wire it now.*

> yes, wire the view now

*Started editing the serializer directly, skipping its own red-first discipline:*

> you need to commit a red test befor wiring it. also commit the previous step 8 commit
> before this red


## Step 9 — Recording a salary change

**Claude Code (Sonnet)**

> lets start step 9

> now implement the full function and pass its tests

*Flagged the same class of gap as Step 8, unprompted this time — checked Steps 10–18 itself
before reporting it:*

> yes, wire the view now


## Step 10 — Corrections

**Claude Code (Sonnet)**

> start step 10

*Interrupted mid-model-writing:*

> add a created_by in this model

*Updated the tests and stub to include `created_by`, confirmed the red state still held,
then asked whether to amend the already-committed red commit or create a new one:*

> amend it

> now implement the full function and pass its tests


## Step 11 — Status changes

**Claude Code (Sonnet)**

> start step 11

> now implement the full function and pass its tests


## Step 12 — Salary history endpoints

**Claude Code (Sonnet)**

> start step 12

> now implement the full endpoints and pass their tests


## Step 13 — Employee list

**Claude Code (Sonnet)**

> start step 13

> now implement the full endpoints and pass their tests


## Step 14–15 — Reports

**Claude Code (Sonnet)**

> start step 14

> now implement the full functions and pass its tests

*Deferred the `GET /api/reports/{name}/` endpoint, since Step 14's own text doesn't mention
it and the API table describes one shared endpoint that Step 15's reports would also need:*

> start step 15

> now implement the full functions and pass its tests

*Asked whether to also refactor Step 14's `total_payroll_cost` onto the same aggregate-based
helper used for the four new reports, for consistency:*

> yes, refactor them now and commit as refactor

> sure build the endpoint now


# Frontend

## Frontend Step 1 — Project skeleton

**Claude Code (Sonnet)**

> give me a list of four pages and modals that needs to be created by claude design as
> mentioned in frontend_developer_docs.md in docs

*Found the doc actually specifies five pages plus three modals, not four; listed them from
the doc's "Built in Claude Design" steps.*

> I want propmpts for these pages and modals which I can give to claude design

*Wrote one paste-ready prompt per page/modal, scoped to static layout only (no
behaviour/fetching), matching the doc's field lists.*

> ok I have the pages ready. lets start with step 1. whenever you need a page ask me. follow
> the guide and if you find any issues tell me

*Scaffolded Vite + React, found `create-vite`'s default template pulls in `oxlint` and
`@types/react`/`@types/react-dom` not in the doc's dependency list, and asked:*

> Strip them out

*Found `npm install tailwindcss` installs v4 (CSS-first, no `tailwind.config.js`) against the
doc's v3-style `tailwind.config.js` + content-glob layout entry, and asked:*

> use tailwind v4 update the doc for same and commit it

*Found the scaffold installs React 19 against the doc's "React 18" Stack line, and asked:*

> Keep React 19, update doc

> go ahead and commit


## Frontend Step 2 — Login: static layout

**Claude Code (Sonnet)**

> where do you want me to add the ui templates

*Asked what form the finished pages were in, to decide where they should live:*

> Exported HTML/image files

*Created `frontend/design/` (gitignored) and asked for the filename.*

> file name is Login.html

*Read the Claude Design `.dc.html` export, stripped its interactive scaffolding (local state,
submit handler, simulated error) down to a static layout per Step 2, and verified it renders
and builds.*

> yes, commit it


## Frontend Step 3 — Login: wire to API and central auth

**Claude Code (Sonnet)**

> yes, let's start step 3

*Wrote `App.test.jsx` covering all four of the doc's listed tests, ran it, hit `expect is not
defined` from jest-dom's setup, added `test.globals: true` to `vite.config.js`, reran and
confirmed a real red (missing `api/client` and `useAuth` modules). Started inspecting git
state before showing the proposed red commit message:*

> before every commit show me the commit message

> yes, commit it

*Implemented `api/client.js`, `useAuth.js`, wired `App.jsx`/`LoginPage.jsx` to green, verified
all four tests and the production build.*

> yes, commit it


## Frontend Step 4 — Employee list: static layout

**Claude Code (Sonnet)**

> employee list page for step 4 in design

*Found `EmployeeListPage.dc.html` already in `frontend/design/`, read it, translated the
design's "New Employee" button into a `Link` per the doc's own wording, stripped the working
pagination state down to a static layout, verified tests and the build.*

> yes commit it


## Interlude — Frontend dev server

**Claude Code (Sonnet)**

> run the frontend server too so that i can see while things are build

*Checked for a project-specific `run` skill (none found for this repo), fell back to the
generic server pattern: launched `npm run dev` in the background, then `curl`-smoke-tested
`/` and `/login` to confirm the app actually responds.*


## Frontend Step 5 — Employee list: wire to API

**Claude Code (Sonnet)**

> yes. lets start step 5

*Wrote `api/employees.js` and `hooks/useEmployees.js` before the test — caught the red-first
slip on its own, wrote `EmployeeListPage.test.jsx` next anyway, hit a router-context error
unrelated to the real assertions, wrapped the test render in `MemoryRouter`, reran and
confirmed the real red (static stub still showing).*

> yes

*Implemented the wiring, which broke two already-green `App.test.jsx` tests since
`EmployeeListPage` now fires its own mount-time fetches once authenticated. Rewrote those
mocks to route by URL instead of call order, fixed an ambiguous `getByText('Engineering')`
match by scoping to `getByRole('cell', ...)`, verified all 8 tests and the build.*

> go ahead and commit


## Frontend Step 6 — Employee detail: static layout

**Claude Code (Sonnet)**

*Session was `/clear`ed after the four `.dc.html` design files had already been read and two
gaps against the doc identified, but before they were resolved or recorded. The recap pasted
back in on resume cut off before showing what had actually been decided.*

> you were on step 6 of the frontend_developer_doc.md this is what you did in step 6 [...]
> Before scaffolding, I found two real gaps against the doc — same pattern as the earlier
> "New Employee" link question, worth flagging before I write anything. [...] User answered
> Claude's questions:

*Re-read the four design files against the doc, re-derived the same two gaps (missing
department/role/country in the detail header; missing Currency field in
`SalaryChangeModal`), and asked for confirmation directly rather than assuming the
unrecorded answers.*

> "Add the three fields (Recommended)"; "Add a Currency field (Recommended)"

*Scaffolded `EmployeeDetailPage.jsx` and the three modal components, verified the production
build and the running dev server, and proposed the commit message.*

> there was one more gap. as new employee button is the link there are other buttons on the
> employee detail page which are supposed to be link

*Checked Step 10's own test wording ("the button opens `StatusChangeModal`") and Steps 6/8/9's
prose, which call Change Salary/Correct Salary/Deactivate-Reactivate "buttons" throughout
since they open in-page modals; only Edit navigates to a distinct route. Reported this back
and asked which buttons were meant instead of guessing.*

> just edit, the rest stay buttons

> go ahead and commit


## Frontend Step 7 — Employee detail: fetch employee and salary history

**Claude Code (Sonnet)**

> start step 7

*Wrote `EmployeeDetailPage.test.jsx` against the still-static page, ran it, confirmed a real
red (no fetch calls made, no interactive corrections control), implemented `getEmployee`,
`api/salary.js`, and the `useEmployee`/`useSalaryHistory` hooks, wired the page to them, and
fixed a latent React key warning on the per-period fragment along the way.*

> yes, commit both


## Fix — Employee list row navigation to detail page

**Claude Code (Sonnet)**

> employee detail page is live but how to go to that page frpm employees page?

*Confirmed there was no way to reach the detail page from the list — neither the doc nor the
design file wires it.*

> "Whole row clickable (Recommended)"

*Wrote the failing test first (row click against a stub `/employees/:id` route), confirmed
red, then wired the row's `onClick` to `useNavigate`.*

> yes, commit both


## Frontend Step 8 — Salary change modal

**Claude Code (Sonnet)**

> start step 8

*Wrote `SalaryChangeModal.test.jsx` against the still-static modal (isolated component test,
not page-level), confirmed real red, implemented `recordSalaryChange`, turned the modal into a
controlled form, and added `refetch` to `useSalaryHistory`.*

> yes, commit both


## Frontend Step 9 — Salary correction modal

**Claude Code (Sonnet)**

> start step 9

*Flagged the conflict between Step 9's "opened from a specific history row" and Step 6's fixed
four-button design before writing anything.*

> "Add a per-row trigger instead"

*Wrote `SalaryCorrectionModal.test.jsx` against the still-static modal, confirmed red,
implemented `correctSalaryPeriod`, wired the modal as a controlled form, moved the correction
trigger to a per-row Correct button, and caught a native `required` attribute blocking the
server's 400 from ever surfacing.*

> yes, commit both


## Frontend Step 10 — Deactivate and reactivate

**Claude Code (Sonnet)**

> start step 10

*Tested at the page level this time rather than in isolation, since Step 10's cases depend on
the page's own employee state. Wrote all four tests against the still-demo modal, confirmed
red, implemented `deactivateEmployee`/`reactivateEmployee`, added `refetch` to `useEmployee`,
and turned `StatusChangeModal` into a controlled form.*

> yes, commit both


## Frontend Steps 11-13 — Employee form: static layout, create, edit

**Claude Code (Sonnet)**

> start step 11. employee form page already in design. complete step 12 and 13 too.

*Read `EmployeeFormPage.dc.html`, scaffolded the static form for both routes (flagged and
resolved the currency-list mismatch with Step 8 and the undocumented reference-data gap along
the way), committed. Wrote the three create-mode tests against the still-static form,
confirmed red, implemented `createEmployee` and the create-path submit handler with the
edit path left as a deliberate stub, committed. Extended the test file with the two edit-mode
cases, confirmed red against that stub, implemented the pre-fill effect and the edit-path
submit handler, committed. Auto Mode was active, so all five commits across the three steps
went straight through after showing each proposed message, rather than waiting for an
explicit go-ahead each time.

> log this in the ai workflow log


## Frontend Step 14 — Reports: static layout

**Claude Code (Sonnet)**

> start step 14 html is in design

*Read `ReportsPage.dc.html`, scaffolded the static reports page (date input, six report
cards, shared error banner), verified and committed. No tests, matching the static-layout
precedent.*


## Frontend Step 15 — Reports: wire to API

**Claude Code (Sonnet)**

> start step 15

*Wrote all four tests against the still-static page, confirmed red, implemented `getReport`
and `useReports`. Caught and fixed an ambiguous test assertion (three fixture reports reused
the same '73000.00' value, so `getByText` matched multiple elements) before it was mistaken
for a real bug.*

> log this in the ai workflow log


## Bug fix — CSRF 403 on every write endpoint, misreported as a logout

**Claude Code (Sonnet)**

> check if backend server is working

*Started checking docker/endpoint health; interrupted mid-check.*

> create employee functionality is logging me out

*Launched an investigation agent into the frontend's central 403 handler, the create-employee
request, and the backend's CSRF/CORS settings.*

> it is giving csrf error

*While the investigation was still running, confirmed the CSRF angle. Entered plan mode once
the agent's findings came back (missing `CSRF_TRUSTED_ORIGINS`), confirmed the root cause by
reading `settings.py` and both `.env` files directly, and asked whether to add a regression
test alongside the settings fix.*

> add one. do this in a red test + fix cycle

*Wrote the plan, got approval.*

> I think so it is not logging out but redirecting to login screen because of error in api

*Noted this matched the plan's own explanation already and proceeded unchanged. Wrote the red
test (`Client(enforce_csrf_checks=True)`, real session + cross-origin Origin header), confirmed
403, added `CSRF_TRUSTED_ORIGINS` to `settings.py` and both env files, discovered a plain
`docker compose restart` doesn't reread `env_file` and force-recreated the container instead,
reran the full suite (104 passed) plus ruff, then verified end-to-end against the live
containers with a real login + cross-origin create (misfired once on guessed reference-data
ids, then confirmed 201 with the real ones), cleaned up the throwaway test data.*

> log this in the ai workflow log
