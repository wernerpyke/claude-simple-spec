# Example 1 — SQLite seam (Claude rewrite)

**All SQLite access is via `skills/_shared/db/`**[^db-api].
No skill calls `sqlite3.connect()` directly.
The only `sqlite3.connect()` calls in the codebase live inside `_shared/db/db.py`.
SQLite access is **stateless**.
Callers pass an explicit `db_path`[^db-path].
Test fixtures override by passing a `tmp_path` DB.
Decision record: `dev-docs/adr/DB.md`.

[^db-api]: `connect_db`, `connect_db_ro`, `ensure_tables`, `table_exists`, `count_rows`, `transaction`
[^db-path]: no module-global path, no connection caching
