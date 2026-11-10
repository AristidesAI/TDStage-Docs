#!/usr/bin/env python3
"""Build the proof-level page from the system repository's own README.

The project keeps one honest answer to "how far is this proven", in README.md:
a line per component with its evidence and the level that evidence supports.
That table is maintained because the people writing the code have to look at it.

A hand-written copy of it on this site would be a second answer to the same
question, and the published one is always the one that goes stale, which on
this page is the worst possible failure, because the whole point of it is that
a reader can trust the labels. The 2026-11-03 fact-check of a client document
found fifty-one errors and roughly all fifty-one leaned the same way: toward
sounding more finished than the evidence supported. Drift here does not wander,
it flatters.

So the page is generated, like the troubleshooting page, and `--check` fails CI
when it falls behind the README.

Usage:
    python3 tools/gen_status.py [--repo ../TDStage] [--check] [--working-tree]
"""
import argparse
import pathlib
import subprocess
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent / "reference" / "status.md"

WORKING_TREE = False

HEADER = """---
title: How far each part is proven
parent: Reference
nav_order: 7
---

# How far each part is proven

Every component, what state it is in, the evidence for that, and the level that
evidence supports. **A claim on this page without evidence beside it is a
defect in this page**, not a thing you may assume.

This page is generated from the system repository's own README, which is the
copy the people writing the code maintain. Do not edit it by hand. Regenerate
it with:

```
python3 tools/gen_status.py
```

"""

FOOTER = """
## Reading a level

Several rows carry a compound level: "Rig (one phone), Simulated", "Rig
(earlier builds)". That is not hedging. It means one part of the claim was
measured on real hardware and another was not, and the row names which is
which. Read the evidence column before quoting the row.

**Levels do not transfer.** A thing proven on one phone is not proven on eight;
a thing proven in a living room is not proven at stage distances, because the
room never tested the distance. A simulated result says the code does what it
was written to do. That is not nothing, and it is not the same as the rig
working.

The strongest single caveat on the whole project sits in the status line above:
the most phones placed and aligned together so far is two, in a living room.
Anything that depends on more phones, or on a stage, is designed or simulated
until the stage test produces its own evidence.

See [Evidence and claims](../operations/evidence.html) for how a number earns
its way onto this table in the first place, and what not to claim.
"""


def source_state(repo: pathlib.Path, rel: str):
    """The COMMITTED text of a source file, and a note saying which state.

    Same rule as the other generators: other sessions edit this checkout, so
    reading the working tree can publish a half-finished change as fact.
    """
    if WORKING_TREE:
        return (repo / rel).read_text(encoding="utf-8"), "working tree (--working-tree)"
    out = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                         capture_output=True, text=True, check=True).stdout
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    return out, f"committed {sha}"


def extract(readme: str):
    """(status paragraph, level definitions, table lines) from the README.

    Anchored on the headings and on the table's own first column rather than on
    line numbers, so an edit above the Status section cannot silently shift what
    this page publishes. A missing anchor raises instead of emitting a page with
    a section quietly absent.
    """
    lines = readme.split("\n")
    try:
        s = next(i for i, l in enumerate(lines) if l.startswith("**Status on "))
    except StopIteration:
        raise SystemExit("README.md has no '**Status on ...' line - re-point gen_status.py")
    e = s
    while e + 1 < len(lines) and lines[e + 1].strip():
        e += 1
    status = "\n".join(lines[s:e + 1])

    try:
        p = lines.index("Proven levels:")
    except ValueError:
        raise SystemExit("README.md has no 'Proven levels:' list - re-point gen_status.py")
    q = p + 1
    while q < len(lines) and lines[q].startswith("- "):
        q += 1
    levels = "\n".join(lines[p + 1:q])

    try:
        t = next(i for i, l in enumerate(lines) if l.startswith("| Component"))
    except StopIteration:
        raise SystemExit("README.md has no '| Component' table - re-point gen_status.py")
    u = t
    while u + 1 < len(lines) and lines[u + 1].startswith("|"):
        u += 1
    table = lines[t:u + 1]
    if len(table) < 3:
        raise SystemExit("the README's status table has no rows")
    return status, levels, table


def render(readme: str, note: str) -> str:
    status, levels, table = extract(readme)
    body = [
        status, "",
        "## The levels", "", levels, "",
        "## Every component", "",
        *table,
        "",                       # load-bearing: kramdown ends a table at a blank line
        f"*Generated from the system repository's README ({note}). "
        f"{len(table) - 2} components.*",
    ]
    return HEADER + "\n".join(body) + "\n" + FOOTER


def demo():
    readme = "\n".join([
        "# X", "",
        "**Status on 2026-01-01: pre-production.** Nothing has run on a stage.",
        "More of the same paragraph.", "",
        "## Status", "", "Proven levels:",
        "- **Rig**: real phones.",
        "- **Designed**: code only.", "",
        "| Component | State | Evidence | Level |",
        "|---|---|---|---|",
        "| Bridge | works | CI run 1 | Simulated |",
        "| Markers | never run | - | Designed |", "",
        "## Something else",
    ])
    out = render(readme, "committed abc1234")
    assert "**Status on 2026-01-01" in out and "More of the same paragraph." in out
    assert "- **Rig**: real phones." in out
    assert "| Bridge | works | CI run 1 | Simulated |" in out
    assert "## Something else" not in out          # the table stops at the blank line
    assert "2 components" in out
    import check_tables                            # the blank line after the table
    assert check_tables.problems_in(out.split("\n")) == [], \
        check_tables.problems_in(out.split("\n"))
    for missing, why in (("**Status on ", "status"), ("Proven levels:", "levels"),
                         ("| Component", "table")):
        broken = readme.replace(missing, "xx")
        try:
            render(broken, "n")
        except SystemExit:
            pass
        else:
            raise AssertionError(f"a README with no {why} anchor should not render")
    print("self-check ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--check", action="store_true", help="exit 1 if the page is stale")
    ap.add_argument("--working-tree", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    globals()["WORKING_TREE"] = a.working_tree
    if a.selftest:
        demo()
        return
    repo = pathlib.Path(a.repo).expanduser().resolve()
    if not (repo / "README.md").exists():
        sys.exit(f"no README.md under {repo}. Pass --repo <path to TDStage>.")
    page = render(*source_state(repo, "README.md"))
    if a.check:
        have = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if have != page:
            sys.exit(f"{OUT.name} is stale - run python3 tools/gen_status.py")
        print(f"{OUT.name} is current")
        return
    OUT.write_text(page, encoding="utf-8")
    rows = len(extract(source_state(repo, "README.md")[0])[2]) - 2
    print(f"wrote {OUT} ({rows} components)")


if __name__ == "__main__":
    main()
