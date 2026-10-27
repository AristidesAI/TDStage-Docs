#!/usr/bin/env python3
"""Run every check, report once, exit non-zero if any failed.

Five checks and two generators, each with its own command, is five commands
nobody runs. This is the one to run before pushing, and the one CI runs.

Checks that need the system repository say so and skip when it is absent,
rather than failing: this repository is public and clones on its own, so a
checkout without TDStage beside it must still be able to prove its links and
diagrams are sound.

Usage:
    python3 tools/check_all.py [--repo ../TDStage]
"""
import argparse
import pathlib
import subprocess
import sys

TOOLS = pathlib.Path(__file__).resolve().parent

# (script, needs the system repo, what it proves)
CHECKS = [
    ("check_links.py", False, "every internal link, image and heading anchor resolves"),
    ("check_diagrams.py", False, "no diagram hits a known silent-failure pattern"),
    ("check_constants.py", True, "numbers in prose match the constants they came from"),
    ("check_contracts.py", True, "the /ctl verb table matches the app"),
    ("check_tox_version.py", True, "the docs are current with the saved project"),
    ("gen_troubleshooting.py --check", True, "the generated troubleshooting page is current"),
    ("gen_api.py --check", True, "the generated API page is current"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        demo()
        return

    repo = pathlib.Path(a.repo).expanduser().resolve()
    have_repo = (repo / "WebConsole").exists()
    if not have_repo:
        print(f"note: {repo} is not here, so the checks that read the code are skipped\n")

    failed, ran, skipped = [], 0, 0
    for script, needs_repo, proves in CHECKS:
        name = script.split()[0]
        if needs_repo and not have_repo:
            skipped += 1
            continue
        cmd = [sys.executable, *str(TOOLS / script).split()]
        if needs_repo:
            cmd += ["--repo", str(repo)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ran += 1
        mark = "ok  " if r.returncode == 0 else "FAIL"
        print(f"{mark} {name:28} {proves}")
        if r.returncode != 0:
            failed.append(name)
            for line in (r.stdout + r.stderr).strip().splitlines():
                print(f"       {line}")

    print()
    if failed:
        print(f"{len(failed)} of {ran} failed: {', '.join(failed)}")
        sys.exit(1)
    tail = f", {skipped} skipped (no system repo)" if skipped else ""
    print(f"all {ran} checks pass{tail}")


def demo():
    missing = [c[0].split()[0] for c in CHECKS if not (TOOLS / c[0].split()[0]).exists()]
    assert not missing, f"listed but not on disk: {missing}"
    on_disk = {p.name for p in TOOLS.glob("check_*.py")} - {"check_all.py"}
    listed = {c[0].split()[0] for c in CHECKS}
    # a new check that nobody wired in here would never run
    assert on_disk <= listed, f"not wired into check_all: {sorted(on_disk - listed)}"
    print("self-check ok")


if __name__ == "__main__":
    main()
