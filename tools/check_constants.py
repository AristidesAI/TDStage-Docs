#!/usr/bin/env python3
"""Pin the numbers written in prose to the constants they came from.

The same failure has now happened twice. A number is copied out of the code
into a sentence, the constant moves, and the sentence stays: the project
version sat at v78 while the code reached v80, and every bandwidth figure was
computed at a grid the phones stopped sending. Both were found by accident.

Generated pages cannot drift because they are rebuilt. Prose can, and prose is
where the operationally important numbers live: how long an id is held, how
long auto-recover waits, how many backups are kept. Those read as facts and get
planned against.

So each entry below ties one sentence to one constant. The check reads the
constant from the system repository (committed, not the working tree - see
`source_state`), reads the number out of the sentence, and compares them. Prose
spells numbers out, so "twelve" and 12.0 compare equal.

An entry whose pattern no longer matches is an ERROR, not a pass. If it were a
pass, rewording a sentence would silently switch its check off, which is the
failure mode this file exists to prevent. Re-point the entry instead.

Usage:
    python3 tools/check_constants.py [--repo ../TDStage] [--working-tree]
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

WORDS = {
    "half": 0.5, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "ninety": 90,
}

# (page, regex capturing ONE number or number-word, source file, constant)
# The regex must be specific enough that it cannot match a different sentence.
CHECKS = [
    ("reference/track.md", r"\*\*(\w+) sightings before publication",
     "WebConsole/track_emit.py", "CONFIRM_HITS"),
    ("reference/track.md", r"\*\*(\w+) seconds of reservation",
     "WebConsole/track_emit.py", "ID_RESERVE_SECONDS"),
    ("reference/track.md", r"not reused for (\w+) seconds",
     "WebConsole/track_emit.py", "ID_RESERVE_SECONDS"),
    ("reference/track.md", r"[Ww]ithin ([\d.]+) m of<br/>another performer",
     "WebConsole/track_emit.py", "CLUSTER_DISTANCE_M"),
    ("operations/failure.md", r"stayed back for\s*\n?(\w+) seconds",
     "WebConsole/server.py", "RECOVERY.graceSeconds"),
    ("operations/failure.md", r"at most once every (\w+) seconds",
     "WebConsole/server.py", "RECOVERY.cooldown"),
    ("operations/failure.md", r"keeps its last (\w+) saves",
     "WebConsole/server.py", "BACKUP_KEEP"),
    ("operations/failure.md", r"released after (\w+) seconds",
     "WebConsole/track_emit.py", "ID_RESERVE_SECONDS"),
    ("console/resilience.md", r"attempt every (\w+) seconds instead of forking",
     "WebConsole/yolo_seg.py", "BACKOFF_S[-1]"),
    ("console/resilience.md", r"given (\w+) seconds before it counts as failed",
     "WebConsole/yolo_seg.py", "START_TIMEOUT_S"),

    # Ports. A reader copies these into their own configuration, and a wrong
    # one fails silently on UDP: nothing arrives and nothing complains.
    ("console/running.md", r"\| `--http PORT` \| `(\d+)`",
     "WebConsole/server.py", "--http"),
    ("console/running.md", r"\| `--tdp4-port PORT` \| `(\d+)`",
     "WebConsole/server.py", "--tdp4-port"),
    ("console/running.md", r"\| `--sim-port PORT` \| `(\d+)`",
     "WebConsole/server.py", "--sim-port"),
    ("console/running.md", r"\| `--f1-port PORT` \| `(\d+)`",
     "WebConsole/server.py", "--f1-port"),
    ("console/running.md", r"\| `--f1-hz RATE` \| `([\d.]+)`",
     "WebConsole/server.py", "--f1-hz"),
    ("reference/track.md", r"to a host and port you give it \((\d+) by convention\)",
     "WebConsole/track_emit.py", "CONTROL_PORT"),
]


def source_state(repo: pathlib.Path, rel: str, working_tree=False):
    """The committed text of a source file, or the checkout with --working-tree.

    Same reasoning as the page generators: other sessions are editing this
    checkout, and a half-finished change must not be able to fail (or pass)
    a documentation check.
    """
    if working_tree:
        return (repo / rel).read_text(encoding="utf-8")
    return subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                          capture_output=True, text=True, check=True).stdout


def constant(src: str, name: str):
    """The value of a module constant, a dict entry (`DICT.key`), one element of
    a tuple constant (`NAME[-1]`), or an argparse default (`--flag`).

    Ports live in argparse defaults rather than in named constants, and a port
    is exactly the kind of number a reader copies into their own config without
    checking.
    """
    if name.startswith("--"):
        m = re.search(rf'add_argument\("{re.escape(name)}"[^)]*?default=([\d.]+)', src, re.S)
        return float(m.group(1)) if m else None
    if name.endswith("]"):
        base, idx = name[:-1].split("[")
        m = re.search(rf"^{re.escape(base)}\s*=\s*\((.*?)\)", src, re.M | re.S)
        if not m:
            return None
        parts = [p.strip() for p in m.group(1).split(",") if p.strip()]
        return float(parts[int(idx)])
    if "." in name:
        _, key = name.split(".", 1)
        m = re.search(rf'^\s*"{re.escape(key)}":\s*([\d.]+)', src, re.M)
        return float(m.group(1)) if m else None
    m = re.search(rf"^{re.escape(name)}\s*=\s*([\d.]+)", src, re.M)
    return float(m.group(1)) if m else None


def as_number(text: str):
    t = text.strip().lower()
    if t in WORDS:
        return float(WORDS[t])
    try:
        return float(t)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--working-tree", action="store_true",
                    help="read the checkout instead of HEAD")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        demo()
        return
    repo = pathlib.Path(a.repo).expanduser().resolve()
    if not (repo / "WebConsole").exists():
        print(f"system repo not found at {repo} - skipping")
        return

    sources, problems, checked = {}, [], 0
    for page, pattern, rel, name in CHECKS:
        text = (ROOT / page).read_text(encoding="utf-8")
        if rel not in sources:
            sources[rel] = source_state(repo, rel, a.working_tree)
        want = constant(sources[rel], name)
        if want is None:
            problems.append(f"{page}: constant {name} not found in {rel} "
                            f"(renamed or removed - re-point this check)")
            continue
        m = re.search(pattern, text)
        if not m:
            problems.append(f"{page}: no sentence matches /{pattern}/ "
                            f"(reworded? re-point it at the new wording)")
            continue
        got = as_number(m.group(1))
        checked += 1
        if got is None:
            problems.append(f"{page}: {m.group(1)!r} is not a number I can read")
        elif got != want:
            problems.append(f"{page}: says {m.group(1)} where {name} is "
                            f"{want:g} ({rel})")

    if problems:
        print("\n".join("  " + p for p in problems))
        print(f"\n{len(problems)} problem(s); {checked} of {len(CHECKS)} checks compared")
        sys.exit(1)
    print(f"{checked} prose numbers match their constants")


def demo():
    src = ('CONFIRM_HITS = 5\nID_RESERVE_SECONDS = 3.0\n'
           'BACKOFF_S = (0.5, 1.0, 15.0)\nRECOVERY = {\n    "cooldown": 30.0,\n}\n')
    assert constant(src, "CONFIRM_HITS") == 5
    assert constant(src, "ID_RESERVE_SECONDS") == 3.0
    assert constant(src, "BACKOFF_S[-1]") == 15.0
    assert constant(src, "RECOVERY.cooldown") == 30.0
    assert constant(src, "NOPE") is None
    assert as_number("twelve") == 12 and as_number("0.7") == 0.7
    assert as_number("half") == 0.5 and as_number("banana") is None
    print("self-check ok")


if __name__ == "__main__":
    main()
