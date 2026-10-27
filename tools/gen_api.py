#!/usr/bin/env python3
"""Build the console HTTP API page from the console's own routing code.

Which routes exist, and whether each is GET or POST, is decided by which
handler the `path ==` test sits in. Copying that into prose by hand produces a
list that is wrong the next time someone adds a route, and GET versus POST on
this API has already caused confusion in practice: several routes that read
like queries are POST only, so a browser or a naive curl gets a 404 and it
reads as "the endpoint does not exist".

So the table is generated. Descriptions are hand-written, because the code
cannot say what a route is FOR, but a route with no description still appears
in the table rather than being quietly left out.

Usage:
    python3 tools/gen_api.py [--repo ../TDStage] [--check]
"""
import argparse
import pathlib
import re
import sys


WORKING_TREE = False          # --working-tree flips this


def source_state(repo: pathlib.Path, rel: str):
    """(text, note) for a source file, reading the COMMITTED version by default.

    These generators run against a working tree that other sessions are editing.
    Reading the checkout means a half-finished change can be published as
    documentation before it is even committed, and `--check` then reports the
    page stale against code that may still be rewritten or dropped. It happened
    on 2026-10-27: a regeneration picked up another session's uncommitted
    rewrite of the fix hints.

    So the default is `git show HEAD:<rel>`, which is a real, named state that
    can be pointed at. `--working-tree` opts into the checkout, and says so in
    the page's own provenance line.
    """
    import subprocess
    if WORKING_TREE:
        return (repo / rel).read_text(encoding="utf-8"), "working tree (--working-tree)"
    try:
        out = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                             capture_output=True, text=True, check=True).stdout
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return out, f"committed {sha}"
    except Exception as e:
        return (repo / rel).read_text(encoding="utf-8"), f"working tree (no git: {e})"

OUT = pathlib.Path(__file__).resolve().parent.parent / "console" / "api.md"

# What each route is for. Anything missing here is still listed, marked so it
# is obvious the description is missing rather than the route.
WHAT = {
    "/": "The console's web interface.",
    "/healthz": "Liveness check. Returns without touching any device.",
    "/api/state": "The whole console state: roster, markers, scene, link status.",
    "/api/live": "Live summary: which ingest paths are receiving and at what rate.",
    "/api/cloud": "The point cloud, as binary, long-polled. Query: `seq`, `max`, `labels=1`, `fmt=i16`. Off the local network this is capped to 5 Hz and 20,000 points.",
    "/api/events": "Server-sent event stream the interface subscribes to.",
    "/api/rgb": "Which devices have a camera image, and how old each one is.",
    "/api/settings": "Read the tunables (GET) or change them (POST).",
    "/api/hands": "Read hand detections (GET) or change the detector's settings (POST).",
    "/api/hands/diag": "Why hand detection is or is not producing results, as checks rather than counters. This is the per-problem list. Read-only.",
    "/api/vision": "State of the vision services.",
    "/api/vision/restart": "Restart a vision service. Clears counters; it does NOT reload code.",
    "/api/rig": "The facts that span phone, console, relay and TouchDesigner in one place: relay status, cable link, this machine's address, the listener and hands. A facts dump, not a problem list.",
    "/api/stalls": "Recorded stalls, for diagnosing a stuttering stream.",
    "/api/track": "Read or configure the tracking output. Body: `enabled`, `host`, `port`.",
    "/api/track/record": "Start or stop recording the tracking output. Body: `{\"on\": true}`. Writes `logs/track-<timestamp>.jsonl`.",
    "/api/track/trace": "Per-frame trace of the tracking output, for offline analysis.",
    "/api/person": "Person segmentation mode.",
    "/api/person/debug": "Segmentation internals.",
    "/api/ctl": "Send a control message to one phone or all of them.",
    "/api/profile": "A phone's stored settings. The phone fetches this itself at boot.",
    "/api/profile/": "Same, addressed per device as `/api/profile/<id>`.",
    "/api/profile/push": "Push a stored profile to a phone.",
    "/api/profile/key": "Change one key in a stored profile.",
    "/api/device": "Change a device's roster entry.",
    "/api/devices": "The device roster.",
    "/api/count": "Set how many devices the roster holds.",
    "/api/markers": "Marker definitions.",
    "/api/markers/size": "Set the printed marker size. Must match the markers you actually printed.",
    "/api/venue/layout": "Load a stage layout. Sets positions, labels, and one rig-wide marker size derived from the smallest sheet in the layout. It writes the roster; it does NOT push the size to the phones, so Apply to all phones is still needed.",
    "/api/align/rig": "Solve the rig alignment.",
    "/api/range": "Working range.",
    "/api/scene": "Scene settings.",
    "/api/td": "Link to TouchDesigner.",
    "/api/listen": "Change the telemetry listening port.",
    "/api/telemetry/retarget": "Tell phones to send health here instead of to TouchDesigner.",
    "/api/usb/link": "Find a phone attached by cable. POST only.",
    "/api/fanout": "The legacy relay. Not the show path.",
    "/api/sim": "Start or stop simulated phones.",
    "/api/ndi": "Video output settings.",
    "/api/recover": "Run a recovery step on a phone.",
    "/api/recovery": "Recovery policy.",
    "/api/autofix": "Run the automatic fixer against a device.",
    "/api/undo": "Undo the last roster change.",
    "/api/redo": "Redo it.",
    "/api/edit": "Edit roster fields in bulk.",
    "/api/dev/shot": "Development screenshot helper.",
    "/api/diag/age": "Frame ages per device.",
    "/api/diag/limbs": "Limb diagnostics.",
    "/api/diag/person": "Person diagnostics.",
    "/api/diag/profile": "Profile diagnostics.",
}

