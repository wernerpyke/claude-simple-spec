#!/usr/bin/env python3
"""Build dist/ skills by stitching skeleton SKILL.md files with their source .md files.

Each skill lives under readability/ (or future sibling folders) as a skeleton SKILL.md
with marker comments. Running this script embeds the source files into each skeleton
and writes the result to dist/<skill-name>/SKILL.md. Re-run whenever any source file
or skeleton changes.

Usage:
    python build.py [--skeleton PATH] [--rules PATH] [--example PATH] [--out PATH] [--check]

--check exits non-zero if the dist output is out of date (for CI / pre-commit).
"""

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent   # build.py lives at repo root
DEFAULT_SKELETON = REPO / "readability/SKILL.md"
DEFAULT_RULES = REPO / "readability/RULES.md"
DEFAULT_EXAMPLE = REPO / "readability/WORKED-EXAMPLE.md"
DEFAULT_OUT = REPO / "dist/spec-readability/SKILL.md"

# Each embedded block is delimited by a START/END marker pair in the skeleton.
RULES_MARKERS = ("<!-- RULES:START -->", "<!-- RULES:END -->")
EXAMPLE_MARKERS = ("<!-- EXAMPLE:START -->", "<!-- EXAMPLE:END -->")


def render(skill_text: str, begin: str, end: str, content: str) -> str:
    start = skill_text.find(begin)
    stop = skill_text.find(end)
    if start == -1 or stop == -1 or stop < start:
        sys.exit(f"error: markers {begin!r} / {end!r} not found in skeleton SKILL.md")
    block = f"{begin}\n\n{content.strip()}\n\n{end}"
    return skill_text[:start] + block + skill_text[stop + len(end):]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skeleton", type=pathlib.Path, default=DEFAULT_SKELETON)
    ap.add_argument("--rules", type=pathlib.Path, default=DEFAULT_RULES)
    ap.add_argument("--example", type=pathlib.Path, default=DEFAULT_EXAMPLE)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if dist output is stale instead of writing")
    args = ap.parse_args()

    skeleton_text = args.skeleton.read_text()
    updated = render(skeleton_text, *RULES_MARKERS, args.rules.read_text())
    updated = render(updated, *EXAMPLE_MARKERS, args.example.read_text())

    if args.check:
        if not args.out.exists():
            sys.exit(f"dist output missing — run: python build.py")
        if updated != args.out.read_text():
            sys.exit(f"{args.out} is out of date — run: python build.py")
        print(f"{args.out} is up to date.")
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists() and updated == args.out.read_text():
        print(f"{args.out} already up to date.")
    else:
        args.out.write_text(updated)
        print(f"Built {args.out}.")


if __name__ == "__main__":
    main()
