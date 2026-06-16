# Example 1 — SQLite seam (human rewrite)

**All SQLite access is via `skills/_shared/db/`[1]**. 
No skill calls `sqlite3.connect()` directly. 
The only `sqlite3.connect()` calls in the codebase live inside `_shared/db/db.py`. 
SQLite access is **stateless**. Callers pass an explicit `db_path`[2].
Test fixtures override by passing a `tmp_path` DB. 
Decision record: `dev-docs/adr/DB.md`.

[1] `connect_db`, `connect_db_ro`, `ensure_tables`, `table_exists`, `count_rows`, `transaction`
[2] no module-global path, no connection caching
