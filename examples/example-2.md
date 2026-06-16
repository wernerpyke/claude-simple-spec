# Example 2 — HTTP/API client consolidation (AI-generated)

## R7. HTTP/API client consolidated into `_shared/api/` (2026-05-18)

The reports skill's HTTP calls (`get_reports_list`, `run_report`, the metadata endpoints) now route through `skills/_shared/api/client.py::get_json(session, path, *, params, timeout)` rather than the pre-strict-envelope pattern of `session.get` → `_decode_response` → `print_output + return None`. The migration was driven by the projects skill: phase 3 was about to add three new HTTP call sites, and the plugin already had three distinct call styles (`reports` print-and-return-None, `projects/fetch` raw `.json()`, `projects/api` typed-error). A pre-refactor assessment surveyed 14 call sites across all skills and recommended consolidation.

**Why this matters for reports.** The reports skill's public function signatures didn't change — `get_reports_list` and `run_report` still return `None` on failure and let callers' `print_output` callbacks render the error. Only the internal HTTP/decode mechanics moved. A latent bug was fixed in passing: HTML-instead-of-JSON responses (session expiry) used to leak `ValueError` from `.json()` in the catalogues path; post-migration they raise `SessionExpiredError` cleanly. `decode_response`, originally a private helper in `reports.py`, is now internal to `_shared/api/` and consumed only by `get_json`.
