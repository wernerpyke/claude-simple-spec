# Issues

Open questions and decisions to resolve, for later work.

## 1. Keep or cut bold announce-style leads (e.g. `**Why this matters for reports.**`)

**Status:** open

The rule "cut sentences that announce what follows rather than stating a fact" conflicts with keeping a short bold lead as a section signpost.

In eval iteration 1 on `examples/example-2.md`:
- The `readable-spec` skill **cut** the bold lead `**Why this matters for reports.**`, reading it as an announce sentence.
- Werner's human rewrite (`examples/example-2-human.md`) **kept** it as a signpost.

The skill and the human ground truth disagree on this case.

**To resolve:** decide the intended behaviour and encode it in `RULES.md` — either carve out an exception for short bold signpost leads, or confirm they should be cut. Then re-run the eval. Until resolved, the skill's cut-vs-keep choice here is not a defect.

## 2. How to handle duplication removal for a whole doc vs a diff/section

**Status:** open

The rules treat removing duplication as a goal, but "duplication" means different things depending on how much of the document the skill can see:

- **(a) Whole document.** The skill sees everything, so it can safely spot a fact stated twice and cut the redundant one.
- **(b) Diff or section only.** The skill sees a fragment. Text that looks redundant within the fragment may be the only statement of that fact in the wider document, or a deliberate restatement of something stated elsewhere. Cutting it could remove the fact entirely or break a cross-reference.

**To resolve:** decide how the skill should treat duplication when it lacks whole-document context, and encode it in `RULES.md` — e.g. only remove duplication that is fully contained within the visible text, leave cross-fragment duplication alone, or flag suspected duplication rather than cutting it. Then encode the behaviour in `SKILL.md` and add an eval.
