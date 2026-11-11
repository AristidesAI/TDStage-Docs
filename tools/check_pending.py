#!/usr/bin/env python3
"""Check what the site says is still coming.

Several pages describe behaviour that is on a branch and not yet on `main`,
and name the branch. Those sentences are true for a few days and then quietly
become wrong in the worst direction: a reader is told to expect today's
behaviour when the fix has landed, or is promised a fix that was dropped.

Nothing about that is visible by reading the page, so it is checked:

* a branch the site names must exist in one of the two repositories - a
  renamed or deleted branch means the sentence is describing work that no
  longer has that name;
* a branch the site names must NOT be merged into that repository's `main` -
  the site only names a branch while its work is pending, so a merged one is a
  page to rewrite.

Both repositories are searched, because the phone pages' branches live in the
ARKit one: `fix/rec-minutes` is in TDStageARKit and nowhere else, and a check
that read only the system repository called it a typo.

Dated promises ("lands 12 November 2026") are listed rather than failed, with
the ones already due called out, because a date slipping is normal and only a
person can say whether the sentence needs rewording or the date moving.

Usage:
    python3 tools/check_pending.py [--repo ../TDStage] [--today YYYY-MM-DD]
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# the branch prefixes this project actually uses, so a backticked path like
# `logs/track-x.jsonl` is not read as a branch
PREFIXES = ("sys", "fix", "fix2", "fix3", "feat", "test", "perf", "ci", "docs",
            "f1", "face", "stroud", "night", "rt", "tools", "ar")
BRANCH_RX = re.compile(r"`((?:" + "|".join(PREFIXES) + r")/[a-z0-9][a-z0-9-]*)`")
# A dated promise is a DATE on a line that is also talking about something not
# here yet. Matching the date alone would pick up every "captured on" and
# "measured on"; matching a fixed phrase missed most of them, because the
# wording varies ("lands", "landing", "not on main until", "expected on",
# "fixed from", "rides in"). So: a pending word anywhere on the line, and the
# dates on it. A date written without its year is read as this year.
PENDING_RX = re.compile(r"\b(?:lands?|landing|expected|not yet|rides in|"
                        r"fixed from|still to come)\b|not on `?main`?", re.I)
DATE_RX = re.compile(r"\b(\d{1,2} (?:January|February|March|April|May|June|July|"
                     r"August|September|October|November|December)(?: 20\d\d)?)\b")
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pages():
    return sorted(p for p in ROOT.glob("**/*.md")
                  if "_site" not in p.parts and p.name != "README.md")


AR_REPO_NAME = "TDStageARKit"
# The two repositories do not agree on the name of the trunk: the system one is
# on `main`, the ARKit one on `master`. Asking the wrong one silently answers
# "not merged", which is the answer that makes this check pass.
#
# The question is deliberately "is it on TRUNK", not "is it merged anywhere".
# Feature branches are merged into integration branches days before they reach
# trunk - fix/track-stale-devcount went into sys/integ-c two days before its
# landing - and the site describes what is on trunk. Asking the looser question
# would turn a page red while its warning was still the truth.
#
# Both the local trunk and the pushed one count, so a landing shows up here
# from the push rather than waiting for this checkout to pull it.
TRUNKS = ("refs/heads/main", "refs/remotes/origin/main",
          "refs/heads/master", "refs/remotes/origin/master")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--today")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        demo()
        return
    repo = (ROOT / a.repo).resolve() if not pathlib.Path(a.repo).is_absolute() \
        else pathlib.Path(a.repo)
    if not (repo / ".git").exists():
        print(f"system repo not found at {repo} - skipping")
        return
    today = (datetime.date.fromisoformat(a.today) if a.today
             else datetime.date.today())

    repos = [repo]
    ar = repo.parent / AR_REPO_NAME
    if (ar / ".git").exists():
        repos.append(ar)
    else:
        print(f"note: {ar} is not here, so a branch that lives only there "
              f"cannot be found")

    cited, dated = {}, []
    for p in pages():
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for b in BRANCH_RX.findall(line):
                cited.setdefault(b, []).append(f"{rel}:{i}")
            if PENDING_RX.search(line):
                for d in DATE_RX.findall(line):
                    dated.append((d, f"{rel}:{i}"))

    problems = []
    for b, where in sorted(cited.items()):
        home = next((r for r in repos
                     if git(r, "rev-parse", "--verify", f"refs/heads/{b}").returncode == 0),
                    None)
        if home is None:
            problems.append(f"`{b}` is named on {', '.join(where)} and is not a "
                            f"branch in "
                            + " or ".join(r.name for r in repos)
                            + " any more - renamed, deleted, or a typo")
            continue
        trunks = [n for n in TRUNKS
                  if git(home, "rev-parse", "--verify", n).returncode == 0]
        if not trunks:
            problems.append(f"{home.name} has no trunk among "
                            + ", ".join(TRUNKS)
                            + f", so whether `{b}` has landed cannot be answered")
            continue
        landed = [n for n in trunks
                  if git(home, "merge-base", "--is-ancestor", b, n).returncode == 0]
        if landed:
            problems.append(f"`{b}` is on {home.name}'s "
                            + " and ".join(n.split("/")[-2] + "/" + n.split("/")[-1]
                                           if "remotes" in n else n.split("/")[-1]
                                           for n in landed)
                            + f", and {', '.join(where)} still describes its work "
                            f"as coming - rewrite those as the behaviour, and "
                            f"drop the branch name")
        else:
            print(f"`{b}`: not on {home.name}'s trunk yet "
                  f"({len(trunks)} ref(s) checked), {len(where)} place(s) say so")

    if dated:
        due = [(d, w) for d, w in dated if _parse(d, today.year) <= today]
        print(f"{len(dated)} dated promise(s), {len(due)} already due:")
        for d, w in sorted(due):
            print(f"  {w}  {d}")

    if problems:
        print("\n".join("  " + p for p in problems))
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1)


def _parse(s, year=None):
    parts = s.split()
    d, m = parts[0], parts[1]
    y = int(parts[2]) if len(parts) > 2 else (year or datetime.date.today().year)
    return datetime.date(y, MONTHS.index(m.capitalize()) + 1, int(d))


def demo():
    assert BRANCH_RX.findall("on `sys/integ-c`, landing") == ["sys/integ-c"]
    # a backticked path is not a branch
    assert BRANCH_RX.findall("`logs/track-x.jsonl`") == []
    assert BRANCH_RX.findall("`TD/newtox/tdp4_sim.py`") == []
    def dates(line):
        return DATE_RX.findall(line) if PENDING_RX.search(line) else []
    # the wordings actually on the site, which a single fixed phrase missed
    assert dates("**Lands 12 November 2026** as `sys/integ-c`") == ["12 November 2026"]
    assert dates("**Fixed from 12 November 2026** by refusing") == ["12 November 2026"]
    assert dates("not on `main` until 12 November 2026.** It is on the branch") \
        == ["12 November 2026"]
    assert dates("A stamped build is expected on 12 November.") == ["12 November"]
    assert dates("**From the 12 November landing an old roster is corrected**") \
        == ["12 November"]
    # a date with nothing pending about it is not a promise, and "until" or
    # "before" on their own are usually history, not a promise: all three of
    # these were reported as due promises before the trigger list was narrowed
    assert dates("They were captured on 14 October 2026 at a narrow width") == []
    assert dates("used 0.15 m until 10 November, which left 300 points") == []
    assert dates("rather than the 58 it used before 10 November 2026") == []
    assert dates("Two honest caveats, both as of 9 November 2026: it") == []
    assert DATE_RX.findall("captured on 2026-10-27 at a narrow width") == []
    assert _parse("12 November 2026") == datetime.date(2026, 11, 12)
    assert _parse("12 November", 2026) == datetime.date(2026, 11, 12)
    # trunk refs only, and the remote one among them: a branch merged into an
    # integration branch has NOT landed, and a landing that is pushed but not
    # pulled here HAS
    assert "refs/remotes/origin/main" in TRUNKS
    assert not any("integ" in n for n in TRUNKS)
    print("self-check ok")


if __name__ == "__main__":
    main()
