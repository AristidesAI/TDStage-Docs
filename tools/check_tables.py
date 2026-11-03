#!/usr/bin/env python3
"""Tables that render on GitHub but not on the site.

The site is built by GitHub Pages with kramdown. GitHub's own Markdown view,
and `gh api /markdown`, use cmark-gfm. They disagree about where a table ends,
and the disagreement is silent: the table looks right everywhere an author
checks it and renders as a wall of pipes on the published page.

kramdown reads a table as the block of lines up to the next BLANK line. If any
line in that block is not a table line, it is not a table at all, and the rows
become one paragraph. cmark-gfm instead ends the table at the first line that
is not a row, so the same source renders.

That is what happened to operations/troubleshooting.md: the generator wrote the
next `##` heading straight after the last row with no blank line between them,
and a 79-row table published as a 18,000-character paragraph (2026-11-03).

So: a table row may not touch a non-table line, on either side. The table that
cannot interrupt a paragraph above it is the same rule from the other end.

Usage:
    python3 tools/check_tables.py [--selftest]
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"_includes", "_sass", "_site", "assets", ".git"}


def problems_in(lines):
    """[(line number, what)] for every table edge that touches prose.

    Line numbers are 1-based and name the non-table line, because that is the
    line to put a blank line next to.
    """
    out = []
    fence = False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence
            continue
        if fence or not s.startswith("|"):
            continue
        if i and lines[i - 1].strip() and not lines[i - 1].strip().startswith("|"):
            out.append((i, "a table starts under a line of prose "
                           "(kramdown will not let a table interrupt a paragraph)"))
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt and not nxt.startswith("|"):
            out.append((i + 2, "a table runs straight into a non-table line "
                               "(kramdown then renders the whole table as a paragraph)"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        demo()
        return
    bad, pages = [], 0
    for p in sorted(ROOT.rglob("*.md")):
        if set(p.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        pages += 1
        for ln, why in problems_in(p.read_text(encoding="utf-8").split("\n")):
            bad.append(f"{p.relative_to(ROOT)}:{ln}: {why}")
    if bad:
        print("\n".join("  " + b for b in bad))
        print(f"\n{len(bad)} problem(s) across {pages} page(s); add a blank line")
        sys.exit(1)
    print(f"{pages} pages: every table is fenced by blank lines")


def demo():
    good = ["text", "", "| a | b |", "|---|---|", "| 1 | 2 |", "", "## next"]
    assert problems_in(good) == [], problems_in(good)
    glued = ["| a | b |", "|---|---|", "| 1 | 2 |", "## next"]
    assert [ln for ln, _ in problems_in(glued)] == [4], problems_in(glued)
    interrupt = ["prose", "| a | b |", "|---|---|", ""]
    assert [ln for ln, _ in problems_in(interrupt)] == [1], problems_in(interrupt)
    fenced = ["```", "| not | a table |", "```", ""]
    assert problems_in(fenced) == [], problems_in(fenced)
    assert problems_in(["| a |"]) == []          # last line of the file
    print("self-check ok")


if __name__ == "__main__":
    main()
