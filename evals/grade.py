#!/usr/bin/env python3
"""Grade an iteration's runs against objective assertions.

Writes grading.json (fields: text, passed, evidence) and eval_metadata.json
into each run dir. Programmatic checks only — readability quality is judged
by the human in the viewer.

Usage: python grade.py <iteration-dir>
"""
import json, pathlib, re, sys

ITER = pathlib.Path(sys.argv[1]).resolve()
EVALS_DIR = pathlib.Path(__file__).resolve().parent   # evals/ at repo root
REPO = EVALS_DIR.parent
EX = REPO / "examples"

orig1 = (EX / "example-1.md").read_text()
orig2 = (EX / "example-2.md").read_text()
orig3 = (EX / "example-3.md").read_text()
base_added = (EVALS_DIR / "files/diff-repo-src/added-section.md").read_text()

# identifiers / facts that must survive each rewrite
IDS1 = ["connect_db", "connect_db_ro", "ensure_tables", "table_exists", "count_rows",
        "transaction", "sqlite3.connect()", "_shared/db/db.py", "db_path", "tmp_path",
        "dev-docs/adr/DB.md"]
IDS2 = ["get_reports_list", "run_report", "get_json", "_decode_response", "SessionExpiredError",
        "decode_response", "14 call sites", "print_output", "2026-05-18"]

def has_footnote(t): return bool(re.search(r"\[\^[\w-]+\]", t))
def no_interrupt(t):
    # Headings (titles) and footnote definitions legitimately keep em-dashes;
    # the rule targets em-dash / semicolon interruptions inside prose lines.
    prose = [l for l in t.splitlines()
             if not l.strip().startswith("[^") and not l.lstrip().startswith("#")]
    body = "\n".join(prose)
    return ";" not in body and "—" not in body
def all_present(t, ids): return [i for i in ids if i not in t]

def section(text, header):
    """Return the slice from a '## header' line to the next '## ' (exclusive)."""
    lines = text.splitlines(keepends=True)
    out, grab = [], False
    for l in lines:
        if l.startswith("## "):
            if grab: break
            grab = header in l
        if grab: out.append(l)
    return "".join(out)

def grade(name, variant):
    d = ITER / name / variant / "outputs"
    A = []
    if name == "whole-doc-sqlite":
        t = (d / "example-1.md").read_text()
        miss = all_present(t, IDS1)
        A.append(("All code identifiers / paths preserved", not miss, f"missing: {miss}" if miss else "all present"))
        A.append(("Uses named Markdown footnotes [^label]", has_footnote(t), "found [^...]" if has_footnote(t) else "none"))
        A.append(("No em-dash / semicolon interruptions in body", no_interrupt(t), "clean" if no_interrupt(t) else "still present"))
        A.append(("Split into multiple lines (one idea per line)", t.count("\n") >= 7, f"{t.count(chr(10))} newlines"))
    elif name == "whole-doc-http":
        t = (d / "example-2.md").read_text()
        miss = all_present(t, IDS2)
        A.append(("All code identifiers / facts preserved", not miss, f"missing: {miss}" if miss else "all present"))
        A.append(("Uses named Markdown footnotes [^label]", has_footnote(t), "found [^...]" if has_footnote(t) else "none"))
        A.append(("No em-dash / semicolon interruptions in body", no_interrupt(t), "clean" if no_interrupt(t) else "still present"))
    elif name == "section-only-accounting":
        t = (d / "example-3.md").read_text()
        sp1_o, sp2_o = section(orig3, "SP1."), section(orig3, "SP2.")
        sp1_n, sp2_n = section(t, "SP1."), section(t, "SP2.")
        A.append(("SP1 section byte-for-byte unchanged", sp1_o == sp1_n, "unchanged" if sp1_o == sp1_n else "MODIFIED"))
        A.append(("SP2 section byte-for-byte unchanged", sp2_o == sp2_n, "unchanged" if sp2_o == sp2_n else "MODIFIED"))
        sp3_o, sp3_n = section(orig3, "SP3."), section(t, "SP3.")
        A.append(("SP3 section actually rewritten", sp3_o != sp3_n and len(sp3_n) > 0, "changed" if sp3_o != sp3_n else "unchanged"))
        A.append(("Declined-quote facts preserved in SP3", all(k in t for k in ["DECLINED_STATUSES", "budget.py", '"Declined"']),
                  "preserved" if all(k in t for k in ["DECLINED_STATUSES", "budget.py", '"Declined"']) else "fact lost"))
    elif name == "git-diff-added-prose":
        t = (d / "docs/cache.md").read_text()
        storage = section(t, "Storage location")
        storage_o = section("## Storage location\n\nThe cache lives at `~/.sharpie/cache.db`.\nIt is a single SQLite file.\nDelete it to force a full re-fetch.\n", "Storage location")
        A.append(("Pre-existing 'Storage location' prose unchanged", storage.strip() == storage_o.strip(),
                  "unchanged" if storage.strip() == storage_o.strip() else "MODIFIED committed prose"))
        inval = section(t, "Invalidation")
        A.append(("Added 'Invalidation' section rewritten", base_added.strip() not in t and "Invalidation" in t,
                  "rewritten" if base_added.strip() not in t else "left as-is"))
        A.append(("Invalidation facts preserved", all(k in t for k in ["invalidate", "store.py", "15 minutes"]),
                  "preserved" if all(k in t for k in ["invalidate", "store.py", "15 minutes"]) else "fact lost"))
        filler = [w for w in ["genuinely", "additionally"] if w in inval.lower()]
        A.append(("Filler words removed (genuinely/additionally)", not filler, f"still present: {filler}" if filler else "removed"))

    expectations = [{"text": txt, "passed": bool(ok), "evidence": ev} for txt, ok, ev in A]
    json.dump({"expectations": expectations}, open(d.parent / "grading.json", "w"), indent=2)
    json.dump({"eval_name": name, "variant": variant, "assertions": [a["text"] for a in expectations]},
              open(d.parent / "eval_metadata.json", "w"), indent=2)
    return name, variant, sum(a["passed"] for a in expectations), len(expectations)

EVALS = ["whole-doc-sqlite", "whole-doc-http", "section-only-accounting", "git-diff-added-prose"]
for name in EVALS:
    for variant in ["with_skill", "without_skill"]:
        n, v, p, total = grade(name, variant)
        print(f"{n:28} {v:14} {p}/{total}")
