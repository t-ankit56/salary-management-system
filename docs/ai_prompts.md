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
