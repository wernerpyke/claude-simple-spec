# Documentation Grammar Rules

This project defines grammar rules for rewriting AI-generated technical documentation to make it easier to read.

## Goal

Iteratively define and refine rules that can be applied to AI-generated technical prose — particularly documentation, ADRs, and developer guides — to improve readability.

A Claude Code skill applies `RULES.md` to rewrite, as instructed by the human:
1. A whole document.
2. A section of a document.
3. A git diff.

## Files

- `RULES.md` — the rewriting rules (standalone)
- `WORKED-EXAMPLE.md` — the worked example shown in the skill (standalone)
- `examples/` — flat files, up to three per example:
  - `example-N.md` — original AI-generated text
  - `example-N-human.md` — rewritten by Werner (only examples 1 and 2)
  - `example-N-rewritten.md` — rewritten by Claude using RULES.md
- `skills/readable-spec/SKILL.md` — the `/readable-spec` skill, and the only file that ships. Applies `RULES.md` to a document, a section, or a git diff. The rules and worked example are embedded into `SKILL.md`, so it is self-contained.
- `build.py` — dev tool. Embeds `RULES.md` and `WORKED-EXAMPLE.md` into `SKILL.md` between markers. Re-run after editing either; `--check` verifies they are in sync. Not shipped.
- `evals/` — dev tooling for testing the skill (`evals.json`, `setup_run.sh`, `grade.py`, `files/`). Eval runs are scratch under `/tmp/readable-spec-evals/`. Not shipped.

## Examples

- Example 1 — SQLite seam / `_shared/db/`
- Example 2 — HTTP/API client consolidation ADR entry
- Example 3 — Timesheet and accounting rules (long document)
- Example 4 — Keychain session rules
