# Example 2 — HTTP/API client consolidation (Claude rewrite)

## R7. HTTP/API client consolidated into `_shared/api/` (2026-05-18)

The reports skill's HTTP calls[^http-calls] now route through `skills/_shared/api/client.py::get_json(session, path, *, params, timeout)`.
It no longer uses the pre-strict-envelope pattern[^envelope].
The projects skill drove the migration.
Phase 3 was about to add three new HTTP call sites, and the plugin already had three distinct call styles[^call-styles].
A pre-refactor assessment recommended consolidation.

**Why this matters for reports.**
The reports skill's public function signatures didn't change.
`get_reports_list` and `run_report` still return `None` on failure and let callers' `print_output` callbacks render the error.
Only the internal HTTP/decode mechanics moved.

The migration also fixed a latent bug.
HTML-instead-of-JSON responses[^session-expiry] used to leak `ValueError` from `.json()` in the catalogues path.
Post-migration they raise `SessionExpiredError` cleanly.

`decode_response` is now internal to `_shared/api/` and consumed only by `get_json`.
It was originally a private helper in `reports.py`.

[^http-calls]: `get_reports_list`, `run_report`, the metadata endpoints
[^envelope]: `session.get` → `_decode_response` → `print_output + return None`
[^call-styles]: `reports` print-and-return-None, `projects/fetch` raw `.json()`, `projects/api` typed-error
[^session-expiry]: session expiry
