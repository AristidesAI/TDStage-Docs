#!/usr/bin/env python3
"""Check the lists that are contracts: every item in the code, every item on the page.

Some tables are not prose, they are a set. The `/ctl` verbs an app accepts are
one: an integrator reads that table and sends what it says. A verb added to the
app and not to the page is a capability nobody knows about; a verb on the page
and not in the app is an instruction that silently does nothing.

Set equality is cheap to check and the whole value is in checking it, so this
runs rather than being remembered.

**Only lists the code states literally are checkable here.** The telemetry
paths look like a candidate and are not: they are built by interpolation
(`osc.send("\\(ns)/calib/pose", ...)`), so matching on the literal would report
drift that is not there. A check that cries wolf gets switched off. If a list
cannot be read reliably, it does not belong in this file.

Usage:
    python3 tools/check_contracts.py [--repo ../TDStage] [--working-tree]
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

CONTRACTS = [
    {
        "what": "/ctl verbs",
        "page": "ios/ctl.md",
        "page_re": r"`/tdlidar/ctl/([a-z/]+)`",
        "source": "TDStage/Net/OSCReceiver.swift",
        "source_re": r'case "/tdlidar/ctl/([a-z/]+)"',
        "note": "the app's own switch over incoming OSC addresses",
    },
]


def source_state(repo: pathlib.Path, rel: str, working_tree=False):
    if working_tree:
        return (repo / rel).read_text(encoding="utf-8")
    return subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                          capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--working-tree", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        demo()
        return
    repo = pathlib.Path(a.repo).expanduser().resolve()
    if not (repo / "TDStage").exists():
        print(f"system repo not found at {repo} - skipping")
        return

    problems = []
    for c in CONTRACTS:
        page = set(re.findall(c["page_re"], (ROOT / c["page"]).read_text(encoding="utf-8")))
        code = set(re.findall(c["source_re"], source_state(repo, c["source"], a.working_tree)))
        if not code:
            problems.append(f'{c["what"]}: found none in {c["source"]} '
                            f"- the code's shape changed, re-point this check")
            continue
        for v in sorted(code - page):
            problems.append(f'{c["what"]}: `{v}` is in {c["source"]} '
                            f'and not on {c["page"]}')
        for v in sorted(page - code):
            problems.append(f'{c["what"]}: `{v}` is on {c["page"]} '
                            f'and not in {c["source"]}')
        if not (code - page or page - code):
            print(f'{c["what"]}: {len(code)} match ({c["note"]})')

    if problems:
        print("\n".join("  " + p for p in problems))
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1)


def demo():
    page_re, src_re = r"`/tdlidar/ctl/([a-z/]+)`", r'case "/tdlidar/ctl/([a-z/]+)"'
    page = "| `/tdlidar/ctl/start` | ... |\n| `/tdlidar/ctl/rec/play` | ... |"
    src = 'case "/tdlidar/ctl/start": return .start\ncase "/tdlidar/ctl/stop": return .stop'
    assert set(re.findall(page_re, page)) == {"start", "rec/play"}
    assert set(re.findall(src_re, src)) == {"start", "stop"}
    # the asymmetry the check reports, both ways round
    assert set(re.findall(src_re, src)) - set(re.findall(page_re, page)) == {"stop"}
    assert set(re.findall(page_re, page)) - set(re.findall(src_re, src)) == {"rec/play"}
    print("self-check ok")


if __name__ == "__main__":
    main()
