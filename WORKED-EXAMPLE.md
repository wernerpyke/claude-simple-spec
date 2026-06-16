Original AI prose:

> **All SQLite access goes through the single seam at `skills/_shared/db/`** (`connect_db`, `connect_db_ro`, `ensure_tables`, ...). No skill calls `sqlite3.connect()` directly — the only `sqlite3.connect()` calls live inside `_shared/db/db.py`. The seam is **stateless**: callers pass an explicit `db_path` (no module-global path, no connection caching).

Rewritten:

> **All SQLite access is via `skills/_shared/db/`[^db-helpers].**
> No skill calls `sqlite3.connect()` directly.
> The only `sqlite3.connect()` calls live inside `_shared/db/db.py`.
> SQLite access is **stateless**. Callers pass an explicit `db_path`[^db-stateless].
>
> [^db-helpers]: `connect_db`, `connect_db_ro`, `ensure_tables`, ...
> [^db-stateless]: no module-global path, no connection caching

Note what happened: one idea per line, the em-dash interruption became a full stop, the parenthetical helper list and the stateless clarification moved to footnotes, and every fact survived.