HEADER = """---
title: HTTP API
parent: Console
nav_order: 6
---

# HTTP API

Every route the console serves, and which verb it answers.

This page is generated from the console's routing code, so it cannot drift
from the software. Do not edit it by hand. Regenerate it with:

```
python3 tools/gen_api.py
```

## Read this before you call anything

**Check the verb.** Several routes that read like queries are POST only. A
GET to one of those returns 404, which looks exactly like a route that does
not exist. This has already wasted time at least once.

**Three paths answer both verbs**, with different meanings: GET reads,
POST changes. They are `/api/settings`, `/api/hands` and `/api/profile`.

**There is no PUT and no DELETE.** Every POST takes a JSON body and answers
with JSON.

**Two surfaces are not HTTP at all.** The client field stream is a WebSocket
on its own port, 9001 by default. The tracking output is OSC over UDP on port
7000, configured through `POST /api/track`.

"""

FOOTER = """
## Cautions

**Restarting a vision service does not reload code.** The restart controls
clear counters and bring a service back up. A code change needs the console
itself restarted.

**Configuration restore is not yet proven.** The console keeps rotating
backups and falls back to the newest one that both parses and passes its
shape check. Treat the snapshot
tooling as a snapshot: restoring from one is being verified, not demonstrated.
A configuration file that parses but holds the wrong values is still accepted.
"""


def routes(repo: pathlib.Path):
    """Pull (method, path, line) out of server.py by walking the handlers.

    A route belongs to whichever `do_GET` / `do_POST` body it sits in, which
    is the only place the verb is actually decided.
    """
    src = source_state(repo, "WebConsole/server.py")[0].splitlines()
    method = None
    out = []
    for n, line in enumerate(src, 1):
        m = re.match(r"\s*def (do_GET|do_POST)\b", line)
        if m:
            method = m.group(1)[3:]
            continue
        if method is None:
            continue
        for rx in (r'path\s*==\s*"([^"]+)"', r'path\.startswith\(\s*"([^"]+)"'):
            for p in re.findall(rx, line):
                out.append((method, p, n))
    return out


def render(found):
    seen = {}
    for method, path, line in found:
        seen.setdefault(path, set()).add(method)
    rows = ["| Path | Verb | What it is for |", "|---|---|---|"]
    for path in sorted(seen):
        verbs = " and ".join(sorted(seen[path]))
        what = WHAT.get(path, "_Not described yet._")
        rows.append(f"| `{path}` | {verbs} | {what} |")
    # Count DISTINCT paths per verb. Counting matched lines double-counts a
    # route written as two tests, and the inflated number then reads as an API
    # bigger than it is.
    distinct = {}
    for method, path, _l in found:
        distinct.setdefault(method, set()).add(path)
    summary = ", ".join(f"{len(v)} {k}" for k, v in sorted(distinct.items()))
    return (HEADER + f"Routes found in the source: {summary}.\n\n"
            + "\n".join(rows) + "\n" + FOOTER)


def demo():
    import tempfile
    src = '''
class Handler:
    def do_GET(self):
        if path == "/healthz":
            pass
        if path == "/api/state":
            pass
    def do_POST(self):
        if path == "/api/ctl":
            pass
'''
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "WebConsole").mkdir()
    (d / "WebConsole" / "server.py").write_text(src, encoding="utf-8")
    found = routes(d)
    r = [(m, path) for m, path, _line in found]
    assert ("GET", "/healthz") in r, r
    assert ("GET", "/api/state") in r, r
    assert ("POST", "/api/ctl") in r, r
    # the point of the whole parser: a route must not pick up the other verb
    assert ("GET", "/api/ctl") not in r, r
    assert ("POST", "/healthz") not in r, r
    page = render(found)
    assert "| `/api/ctl` | POST |" in page
    print("self-check ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../TDStage")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--working-tree", action="store_true",
                    help="read the checkout instead of HEAD (documents uncommitted code)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    globals()['WORKING_TREE'] = a.working_tree
    if a.selftest:
        demo()
        return
    repo = pathlib.Path(a.repo).expanduser().resolve()
    if not (repo / "WebConsole" / "server.py").exists():
        sys.exit(f"no console source under {repo}. Pass --repo <path to TDStage>.")
    found = routes(repo)
    page = render(found)
    if a.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != page:
            sys.exit("api.md is stale. Run: python3 tools/gen_api.py")
        print("api.md is current")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    undescribed = sorted({p for _m, p, _l in found if p not in WHAT})
    print(f"wrote {OUT} ({len(found)} routes)")
    if undescribed:
        print("no description yet for: " + ", ".join(undescribed))


if __name__ == "__main__":
    main()
