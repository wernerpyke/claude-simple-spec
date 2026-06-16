# Issues

Open questions and decisions to resolve, for later work.

## 1. Keep or cut bold announce-style leads (e.g. `**Why this matters for reports.**`)

**Status:** open

The rule "cut sentences that announce what follows rather than stating a fact" conflicts with keeping a short bold lead as a section signpost.

In eval iteration 1 on `examples/example-2.md`:
- The `simple-spec` skill **cut** the bold lead `**Why this matters for reports.**`, reading it as an announce sentence.
- Werner's human rewrite (`examples/example-2-human.md`) **kept** it as a signpost.

The skill and the human ground truth disagree on this case.

**To resolve:** decide the intended behaviour and encode it in `RULES.md` — either carve out an exception for short bold signpost leads, or confirm they should be cut. Then re-run the eval. Until resolved, the skill's cut-vs-keep choice here is not a defect.
