# Example 3 — long document

## SP1. Timesheets with `Entry ID == null` are unsubmitted drafts (2026-05-23)

**What.** A row returned by `/api/timesheets/get` whose `"Entry ID"`
field is `null` (JSON `null`, not `0` and not a string `""`) is a draft
the user has saved but not yet submitted for billing. Drafts can still
be edited or deleted; they are *not* committed billing artefacts.

**Where it surfaces.**

- `/api/timesheets/get` returns `"Entry ID": null` for drafts and an
  integer ID for submitted rows.
- `/reports/run?report-id=18` (the per-month burn-down) **excludes**
  drafts entirely — they do not appear in any `action` bucket (`Logged`,
  `Invoiced`, or `Carried Over`).
- `/api/project/estimates-vs-actuals.summary.actuals.total-*`
  **excludes** drafts (consistent with the burn-down).

**Why we believe it.** Werner, 2026-05-23 (assertion). Live evidence
captured the same day during the phase-3 step-9 freshness-rule
investigation: PEPKOR-081 had two non-Presales rows with `Entry ID =
null` and amounts totalling 3,392.50 that the burn-down did not count.
The decision to filter on `submitted = 1` is recorded in
[`../adr/PROJECTS.md`](../adr/PROJECTS.md)
item 16.

**Implications for our cache / commands.**

- `prj_timesheets.submitted` (added phase 3 step 9b) is populated at
  ingest from `int(api_row["Entry ID"] is not None)`. The freshness rule
  filters `SUM(amount)` on `submitted = 1` so the equality holds against
  the burn-down's Logged total.
- The cache *still stores* draft rows (with auto-assigned ROWIDs in
  place of the API's null Entry ID); only their participation in the
  freshness comparison is filtered.
- Any future report that pivots over `prj_timesheets` and asks "what's
  billable?" should also filter on `submitted = 1`. The opposite — "show
  me drafts that need submitting" — would filter on `submitted = 0`.

**First documented.** 2026-05-23, alongside the phase-3 step-9
freshness-rule investigation (recorded in
[`../adr/PROJECTS.md`](../adr/PROJECTS.md)
item 16).

## SP2. `Task = "Presales"` rows are non-billable (2026-05-23)

**What.** Timesheet rows whose `"Task"` field is exactly `"Presales"`
(case-sensitive, matching the catalogue spelling in `ref_tasks`) are
non-billable activity. Sharpie's billing pipeline excludes them; in
every captured project where Presales rows appear they have `Amount = 0`
on the timesheet endpoint.

**Where it surfaces.**

- `/api/timesheets/get` returns Presales rows with `"Amount": 0` (and
  often with `"Invoice Period": null` and `"Invoiced Date": null`, since
  there is nothing to invoice).
- `ref_tasks` lists `Presales` under multiple `task_type` groups
  (`SALES`, `SALES-NEW`, `Engineering`, `Visa`); the rule applies
  regardless of `task_type`.
- `/reports/run?report-id=18` Σ(Logged.amount) excludes Presales (zero
  contribution by virtue of `Amount = 0`).
- `/api/project/estimates-vs-actuals.summary.actuals.total-*` is also
  consistent with Presales contributing zero.

**Why we believe it.** Werner, 2026-05-23 (assertion). Live evidence
across the four projects with Presales rows we sampled: CAPITEC-240 (6
rows), INVESTEC-072 (1 row), OLYMPUS-DISCOVERY (24 rows), PEPKOR-081 (2
rows) — every Presales row had `Amount = 0`.

**Implications for our cache / commands.**

- The non-billable nature is currently *structurally encoded* in the
  data — every observed Presales row has zero amount, so filtering them
  out of `SUM(amount)` is a no-op against the data we have.
- No code-side filter is in place today (the phase-3 step-9 freshness
  rebaseline deliberately deferred the task-type filter; the empirical
  no-op makes it dead weight against current data — see
  [`../adr/PROJECTS.md`](../adr/PROJECTS.md)
  item 16).
- If a non-zero Presales row ever surfaces (the API doesn't guarantee
  zero — that's an empirical observation, not a contract), the
  freshness rule and the `actuals_discrepancy` cross-check will
  disagree by exactly that amount. Add an `AND task NOT IN (…)` filter
  to `prj_timesheets._cache_stats` at that point. The canonical
  non-billable task list should come from Werner / Sharpie ops rather
  than be inferred from data.

**Open question.** Is `Presales` the *only* always-non-billable task
type, or are there others (e.g. `IDLE`, `TRAINING`, internal `MANAGEMENT`
tasks)? `ref_tasks` lists these task types but doesn't carry a billable
flag. Treat additional non-billable types as a follow-up question if
they cause `actuals_discrepancy` false-positives in the wild.

**First documented.** 2026-05-23, alongside the phase-3 step-9
freshness-rule investigation (recorded in
[`../adr/PROJECTS.md`](../adr/PROJECTS.md)
item 16).

## SP3. `/api/accounting/get` includes Declined quotes (2026-05-23)

**What.** The `/api/accounting/get?projectCode=…` endpoint returns every
quote and invoice ever associated with the project — including ones the
customer declined. A declined quote is identified by `"status":
"Declined"` on the document body. Declined quotes are not part of the
project's "live financial position" and should be filtered out for any
budget / actuals view.

**Where it surfaces.**

- `/api/accounting/get` response is `{<document_no>: {…, status,
  total, lines, …}}`. Declined documents are present with
  `"status": "Declined"`.
- `/api/projects/all` and `/api/project/estimates-vs-actuals` reflect
  whatever Xero (the accounting back-end) is configured to count.

**Why we believe it.** Long-standing — captured in phase 3 step 6's
`budget.py` implementation. The `DECLINED_STATUSES = {"Declined"}` set
in `skills/projects/scripts/budget.py` is the canonical place this
filter lives.

**Implications for our cache / commands.**

- `budget._filter_accounting` drops rows whose `status` is in
  `DECLINED_STATUSES` before shaping the envelope's `accounting` list.
- A future *audit* command or quote-history view would want the
  unfiltered list (to show the full negotiation history). At that
  point the filter becomes a flag rather than a hard-coded exclusion.

**First documented.** Phase 3 step 6 (commit `f42456a`); recorded here
2026-05-23.