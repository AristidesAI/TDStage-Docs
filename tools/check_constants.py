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
    ("reference/track.md", r"average only the points within (\d+) cm of it",
     "WebConsole/track_emit.py", "CORE_R_CM"),
    ("reference/track.md", r"for up to ([a-z]+)\nseconds, so that when they separate",
     "WebConsole/track_emit.py", "RIDE_MAX_S"),
    # the hysteresis: a receiver acts on these two, so they must not drift
    ("reference/track.md", r"It \*\*enters\*\* at ([\d.]+) m",
     "WebConsole/track_emit.py", "CLUSTER_DISTANCE_M"),
    ("reference/track.md", r"leaves\*\* only after ([\d.]+) m of separation",
     "WebConsole/track_emit.py", "CLUSTER_RELEASE_M"),
    ("reference/track.md", r"separation held for\n([\d.]+) s",
     "WebConsole/track_emit.py", "CLUSTER_HOLD_S"),
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

    ("console/guide.md", r"\*\*That cap is now (\d+), which means",
     "TDStage/ShowSettings.swift", "stage.thermalSeriousFPS"),

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
    ("console/running.md", r"the setting `f1\.rateHz` holds the rate instead, (\d+) Hz",
     "WebConsole/settings.py", "_n.f1.rateHz"),
    ("reference/track.md", r"to a host and port you give it \((\d+) by convention\)",
     "WebConsole/track_emit.py", "CONTROL_PORT"),

    # The field stream: a receiver sizes its grid from these.
    ("reference/field.md", r"\*\*Voxels\*\* are (\d+) cm",
     "WebConsole/f1_field.py", "VOXEL_CM"),
    ("reference/field.md", r"falls below (\d+) of 255",
     "WebConsole/f1_field.py", "DROP_W"),
    ("reference/field.md", r"covers at least (\d+) cells",
     "WebConsole/f1_field.py", "PRES_MIN_CELLS"),
    ("reference/field.md", r"no wider than ([\d.]+) m in radius",
     "WebConsole/f1_field.py", "PRES_R_MAX"),
    ("reference/field.md", r"\*\*The source id\*\* is (\d+), always",
     "WebConsole/f1_field.py", "SOURCE_ID"),
    ("reference/field.md", r"The default rate is (\d+) Hz",
     "WebConsole/settings.py", "_n.f1.rateHz"),
    ("reference/field.md", r"listens on TCP port (\d+) \(`--f1-port`\)",
     "WebConsole/server.py", "--f1-port"),
    ("console/ui.md", r"A disagreement over (\d+) cm names the phone",
     "WebConsole/calib_check.py", "WARN_M_CM"),
    # The ghost-after-merge reach (#68). A receiver counting heads acts on
    # these, so they are pinned the day the paragraph goes up.
    ("reference/track.md", r"reach starts at ([\d.]+) m and grows",
     "WebConsole/track_emit.py", "GATE_M"),
    ("reference/track.md", r"grows by\n([\d.]+) m for every second of coasting",
     "WebConsole/track_emit.py", "REACQ_GROW_MPS"),
    ("reference/track.md", r"to a limit of ([\d.]+) m",
     "WebConsole/track_emit.py", "REACQ_MAX_M"),
    ("reference/track.md", r"ride lasts at most ([a-z]+) seconds",
     "WebConsole/track_emit.py", "RIDE_MAX_S"),
    # The hand contract, published 2026-11-11. A receiver times a gesture latch
    # against the hold ladder, so every number in it is pinned: a change in
    # hands.py that nobody carries to the page would mis-time somebody's show.
    ("reference/track.md", r"up to ([\d.]+) s \| the position, with its measured",
     "WebConsole/hands.py", "LIVE_S"),
    ("reference/track.md", r"waiting out the ([\d.]+) s", "WebConsole/hands.py",
     "self.hold_s"),
    ("reference/track.md", r"saw that wrist within ([\d.]+) s of each",
     "WebConsole/hands.py", "FUSE_AGE_S"),
    ("reference/track.md", r"more than\n([\d.]+) m from the median of them",
     "WebConsole/hands.py", "FUSE_M"),
    ("reference/track.md", r"beyond ([\d.]+) m \(scaled by the interval",
     "WebConsole/hands.py", "self.outlier_m"),
    # the detection fusion radius and the settle gate, same day, same reason
    ("reference/track.md", r"within ([\d.]+) m in plan is folded into it",
     "WebConsole/track_emit.py", "OBS_FUSE_M"),
    ("console/settings.md", r"`settleWindow`, (\w+) seconds by default",
     "WebConsole/track_emit.py", "SETTLE_WINDOW_S"),
    ("console/settings.md", r"`settleGrowth`, ([\d.]+), is how much",
     "WebConsole/track_emit.py", "SETTLE_GROWTH"),
    ("reference/track.md", r"The hold is (\d+) s, or\nlonger",
     "WebConsole/track_emit.py", "REG_SETTLE_S"),
    # Body points, pinned from the day the pages went up. The two radii are the
    # easiest pair on the site to confuse: 0.25 m drops a view that is lying
    # about a joint, 0.12 m decides which depth points become the published
    # position, and only the first is a setting.
    ("reference/design.md", r"lies more than ([\d.]+) m in front of the triangulated",
     "WebConsole/body_points.py", "OUTLIER_M"),
    ("reference/design.md", r"within ([\d.]+) m of the<br/>triangulated joint",
     "WebConsole/body_points.py", "CONFIRM_M"),
    ("reference/design.md", r"agrees with\nwithin (\d+) pixels of reprojection",
     "WebConsole/body_points.py", "REPROJ_PX"),
    ("reference/design.md", r"rays closer than (\d+) degrees apart cannot be the pair",
     "WebConsole/body_points.py", "MIN_ANGLE_DEG"),
    ("reference/design.md", r"performer in plan within ([\d.]+) m",
     "WebConsole/body_points.py", "MATCH_M"),
    ("reference/track.md", r"carrying a person within ([\d.]+) m of them",
     "WebConsole/body_points.py", "MATCH_M"),
    ("reference/track.md", r"no phone frame younger than\n> ([\d.]+) s", "WebConsole/body_points.py",
     "MAX_AGE_S"),
    ("console/settings.md", r"counts ([\d.]+)x in\nevery depth median",
     "WebConsole/body_points.py", "FAR_W"),
    ("console/settings.md", r"with no body for ([\d.]+) s restarts their smoothing",
     "WebConsole/body_points.py", "SMOOTH_RESET_S"),
]


