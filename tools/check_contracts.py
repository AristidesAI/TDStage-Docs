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

# Two apps ship this surface and they are not identical. The rig deploys
# TDStage AR; the AVFoundation app is parked. Checking one of them is how
# `/tdlidar/ctl/imu/lock` stayed undocumented: it exists only in the AR app, so
# a check that read the parked app's source saw a table that matched perfectly
# (2026-11-10). The page must carry the UNION, and a verb missing from one app
# is named with the app it came from, so the page can say "TDStage AR only".
CONTRACTS = [
    {
        "what": "/ctl verbs",
        "page": "ios/ctl.md",
        "page_re": r"`/tdlidar/ctl/([a-z/]+)`",
        "sources": [
            ("system", "TDStage/Net/OSCReceiver.swift"),
            ("ar", "TDStageARKit/Net/OSCReceiver.swift"),
        ],
        "source_re": r'case "/tdlidar/ctl/([a-z/]+)"',
        "note": "both apps' own switch over incoming OSC addresses",
    },
    {
        # Same reasoning as the verbs, same near-miss: three keys that exist
        # only in the AR app (stage.capture, stage.confidenceGate,
        # stage.rec.imu) were on no page at all, and stage.capture is the one
        # that decides the grid, the confidence plane and whether a person
        # matte exists (2026-11-10). A key nobody wrote down is a control
        # nobody can use and a default nobody can question.
        "what": "phone settings keys",
        "pages": ["ios/settings.md", "ios/arkit.md", "ios/record.md",
                  "ios/playback.md", "ios/live.md", "ios/ctl.md"],
        "page_re": r"`(stage\.[A-Za-z.]+)`",
        "sources": [
            ("system", "TDStage/ShowSettings.swift"),
            ("ar", "TDStageARKit/ShowSettings.swift"),
        ],
        "source_re": r'"(stage\.[A-Za-z.]+)"',
        "note": "every key either app registers a default for",
    },
    {
        # The tox's parameters are the operator's whole surface, and the one
        # list that is NOT read from code: it comes from tox_params_live.md,
        # which is regenerated from the running tox's `customPars`. That file
        # was itself 30 tox versions stale on 2026-11-11 (generated from v63
        # while the tox was at v93), so the Stage Cut page's nine parameters
        # were in the tox, on the documentation page, and in no reference list
        # at all. Checking the page against it keeps both honest: regenerate
        # the list after adding a parameter and this check names what is not
        # written down yet.
        #
        # Header rows are section labels rather than controls, so they are
        # skipped on the source side; the page may still name one.
        #
        # One direction only. The page legitimately carries names the tox does
        # not have as parameters: the components of an XYZW tuple
        # (`Cropminx`), menu values (`icp`, `learned`), and the design
        # inventory's never-built parameters where the page says so. Enforcing
        # the other direction would report all of those every run, and a check
        # that cries wolf gets switched off.
        "what": "tox parameters",
        "page": "td/parameters.md",
        "page_re": r"`([A-Za-z]+)`(?=(?:, `[A-Za-z]+`)* \|)",
        "sources": [("system", "TD/newtox/tox_params_live.md")],
        "source_re": r"\n\| `([A-Za-z]+)` \| [^|]*\| (?!Header)",
        "note": "every non-header parameter in the live tox list",
        "one_way": True,
    },
]

# The ARKit app is its own repository, beside the system one.
AR_REPO_NAME = "TDStageARKit"


def ar_repo(repo: pathlib.Path) -> pathlib.Path:
    return repo.parent / AR_REPO_NAME


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

    ar = ar_repo(repo)
    have_ar = (ar / AR_REPO_NAME).exists()
    if not have_ar:
        print(f"note: {ar} is not here, so only the system repo's half is checked")

    problems = []
    for c in CONTRACTS:
        pages = c.get("pages") or [c["page"]]
        page = set()
        for pg in pages:
            page |= set(re.findall(c["page_re"], (ROOT / pg).read_text(encoding="utf-8")))
        page_name = pages[0] if len(pages) == 1 else f"{len(pages)} pages"
        union, read = set(), []
        for which, rel in c["sources"]:
            if which == "ar" and not have_ar:
                continue
            root = ar if which == "ar" else repo
            found = set(re.findall(c["source_re"], source_state(root, rel, a.working_tree)))
            if not found:
                problems.append(f'{c["what"]}: found none in {rel} '
                                f"- the code's shape changed, re-point this check")
                continue
            read.append((rel, found))
            union |= found
        if not read:
            continue
        for v in sorted(union - page):
            where = ", ".join(rel for rel, f in read if v in f)
            hint = ""
            if all(rel.startswith(AR_REPO_NAME) for rel, f in read if v in f):
                # The ARKit app is a separate repository that other sessions
                # edit while this check runs. A verb or key that appears there
                # and nowhere else is usually one that has just landed, and
                # occasionally one that is about to be amended away.
                hint = (" (that repository is edited outside this one: if the"
                        " addition is real, document it; if a peer is mid-work,"
                        " re-run)")
            problems.append(f'{c["what"]}: `{v}` is in {where} '
                            f'and not on {page_name}{hint}')
        extras = set() if c.get("one_way") else page - union
        for v in sorted(extras):
            problems.append(f'{c["what"]}: `{v}` is on {page_name} '
                            f'and in neither app')
        if not (union - page or extras):
            only = {rel: f - set().union(*(g for r, g in read if r != rel))
                    for rel, f in read} if len(read) > 1 else {}
            extra = "; ".join(f"{len(v)} only in {rel.split('/')[0]}"
                              for rel, v in only.items() if v)
            print(f'{c["what"]}: {len(union)} match ({c["note"]})'
                  + (f" - {extra}" if extra else ""))

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
    # the union rule: a verb in only ONE of the two apps still has to be on the
    # page, which is the case that went unnoticed while one app was read
    ar_only = 'case "/tdlidar/ctl/imu/lock": return .imuLock'
    union = set(re.findall(src_re, src)) | set(re.findall(src_re, ar_only))
    assert "imu/lock" in union and "imu/lock" not in set(re.findall(src_re, src))
    page_both = page + "\n| `/tdlidar/ctl/stop` | ... |\n| `/tdlidar/ctl/imu/lock` | ... |"
    assert union - set(re.findall(page_re, page_both)) == set()
    # the tox-parameter contract: grouped cells, header rows, one direction
    tox_src = ("\n| `Trimx` | Cloud Offset X (m) | Float | 0.0 |  |"
               "\n| `Hdrwall` | Backdrop wall | Header | |  |"
               "\n| `Wallcut` | Backdrop Wall Cut | Toggle | False |  |")
    tox_rx = r"\n\| `([A-Za-z]+)` \| [^|]*\| (?!Header)"
    assert set(re.findall(tox_rx, tox_src)) == {"Trimx", "Wallcut"}, "header row not skipped"
    pg_rx = r"`([A-Za-z]+)`(?=(?:, `[A-Za-z]+`)* \|)"
    pg = "| `Trimx`, `Trimy`, `Trimz` | Cloud Offset X/Y/Z (m) |\n| `Cropminx` | a tuple component |"
    names = set(re.findall(pg_rx, pg))
    assert {"Trimx", "Trimy", "Trimz"} <= names, "grouped cell lost a name"
    assert set(re.findall(tox_rx, tox_src)) - names == {"Wallcut"}
    # and the page's own extras are NOT reported, which is why this one is one-way
    assert "Cropminx" in names - set(re.findall(tox_rx, tox_src))
    print("self-check ok")


if __name__ == "__main__":
    main()
