#!/usr/bin/env python3
"""Embed the project's RULES.md into SKILL.md between marker comments.

RULES.md is the single source of truth for the rewriting rules. Running this
script copies the current rules into SKILL.md so the skill ships self-contained.
Re-run it whenever RULES.md changes.

Usage:
    python build.py [--rules PATH] [--skill PATH] [--check]

--check exits non-zero if SKILL.md is out of date (for CI / pre-commit).
"""

import argparse
import pathlib
import sys

BEGIN = "<!-- BEGIN RULES (generated from RULES.md — do not edit by hand) -->"
END = "<!-- END RULES -->"

REPO = pathlib.Path(__file__).resolve().parent   # build.py lives at repo root
DEFAULT_RULES = REPO / "RULES.md"
DEFAULT_SKILL = REPO / ".claude/skills/simple-spec/SKILL.md"


def render(skill_text: str, rules_text: str) -> str:
    start = skill_text.find(BEGIN)
    end = skill_text.find(END)
    if start == -1 or end == -1 or end < start:
        sys.exit(f"error: markers {BEGIN!r} / {END!r} not found in SKILL.md")
    block = f"{BEGIN}\n\n{rules_text.strip()}\n\n{END}"
    return skill_text[:start] + block + skill_text[end + len(END):]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=pathlib.Path, default=DEFAULT_RULES)
    ap.add_argument("--skill", type=pathlib.Path, default=DEFAULT_SKILL)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if SKILL.md is stale instead of writing")
    args = ap.parse_args()

    rules_text = args.rules.read_text()
    skill_text = args.skill.read_text()
    updated = render(skill_text, rules_text)

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
