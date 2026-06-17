#!/usr/bin/env bash
# Build per-run input directories for one eval iteration.
#
# Usage: bash setup_run.sh [iteration-dir]
#
# The eval workspace is scratch — input copies, per-run outputs, grading, and
# benchmark files. It does NOT belong in the repo. It defaults to a tmp
# location and should be deleted once the eval is reviewed:
#     rm -rf /tmp/readable-spec-evals
#
# Creates <iteration-dir>/<eval-name>/{with_skill,without_skill}/outputs/ populated
# with each eval's input files (in-place editing targets).
set -euo pipefail

ITER="${1:-/tmp/readable-spec-evals/iteration-1}"
EVALS_DIR="$(cd "$(dirname "$0")" && pwd)"        # evals/ at repo root
REPO_ROOT="$(cd "$EVALS_DIR/.." && pwd)"
EXAMPLES="$REPO_ROOT/examples"
DIFFSRC="$EVALS_DIR/files/diff-repo-src"

# Scratch workspace — always start from a clean slate so re-runs are idempotent
# and never clobber a half-built or completed iteration.
rm -rf "$ITER"

mk() { mkdir -p "$1/outputs"; }

for variant in with_skill without_skill; do
  # eval-0 / eval-1 / eval-2 — copy a single markdown file to edit in place
  d="$ITER/whole-doc-sqlite/$variant";        mk "$d"; cp "$EXAMPLES/example-1.md" "$d/outputs/example-1.md"
  d="$ITER/whole-doc-http/$variant";          mk "$d"; cp "$EXAMPLES/example-2.md" "$d/outputs/example-2.md"
  d="$ITER/section-only-accounting/$variant"; mk "$d"; cp "$EXAMPLES/example-3.md" "$d/outputs/example-3.md"

  # eval-3 — a real git repo with a committed base and an uncommitted added section
  d="$ITER/git-diff-added-prose/$variant/outputs"; mkdir -p "$d/docs"
  cp "$DIFFSRC/base.md" "$d/docs/cache.md"
  git -C "$d" init -q
  git -C "$d" config user.email eval@example.com
  git -C "$d" config user.name eval
  git -C "$d" add docs/cache.md
  git -C "$d" commit -qm "initial cache notes"
  cat "$DIFFSRC/added-section.md" >> "$d/docs/cache.md"   # uncommitted change
done

echo "Set up runs under $ITER"
