# Example 3 — long document (Claude rewrite)

## SP1. Timesheets with `Entry ID == null` are unsubmitted drafts (2026-05-23)

**What.**
A row returned by `/api/timesheets/get` whose `"Entry ID"` field is `null`[^sp1-null] is a draft the user has saved but not yet submitted for billing.
Drafts can still be edited or deleted.
They are *not* committed billing artefacts.

**Where it surfaces.**

- `/api/timesheets/get` returns `"Entry ID": null` for drafts and an integer ID for submitted rows.
- `/reports/run?report-id=18` **excludes** drafts entirely. They do not appear in any `action` bucket[^sp1-buckets].
- `/api/project/estimates-vs-actuals.summary.actuals.total-*` **excludes** drafts.

**Why we believe it.**
Werner, 2026-05-23.
Live evidence from the phase-3 step-9 freshness-rule investigation.
PEPKOR-081 had two non-Presales rows with `Entry ID = null` and amounts totalling 3,392.50 that the burn-down did not count.
See [`../adr/PROJECTS.md`](../adr/PROJECTS.md) item 16.

**Implications for our cache / commands.**

- `prj_timesheets.submitted` is populated at ingest from `int(api_row["Entry ID"] is not None)`.
  The freshness rule filters `SUM(amount)` on `submitted = 1`.
- The cache *still stores* draft rows[^sp1-drafts].
  Only their participation in the freshness comparison is filtered.
- Any future report pivoting over `prj_timesheets` that asks "what's billable?" should filter on `submitted = 1`.
  The opposite[^sp1-opposite] filters on `submitted = 0`.

**First documented.** 2026-05-23. See [`../adr/PROJECTS.md`](../adr/PROJECTS.md) item 16.

[^sp1-null]: JSON `null`, not `0` and not a string `""`
[^sp1-buckets]: `Logged`, `Invoiced`, or `Carried Over`
[^sp1-drafts]: with auto-assigned ROWIDs in place of the API's null Entry ID
[^sp1-opposite]: queries asking "show me drafts that need submitting"

---

## SP2. `Task = "Presales"` rows are non-billable (2026-05-23)

**What.**
Timesheet rows whose `"Task"` field is `"Presales"`[^sp2-case] are non-billable.
Sharpie's billing pipeline excludes them.
Every captured project with Presales rows shows `Amount = 0` on the timesheet endpoint.

**Where it surfaces.**

- `/api/timesheets/get` returns Presales rows with `"Amount": 0`[^sp2-nulls].
- `ref_tasks` lists `Presales` under multiple `task_type` groups[^sp2-task-types]. The rule applies regardless of `task_type`.
- `/reports/run?report-id=18` Σ(Logged.amount) excludes Presales.
- `/api/project/estimates-vs-actuals.summary.actuals.total-*` is consistent with Presales contributing zero.

**Why we believe it.**
Werner, 2026-05-23.
Live evidence from four sampled projects[^sp2-projects].
Every Presales row had `Amount = 0`.

**Implications for our cache / commands.**

- The non-billable nature is currently *structurally encoded* in the data.
  Every observed Presales row has `Amount = 0`, making a `SUM(amount)` filter a no-op against current data.
- No code-side filter is in place today.
  The empirical no-op makes it dead weight against current data.
  See [`../adr/PROJECTS.md`](../adr/PROJECTS.md) item 16.
- If a non-zero Presales row surfaces[^sp2-api-note], the freshness rule and `actuals_discrepancy` cross-check will disagree by that amount.
  Add an `AND task NOT IN (…)` filter to `prj_timesheets._cache_stats` at that point.
  Werner / Sharpie ops should supply the canonical non-billable task list.

**Open question.**
Is `Presales` the *only* always-non-billable task type, or are there others[^sp2-others]?
`ref_tasks` lists these task types but doesn't carry a billable flag.
Treat additional non-billable types as a follow-up if they cause `actuals_discrepancy` false-positives in the wild.

**First documented.** 2026-05-23. See [`../adr/PROJECTS.md`](../adr/PROJECTS.md) item 16.

[^sp2-case]: case-sensitive, matching the catalogue spelling in `ref_tasks`
[^sp2-nulls]: often with `"Invoice Period": null` and `"Invoiced Date": null`
[^sp2-task-types]: `SALES`, `SALES-NEW`, `Engineering`, `Visa`
[^sp2-projects]: CAPITEC-240 (6 rows), INVESTEC-072 (1 row), OLYMPUS-DISCOVERY (24 rows), PEPKOR-081 (2 rows)
[^sp2-api-note]: the API doesn't guarantee zero; this is an empirical observation, not a contract
[^sp2-others]: e.g. `IDLE`, `TRAINING`, internal `MANAGEMENT` tasks

---

## SP3. `/api/accounting/get` includes Declined quotes (2026-05-23)

**What.**
The `/api/accounting/get?projectCode=…` endpoint returns every quote and invoice ever associated with the project.
This includes quotes the customer declined.
A declined quote is identified by `"status": "Declined"` on the document body.
Filter declined quotes from any budget or actuals view.

**Where it surfaces.**

- `/api/accounting/get` response is `{<document_no>: {…, status, total, lines, …}}`. Declined documents are present with `"status": "Declined"`.
- `/api/projects/all` and `/api/project/estimates-vs-actuals` reflect whatever Xero is configured to count.

**Why we believe it.**
Long-standing.
Captured in phase 3 step 6's `budget.py` implementation.
The `DECLINED_STATUSES = {"Declined"}` set in `skills/projects/scripts/budget.py` is the canonical place this filter lives.

**Implications for our cache / commands.**

- `budget._filter_accounting` drops rows whose `status` is in `DECLINED_STATUSES` before shaping the envelope's `accounting` list.
- A future *audit* command or quote-history view would want the unfiltered list[^sp3-audit].
  At that point the filter becomes a flag rather than a hard-coded exclusion.

**First documented.** Phase 3 step 6[^sp3-commit]. Recorded here 2026-05-23.

[^sp3-audit]: to show the full negotiation history
[^sp3-commit]: commit `f42456a`
