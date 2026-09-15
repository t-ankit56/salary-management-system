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