---
name: spec-readability
description: Rewrite AI-generated technical prose for readability using this project's documentation grammar rules. Use whenever the user wants to clean up, tighten, simplify, or improve the readability of documentation, ADRs, READMEs, developer guides, or design docs — or asks to "apply the rules" / "run the grammar rules" / run "/spec-readability" on a file, a section, or a git diff. Trigger even when the user doesn't name the rules explicitly but clearly wants AI-sounding docs made easier to read.
---

# Spec Readability

Rewrite AI-generated technical documentation so a human can read it quickly, by applying the grammar rules embedded below. The rules are the contract — apply them, don't paraphrase them.

## What you preserve

The rewrite changes *form*, never *facts*. Keep every claim, every code identifier (`like_this`), every path, every number, and the document's heading structure. You are reorganising sentences and moving asides into footnotes — not summarising, not adding, not deleting information. If a sentence carries a fact, that fact must survive somewhere in the output (often as a footnote).

## Pick the mode

The user is asking for one of three scopes. Work out which from their request:

1. **Whole document** — "rewrite `guide.md`", "clean up this doc". Apply the rules to the entire file.
2. **A section** — "rewrite the *Caching* section", "just the second paragraph". Apply the rules only to that span; leave the rest of the file byte-for-byte unchanged.
3. **A git diff** — "rewrite what I just added", "apply the rules to my changes". The target is the *newly added or changed prose* in the working tree, not the whole file. See below.

If the scope is ambiguous, ask before editing — rewriting a whole file when they meant one section is annoying to undo.

## How to apply

Edit the file **in place** using the editing tools. The user reviews your work as a diff, so in-place edits are the natural fit — don't write a separate `-rewritten.md` file unless asked.

Work section by section. For each section:
1. Read it and identify the facts, the asides, and the announce/restate filler.
2. Rewrite per the rules below.
3. Collect the asides into footnotes at the **end of that section**, not the end of the document.

After editing, briefly tell the user what changed at a high level (e.g. "split long sentences, moved the four DB helper names to a footnote") so they know what to look for in the diff.

### Git diff mode

When the scope is a diff:
1. Run `git diff` (and `git diff --staged` if relevant) to see what changed. If nothing is staged/unstaged, ask which range they mean.
2. Identify the **added or modified prose** — added lines (`+`) that are documentation text. Ignore deletions, code, and unchanged context.
3. Rewrite that prose in place in the actual files, leaving untouched lines alone.
4. Don't rewrite text the diff didn't touch, even if it also violates the rules — the user scoped you to their change.

## The rules

<!-- RULES:START -->
<!-- RULES:END -->

## A worked example

<!-- EXAMPLE:START -->
<!-- EXAMPLE:END -->
