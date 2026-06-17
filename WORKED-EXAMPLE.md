Original AI prose:

> **All SQLite access goes through the single seam at `skills/_shared/db/`** (`connect_db`, `connect_db_ro`, `ensure_tables`, ...). It's worth noting that no skill calls `sqlite3.connect()` directly — the only `sqlite3.connect()` calls live inside `_shared/db/db.py`. The seam is genuinely **stateless**: callers pass an explicit `db_path` (no module-global path, no connection caching).

Apply the phases in order.

**Phase 1 — cut.** Drop "It's worth noting that" (announces what follows) and "genuinely" (intensifier carrying no fact):

> **All SQLite access goes through the single seam at `skills/_shared/db/`** (`connect_db`, `connect_db_ro`, `ensure_tables`, ...). No skill calls `sqlite3.connect()` directly — the only `sqlite3.connect()` calls live inside `_shared/db/db.py`. The seam is **stateless**: callers pass an explicit `db_path` (no module-global path, no connection caching).

**Phase 2 — structure.** One idea per sentence, lead with the actor, and turn the em-dash and the colon into full stops:

> **All SQLite access goes through the single seam at `skills/_shared/db/`** (`connect_db`, `connect_db_ro`, `ensure_tables`, ...).
> No skill calls `sqlite3.connect()` directly.
> The only `sqlite3.connect()` calls live inside `_shared/db/db.py`.
> The seam is **stateless**.
> Callers pass an explicit `db_path` (no module-global path, no connection caching).

**Phase 3 — footnotes.** Move the two long asides to footnotes at the bottom of the section. The helper list sits in parentheses; "no module-global path, no connection caching" is a clarification of more than four words. Both move. A four-word-or-less aside would stay inline:

> **All SQLite access is via `skills/_shared/db/`[^db-helpers].**
> No skill calls `sqlite3.connect()` directly.
> The only `sqlite3.connect()` calls live inside `_shared/db/db.py`.
> The seam is **stateless**. Callers pass an explicit `db_path`[^db-stateless].
>
> [^db-helpers]: `connect_db`, `connect_db_ro`, `ensure_tables`, ...
> [^db-stateless]: no module-global path, no connection caching

Note what happened: the announce clause and the intensifier are gone, one idea sits per line, the em-dash and colon became full stops, the helper list and the stateless clarification moved to footnotes, and every fact survived.
