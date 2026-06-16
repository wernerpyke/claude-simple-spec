# Example 1 — SQLite seam (AI-generated)

**All SQLite access goes through the single seam at `skills/_shared/db/`** (`connect_db`, `connect_db_ro`, `ensure_tables`, `table_exists`, `count_rows`, `transaction`). No skill calls `sqlite3.connect()` directly — the only `sqlite3.connect()` calls in the codebase live inside `_shared/db/db.py`. The seam is **stateless**: callers pass an explicit `db_path` (no module-global path, no connection caching); test fixtures override by passing a `tmp_path` DB. Decision record: `dev-docs/adr/DB.md`.
