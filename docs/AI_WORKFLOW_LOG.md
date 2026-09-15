# AI Workflow Log

Running record of AI use: what I asked for, what I kept, what I overrode.

---

## Requirements

**Tool:** Claude (conversational) → `requirements.md`

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
