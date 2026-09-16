# Salary Management System — Project Standards

Web-based salary management for ACME Organisation. Employee records, full salary history
over time, and payroll reporting for any date.

Monorepo: `backend/` (Django, DRF, PostgreSQL) and `frontend/` (React). Each has its own
`CLAUDE.md` with stack-specific conventions. This file covers what applies to both.

Scope and rationale: `docs/requirements.md`

---

## Working agreement

Development is test-first. Every behaviour is built in a red-green-refactor cycle.

- Write the failing test first, and run it to confirm it fails for the expected reason.
- Commit the failing test as `test: <behaviour> (red)` before implementing.
- Implement the minimum that makes it pass. Nothing more.
- Commit the implementation as `feat:` or `fix:` once green.
- Refactor only once green, as a separate commit with tests still passing.
- One behaviour per cycle. Every cycle produces at least two commits.
- Do not add functionality that no current test requires.
- Do not weaken, skip, or delete a test to make a suite pass. A failing test is
  information; find out what it is telling you.
- If a requirement is ambiguous, stop and ask rather than choosing an interpretation.

## Domain rules

These hold across the whole system, frontend included. They are invariants, not
preferences.

- A salary **change** applies from a date forward and preserves history. A **correction**
  amends an existing period in place and is logged with its previous values and a reason.
  These are distinct operations and are never merged into a single "edit salary" action.
- Every salary change requires an effective date. It is never defaulted silently.
- Current salary is resolved from salary history by date, never stored separately and
  never assumed to be the most recent record — a future-dated change makes those different
  answers.
- Money is an exact decimal at every layer, in transit and in storage. Never a float, in
  Python or in JavaScript.
- All aggregate reports use gross pay. Net appears only on an individual employee record.
- Employees are never deleted. They are deactivated, with an effective date.
- Reports never silently omit employees. Missing data surfaces as an explicit exclusion
  count or a rejected request, never as a smaller number presented as complete.

## Commits

Small and frequent, one behaviour each. Every red-green cycle is committed as a pair: the
failing test, then the implementation. Conventional Commit prefixes:

| Prefix | Use |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fixes |
| `test:` |  A failing test, committed before its implementation; or test-only changes  |
| `refactor:` | Restructuring without behaviour change |
| `docs:` | Documentation only, including the AI workflow log and prompt log |
| `chore:` | Setup, config, non-feature work |

Every commit message has a body, not just the Conventional Commit subject line: a sentence
or two describing what the change does. A one-line `type: subject` with nothing beneath it
is not enough.

When an AI assistant is doing the committing: as soon as the change is ready to commit,
show the proposed subject and body up front, unprompted — don't wait to be asked what
message will be used, and don't commit silently.

## Out of bounds

- Do not add dependencies without asking.
- Do not change project scope. Scope decisions live in `docs/requirements.md` and are
  settled; if something appears to be missing, raise it rather than building it.
- Do not commit secrets or environment files.
