
## Invalidation

The cache is invalidated through the single `invalidate()` helper in `cache/store.py` (`invalidate`, `invalidate_all`, `touch`) — no command clears rows directly, which keeps the eviction policy in one place. The TTL is genuinely short: entries older than 15 minutes are considered stale and are additionally re-fetched on the next read (this avoids serving data that the upstream API may have changed). Writes are performed by the ingest path, which opens a transaction (begins a transaction and commits at the end) exactly like the read path does.