def source_state(repo: pathlib.Path, rel: str, working_tree=False):
    """The committed text of a source file, or the checkout with --working-tree.

    Same reasoning as the page generators: other sessions are editing this
    checkout, and a half-finished change must not be able to fail (or pass)
    a documentation check.
    """
    if working_tree:
        path = repo / rel
        return path.read_text(encoding="utf-8") if path.exists() else None
    r = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                       capture_output=True, text=True)
    # A page may pin a constant in a file that is not on trunk yet: the pins for
    # a feature land in the same commit as the page describing it, and the
    # feature's own file arrives with its branch. That is a thing to report, not
    # a traceback - the check used to die here with a CalledProcessError.
    return r.stdout if r.returncode == 0 else None


def constant(src: str, name: str):
    """The value of a module constant, a dict entry (`DICT.key`), a settings
    schema default (`_n.key`), an instance default (`self.attr`), one element of a tuple constant (`NAME[-1]`), or an
    argparse default (`--flag`).

    Ports live in argparse defaults rather than in named constants, and a port
    is exactly the kind of number a reader copies into their own config without
    checking.
    """
    if name.startswith("stage."):
        m = re.search(rf'"{re.escape(name)}"\s*:\s*([\d.]+)', src)
        return float(m.group(1)) if m else None
    if name.endswith("_CM"):
        v = constant(src, name[:-3])
        return None if v is None else round(v * 100)
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
    if name.startswith("_n."):
        # A settings-schema default, group-qualified: `_n.f1.rateHz` reads
        # `"rateHz": _n("F1 rate", "float", 15.0, ...)` inside `"f1": {`.
        #
        # The group is not optional, and the reason is the bug it caused here:
        # `rateHz` exists twice in the schema, vision's observer rate (30) and
        # f1's field rate (15), and an unqualified search took the first.
        #
        # These pins matter when a CLI flag stops carrying a number. --f1-hz
        # became `default=None` on sys/integ-c, with the schema holding 15 and
        # the flag only overriding it, which would have failed two pins the day
        # it landed.
        _, grp, key = name.split(".", 2)
        g = re.search(rf'^\s*"{re.escape(grp)}":\s*\{{', src, re.M)
        if not g:
            return None
        rest = src[g.end():]
        nxt = re.search(r'^\s{0,8}"[a-zA-Z0-9_]+":\s*\{', rest, re.M)
        block = rest[:nxt.start()] if nxt else rest
        m = re.search(rf'"{re.escape(key)}":\s*_n\([^,]*,\s*"[a-z]+",\s*([\d.]+)', block)
        return float(m.group(1)) if m else None
    if name.startswith("self."):
        # A default that lives on an instance rather than at module level:
        # hands.py keeps holdS and outlierM as `self.hold_s = 0.2`, set once in
        # __init__ and overwritten from the settings. settings.py would be the
        # other place to read them, and it has two different `holdS` keys in two
        # groups, so the class's own default is the unambiguous one.
        attr = name.split(".", 1)[1]
        m = re.search(rf"^\s*self\.{re.escape(attr)}\s*=\s*([\d.]+)", src, re.M)
        return float(m.group(1)) if m else None
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
        if sources[rel] is None:
            problems.append(f"{page}: {rel} is not in the repository's trunk, so "
                            f"{name} cannot be compared - if the feature has not "
                            f"landed, the page and this pin belong on the same "
                            f"branch as it")
            continue
        want = constant(sources[rel], name)
        if want is None:
            problems.append(f"{page}: constant {name} not found in {rel} "
                            f"(renamed, removed, or a key that has not landed "
                            f"yet - re-point this check, or hold it on the "
                            f"feature's own branch)")
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
