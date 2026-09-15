# Salary Management System — Requirements

**Client:** ACME Organisation · **User:** HR Manager

## Goal
Replace ACME's spreadsheet-based salary tracking for ~10,000 employees across multiple countries with a web application that holds employee records, maintains a full history of salary changes over time, and produces payroll reports for any date — not only the present.

## Scope
- **Access** — single authenticated admin user (HR Manager role).
- **Employee records** — create, view, update; search and filter by department, country, role, status. Employees are never deleted: they are marked inactive with an effective date, and can be viewed and reactivated.
- **Salary** — base, allowance and yearly bonus. Editing is two distinct operations the user chooses between: a *change*, applying from a date forward, or a *correction*, amending an existing period in place. Corrections are logged with a required reason, since they alter what historical reports return.
- **Reporting** — every report accepts an as-of date. Average salary by department and country, average bonus by department, total payroll cost, headcount by department and country. All aggregates use gross pay.
- **Bulk upload** — Excel roster, one row per employee, upserted on company employee ID. Creates new employees with their opening salary period; updates demographic fields only for existing ones. All-or-nothing validation with row-level errors.
- **Seed data** — Faker-based script generating representative employees and salary history.

## Key decisions and reasoning
- **Currency: single currency (USD), stored per record.** True multi-currency needs live exchange rates and a policy decision on which rate applies to a historical report — a client choice, not a developer one. Storing currency per record makes this a future reporting change rather than a schema migration.
- **Salary structure: base + allowance + yearly bonus, flat 10% deduction.** A flat rate with no threshold avoids inventing an arbitrary tax band and avoids the cliff where an employee earning marginally more takes home less. A transparent placeholder for a real tax engine.
- **Salary history: end-dated snapshot records, half-open periods.** Snapshots make resolving a salary for any date a single lookup, which is what an aggregate over 10,000 employees needs. Half-open intervals let consecutive periods chain without date arithmetic.
- **Reporting: time-aware.** Point-in-time reporting is the capability the spreadsheet cannot provide and the reason salary history exists. Reports resolve both salary and employment status as of the requested date.
- **Database: PostgreSQL.** The core value is analytical aggregation, where Postgres is strongest. It also provides exclusion constraints, used to guarantee salary periods never overlap regardless of which code path writes them — the invariant that makes time-aware reporting trustworthy.
- **Incomplete data fails loudly.** A report requested for a date before the earliest recorded salary is rejected rather than answered, and employees with no salary covering that date are reported as explicit exclusions. A payroll total that quietly omits people looks valid and is wrong.

## Deliberately out of scope
- **Multi-currency conversion** — requires live exchange rate data and a client policy decision on historical rates. The currency field exists, so this is additive.
- **Country-specific tax slabs** — jurisdiction rules are extensive, change annually, and are not what this exercise evaluates. A flat rate stands in.
- **Role-based authorisation tiers** — one role is implemented. Authentication and authorisation are separate concerns; only the latter is deferred, so tiers can be added without restructuring.
- **Bulk import of historical salary periods** — a real gap: history begins at migration, so pre-migration dates return the exclusion response until history accrues. Deferred because writing into already-occupied time ranges safely requires validation against stored history and a preview step, since a bad import silently rewrites past reports. The schema already supports arbitrary past periods, so nothing needs restructuring to add it.
- **Partial-success uploads** — all-or-nothing gives a simpler mental model: fix the file, upload again.
- **Distributed architecture** — narrow scope, single user; service boundaries would add operational complexity with nothing gained.

*Design decisions, data integrity rules, non-functional requirements, testing approach and extended tradeoff reasoning are documented separately.*
