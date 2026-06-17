#!/usr/bin/env python3
"""Embed RULES.md and WORKED-EXAMPLE.md into SKILL.md between marker comments.

RULES.md and WORKED-EXAMPLE.md are the single sources of truth for the rewriting
rules and the worked example. Running this script copies their current content
into SKILL.md so the skill ships self-contained. Re-run it whenever either file
changes.

Usage:
    python build.py [--rules PATH] [--example PATH] [--skill PATH] [--check]

--check exits non-zero if SKILL.md is out of date (for CI / pre-commit).
"""

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent   # build.py lives at repo root
DEFAULT_RULES = REPO / "RULES.md"
DEFAULT_EXAMPLE = REPO / "WORKED-EXAMPLE.md"
DEFAULT_SKILL = REPO / "skills/readable-spec/SKILL.md"

# Each embedded block is delimited by a START/END marker pair in SKILL.md.
RULES_MARKERS = ("<!-- RULES:START -->", "<!-- RULES:END -->")
EXAMPLE_MARKERS = ("<!-- EXAMPLE:START -->", "<!-- EXAMPLE:END -->")


def render(skill_text: str, begin: str, end: str, content: str) -> str:
    start = skill_text.find(begin)
    stop = skill_text.find(end)
    if start == -1 or stop == -1 or stop < start:
        sys.exit(f"error: markers {begin!r} / {end!r} not found in SKILL.md")
    block = f"{begin}\n\n{content.strip()}\n\n{end}"
    return skill_text[:start] + block + skill_text[stop + len(end):]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=pathlib.Path, default=DEFAULT_RULES)
    ap.add_argument("--example", type=pathlib.Path, default=DEFAULT_EXAMPLE)
    ap.add_argument("--skill", type=pathlib.Path, default=DEFAULT_SKILL)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if SKILL.md is stale instead of writing")
    args = ap.parse_args()

    skill_text = args.skill.read_text()
    updated = render(skill_text, *RULES_MARKERS, args.rules.read_text())
    updated = render(updated, *EXAMPLE_MARKERS, args.example.read_text())

    if args.check:
        if updated != skill_text:
            sys.exit("SKILL.md is out of date — run: python build.py")
        print("SKILL.md is up to date.")
        return

    if updated == skill_text:
        print("SKILL.md already up to date.")
    else:
        args.skill.write_text(updated)
        print(f"Embedded {args.rules} into {args.skill}.")


if __name__ == "__main__":
    main()
