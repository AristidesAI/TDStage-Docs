#!/usr/bin/env python3
"""Build the troubleshooting page from the console's own fix hints.

The console already pairs every warning it can raise with the fix for it, in
`FIX_HINTS` in WebConsole/server.py, and Tools/check_fix_hints.py fails the
build if any message lacks one. Hand-copying that list into the documentation
would create a second copy to keep in step, and the copy would be the one that
goes stale. So the page is generated instead.

Usage:
    python3 tools/gen_troubleshooting.py [--repo ../TDStage] [--check]

--check exits 1 if the generated page differs from the one on disk, which is
what a CI job would run.
"""
import argparse
import pathlib
import re
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent / "operations" / "troubleshooting.md"

HEADER = """---
title: Troubleshooting
parent: Operations
nav_order: 9
---

# Troubleshooting

Symptoms the console can report, and what to do about each one.

This page is generated from the console's own fix hints, so it cannot drift
from the software. Do not edit it by hand. Regenerate it with:

```
python3 tools/gen_troubleshooting.py
```

Every row is a message the console raises, with the fix it offers. The console
shows the same text in its log and on the Rig health page, so what you read
here is what an operator sees at the desk.

"""

FOOTER = """
## When none of these match

Check the console log first: it names the device and the time, which usually
narrows a vague fault to one phone. Then confirm the stream is actually
arriving before changing anything else, because a dead link produces symptoms
that look like a dozen different faults.
"""


def readable(pattern: str) -> str:
    """Turn a hint's regex into the symptom text an operator would recognise.

    The patterns are written to match log lines, so they are already close to
    English. This strips the regex furniture and leaves the words.
    """
    s = pattern
    s = s.replace(r"\(s\)", "(s)")
    s = re.sub(r"\\([.()\[\]{}+*?^$|])", r"\1", s)   # unescape
    s = s.lstrip("^").rstrip("$")
    s = s.replace("|", " / ")
    return s.strip()


def load_hints(repo: pathlib.Path):
    """Read FIX_HINTS out of server.py without importing the console.

    Same trick as Tools/check_fix_hints.py: the list is a literal, so slicing
    the source between its definition and the next statement and exec-ing that
    avoids pulling in the console's imports and its sockets.
    """
    src = (repo / "WebConsole" / "server.py").read_text(encoding="utf-8")
    start = src.index("FIX_HINTS = [")
    end = src.index("_FIX_RX = ")
    ns: dict = {}
    exec("import re\n" + src[start:end], ns)          # noqa: S102 - our own source
    return ns["FIX_HINTS"]


def render(hints) -> str:
    rows = ["| Symptom | What to do |", "|---|---|"]
    for pattern, fix in hints:
        sym = readable(pattern).replace("|", "\\|")
        fx = fix.replace("|", "\\|")
        rows.append(f"| {sym} | {fx} |")
    return HEADER + "\n".join(rows) + "\n" + FOOTER


def demo():
    assert readable(r"^thermal|capture age") == "thermal / capture age"
    assert readable(r"commit\(s\) behind") == "commit(s) behind"
    assert readable(r"GB free") == "GB free"
    out = render([(r"a|b", "do the thing")])
    assert "| a / b | do the thing |" in out
    print("self-check ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage", help="the system repo checkout")
    ap.add_argument("--check", action="store_true", help="exit 1 if the page is stale")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        demo()
        return
    repo = pathlib.Path(a.repo).expanduser().resolve()
    if not (repo / "WebConsole" / "server.py").exists():
        sys.exit(f"no console source under {repo}. Pass --repo <path to TDStage>.")
    page = render(load_hints(repo))
    if a.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != page:
            sys.exit("troubleshooting.md is stale. Run: python3 tools/gen_troubleshooting.py")
        print("troubleshooting.md is current")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(load_hints(repo))} symptoms)")


if __name__ == "__main__":
    main()
