# Example 4 — another document (Claude rewrite)

## SKS1. `SharpieSessionId` must be present and HttpOnly (2026-06-15)

**What.**
Login validates `SharpieSessionId` scoped to `sharpie.electrum.io` with `HttpOnly = true`.
If the cookie is absent or not HttpOnly, login fails immediately.

**Operation.** `login`

**Why.**
The HttpOnly flag signals that the server established the session correctly.
JavaScript cannot read an HttpOnly cookie.
Its absence means the login flow did not complete or the server did not set the session.

**Implications.**
A login that completes browser sign-in but does not result in a valid `SharpieSessionId` HttpOnly cookie is treated as failed.
The user sees a login error, not a silent partial session.

**First documented.** 2026-06-15.

---

## SKS2. Login sequence: two-phase detection with 300-second overall timeout (2026-06-15)

**What.**
Login proceeds in two phases.

1. Poll the browser URL every 500 ms until it leaves the `/login` path. This signals Google OAuth completed.
2. Poll `/api/reports/get` via in-page JS fetch every 500 ms until the response is JSON rather than HTML. This signals the Sharpie session is active and `SharpieSessionId` is live. Phase 2 has a 30-second budget.

The overall login flow has a 300-second wall-clock timeout.
If the user has not completed Google sign-in within that window, the browser is closed and login fails.

**Operation.** `login`

**Why.**
A redirect away from `/login` is necessary but not sufficient.
The session cookie may not yet be set.
The readiness probe against `/api/reports/get` confirms the session is functional before cookies are captured.

**Implications.**
A user who completes OAuth but whose session is not confirmed by the probe within 30 seconds will see a login failure.
A user who takes more than 300 seconds to complete Google sign-in will also see a login failure.

**First documented.** 2026-06-15.

---

## SKS3. Re-login destroys the existing session before establishing a new one (2026-06-15)

**What.**
Storing new cookies deletes the existing Keychain entry before writing the new one.
Running `login` when already authenticated invalidates the current session and replaces it.
There is no "refresh existing session" path. Login is always a full replacement.

**Operation.** `login`

**Why.**
The macOS Keychain rejects duplicate entries (`errSecDuplicateItem`).
Delete-then-add is the only safe write pattern.
Destroying the active session is a deliberate trade-off.

**Implications.**
A user who runs `login` mid-session will lose their current session before the new one is confirmed.
If the new login fails (e.g. browser timeout), they are left unauthenticated.

**First documented.** 2026-06-15.

---

## SKS4. Keychain coordinates for session storage (2026-06-15)

**What.**
Login stores session cookies in the macOS Keychain under service `sharpie`, key `session_cookies`.
These coordinates are shared across all skills in the plugin.
Every skill reads from the same entry.

**Operation.** `login`, `logout`, all authenticated commands

**Why.**
A single plugin-wide entry reflects the single login surface. There is one Sharpie session, not one per skill.
The coordinates are surfaced in the `help` envelope so users and operators can inspect or clear the entry manually.

**Implications.**
Changing either coordinate breaks cross-skill session sharing and invalidates any externally cached references to the Keychain entry.

**First documented.** 2026-06-15.

---

## SKS5. Three Keychain read outcomes determine authentication error codes (2026-06-15)

**What.**
Reading the session from the Keychain produces one of three outcomes, each mapping to a distinct error code:

- **Jar** (entry present and parseable). Session available. Proceed.
- **Absent**. Surfaces as `NOT_AUTHENTICATED`. The user has never logged in or has logged out.
- **Denied**[^sks5-denied]. Surfaces as `SESSION_EXPIRED`. The session exists but cannot be read.

A present but malformed entry is treated as Absent.

**Operation.** All authenticated commands

**Why.**
Absent and Denied are different user states that warrant different messages and remediation paths.
Absent means "run `login`". Denied means the OS is blocking access[^sks5-denied-why].

**Implications.**
Callers must not assume a missing session and a denied session are the same condition.
The error code signals what action the user should take.

**First documented.** 2026-06-15.

[^sks5-denied]: user cancelled Keychain access, or ACL denied
[^sks5-denied-why]: possibly a permissions issue, or the user dismissed the prompt

---

## SKS6. Data folder resolution rule (2026-06-15)

**What.**
The plugin resolves the data folder from session folder `S` as:

1. `S` itself, if it contains `reference_data/sharpie.db`.
2. Else the first subfolder of `S` among `sharpie-data/`, `sharpie_data/`, `sharpie/` that contains `reference_data/sharpie.db`.
3. Else absent → `DATA_FOLDER_NOT_FOUND`.

The canonical name is `sharpie-data/`. The `setup` command creates this name.
The plugin recognises the other two names as fallbacks for users who renamed by hand.

**Operation.** All commands

**Why.**
The resolution rule lets users maintain multiple independent workspaces by opening different folders in Claude Code.
The `sharpie.db` presence check ensures a folder that exists but has not been set up does not silently masquerade as a valid data folder.

**Implications.**
A user who opens a parent or sibling folder will not find a data folder created under a different folder.
The fallback names are not advertised. Users who rely on them may be surprised if the name changes in future.

**First documented.** 2026-06-15. Also stated in `dev-docs/ARCHITECTURE-PRINCIPLES.md` § *Data folder layout*.
