#!/usr/bin/env python3
"""Fail if the docs have fallen behind the TouchDesigner project's version.

The project is saved as numbered snapshots, and several pages quote a number:
the drift-check example, the directory listing, "the working copy was
byte-identical to". Those numbers go stale the moment somebody saves a new
version, and a stale one is worse than no number, because it is also attached
to parameter values that may since have changed. It happened: the docs sat on
v78 while the project reached v80, and in between a floor offset of -0.78 m was
zeroed and the pose source was moved off `manual`. A reader following the page
would have set up a stage 78 cm off the floor.

The rule is one line: the highest version the docs mention must be the highest
version on disk. That tolerates historical mentions of older numbers, which are
legitimate, while catching the whole site lagging behind.

Needs the TDStage repository beside this one. Skips cleanly when it is absent,
so a build on a machine with only the docs still passes.

Usage: python3 tools/check_tox_version.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TD = ROOT.parent / "TDStage" / "TD"
VER = re.compile(r"TDStageConductor_v0*(\d+)\.tox|\bv0*(\d+)\b")


def versions_on_disk(td=TD):
    return sorted(int(m.group(1))
                  for f in td.glob("TDStageConductor_v*.tox")
                  if (m := re.search(r"_v0*(\d+)\.tox$", f.name)))


def versions_in_docs(root=ROOT):
    found = {}
    for page in root.rglob("*.md"):
        if ".git" in page.parts:
            continue
        for line_no, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            for m in VER.finditer(line):
                n = int(m.group(1) or m.group(2))
                # v1-v9 as bare words are almost always something else
                # (a spec revision, an API version), so only trust _vNN.tox
                # and two-digit numbers.
                if m.group(1) or n >= 10:
                    found.setdefault(n, []).append(f"{page.relative_to(root)}:{line_no}")
    return found


def main():
    disk = versions_on_disk()
    if not disk:
        print(f"TDStage project not found beside the docs ({TD}) - skipping")
        return
    latest, docs = disk[-1], versions_in_docs()
    if not docs:
        print(f"no version mentioned anywhere in the docs; project is at v{latest}")
        sys.exit(1)
    ahead = [n for n in docs if n > latest]
    if ahead:
        for n in sorted(ahead):
            print(f"  docs claim v{n}, which is not on disk: {', '.join(docs[n][:3])}")
        sys.exit(1)
    if max(docs) < latest:
        print(f"  docs' newest mention is v{max(docs)}, project is at v{latest}")
        print(f"  pages quoting v{max(docs)}: {', '.join(docs[max(docs)])}")
        print("\nCheck the parameter values on td/parameters.md too: a new version"
              "\nusually means some saved default moved.")
        sys.exit(1)
    print(f"docs are current with v{latest} "
          f"({len(docs[latest])} mention(s), {len(docs)} version(s) referenced)")


def demo():
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "TDStageConductor_v09.tox").touch()
    (d / "TDStageConductor_v80.tox").touch()
    assert versions_on_disk(d) == [9, 80], versions_on_disk(d)
    docs = d / "docs"
    (docs / "td").mkdir(parents=True)
    (docs / "td" / "a.md").write_text(
        "see TDStageConductor_v80.tox and the older v77\nREV6 and v3 are not tox versions\n")
    got = versions_in_docs(docs)
    assert set(got) == {80, 77}, got
    print("self-check ok")


if __name__ == "__main__":
    demo() if "--selftest" in sys.argv else main()
