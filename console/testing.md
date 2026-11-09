---
title: Checking the console
parent: Console
nav_order: 9
---

# Checking the console, with no rig

The console carries the client outputs. If it stops, TouchDesigner's cloud is
untouched, but `/track`, the field stream and the NDI feed stop with it
([what dies with each piece absent](resilience.html#what-dies-with-each-one-absent)).
That is reason enough to check it on a Mac, in minutes, before the rig exists.

Every tool on this page runs with no phones and no TouchDesigner. None of them
touch the live rig: they boot their own console on a throwaway config, on ports
in the 947x range, with the TouchDesigner link off and no telemetry listener,
so nothing is ever learned about a phone and no `/ctl` can reach one.

{: .warning }
> That isolation is the whole safety story, and it has been broken by hand
> before: a scratch console started from an empty config pushed its seed poses
> into the live tox and overwrote a real registration. These tools arrange the
> isolation themselves. A console **you** start by hand does not, unless you
> give it `--config`, an off-show web port and `{"td": {"enabled": false}}`.

## Which one do I run?

| After changing | Run |
|---|---|
| Anything in `server.py` | `python3 WebConsole/server_selftest.py` |
| A route, a request body, a query string | `python3 Tools/console_fuzz.py` |
| Anything that loads at boot, before you restart the show console | `python3 Tools/restart_dryrun.py` |
| The motion segmentation engine | `python3 Tools/segment_bench.py --against HEAD` |
| The GPU segmentation path | `<torch python> WebConsole/seg_gpu_test.py` |

## The three paths that broke: `server_selftest.py`

```bash
python3 WebConsole/server_selftest.py          # offline and deterministic
python3 WebConsole/server_selftest.py --real   # this Mac's real interfaces, read-only
```

It imports the real server module — no `main()`, so no HTTP and no telemetry
listener, the TouchDesigner link off, config and logs in a temp folder — and
fakes only the **inputs**: walk tracks, floor clouds, and the text `ifconfig`,
`arp` and `route` print. Everything after those inputs is the shipped code.

| It proves | Because it did not |
|---|---|
| An applied walk align runs to the end: the job reaches `done`, the poses land as the walk placed them, one Undo step, persisted to disk, the live view synced, the poses sent to TouchDesigner, a phone it placed marked checked, and Undo putting the poses back | It ended `failed: KeyError 'score'` |
| `usb_links()` finds a cable phone **with the ARP table hidden** — macOS Local Network privacy hides it from Homebrew's Python, so `arp` prints nothing — by asking `route -n get` on each cable instead. Two cables, two links; an address with no neighbour, none; a readable table still works alone | Homebrew's Python cannot read the ARP table |
| `telemetry_host_for` gives a cable phone its own cable's address, and gives a phone on no cable with a typed LAN host the route toward that host | It fell back to the console's LAN address |
| `GET /api/align/check?wait=1` returns fresh pairs in one call, answers at once from a result under five seconds old, and joins a refresh already running | The first call after a console start returned no pairs and only started a refresh |

**43 checks, passing 9 November 2026.** `--real` runs the two link functions
against this Mac with nothing faked; it runs `ifconfig`, `arp` and `route get`
only, and exits 1 when you give it a phone's cable address and it finds no link
for it.

## Every route, bad input: `console_fuzz.py`

```bash
python3 Tools/console_fuzz.py          # about two minutes
```

It boots the console on a throwaway config in a temp folder (ports 947x,
`--no-autostart`, TouchDesigner off, phones with no host) and sends every POST
route a set of badly typed bodies and every GET route a set of junk query
strings. **A bad field must be a 4xx.** A 5xx or a closed connection is a
defect, not a matter of taste: a browser request that kills a reply is a
console that looks hung in front of an audience.

Routes that start processes, reach phones or stream forever are skipped.

**41 routes against 48 POST bodies and 7 GET queries, 0 failures, 9 November
2026.** When it was first written, on 28 October, 15 POST routes returned 500
and two GET routes dropped the connection.

## Before restarting the show console: `restart_dryrun.py`

```bash
python3 Tools/restart_dryrun.py                                   # WebConsole/config.json
python3 Tools/restart_dryrun.py --config X.json --live http://127.0.0.1:9080
```

A restart mid-get-in is the moment to be sure the console comes back the way
it went down. This boots **this checkout's** console on a **copy** of the live
config and reports what restarting the real one would do.

It reports where the roster came from and which phones it would hold, every
WARN and ERROR the boot logs, the poses link-up would push against what the
running console has right now (`--live`, a read-only GET), the `/track` and
NDI state, auto-recover, and Rig health. **It exits 1 when a pose would change
on restart** — which is the question it exists to answer.

Its isolation is worth knowing, because it reads the real config: the copy's
TouchDesigner and `/track` targets are rewritten to sockets the script itself
owns, every phone's typed host is cleared, and a fake TouchDesigner answers
pings so link-up happens and the poses it would have pushed are recorded
instead of sent.

## The segmentation engine, timed and compared: `segment_bench.py`

```bash
python3 Tools/segment_bench.py                  # time the working copy
python3 Tools/segment_bench.py --against HEAD   # and compare it tick by tick with HEAD
```

It renders the eight-phone show rig with three walkers (`human_sim4.py`, the
same simulator the console sees), unprojects every valid cell the way ingest
does, and drives `segment.MotionBG.update` on a simulated 20 Hz clock. Scenes
are cached — eight seconds of walk, looped — so two variants are compared on
identical input rather than on two different random walks.

`--against` compares every state column, the published foreground and
background, the guard cells and the stats **on every tick**, through an
operator seed at tick 40, a live stage-box change at tick 500, and again with
`FREEZE_BG` on. It exits 1 on the first difference.

Measured 2026-10-27 at 306,000 points a tick: 28.0 ms at `HEAD`, 14.0 ms with
the table joins, identical output.

## The GPU path against the CPU path: `seg_gpu_test.py`

```bash
<torch python> WebConsole/seg_gpu_test.py [--device cpu|mps|cuda] [--ticks 700]
```

`seg_gpu.TorchMotionBG` against `segment.MotionBG`, tick by tick, on
`segment_bench`'s cached scenes. On a float64 device — `cpu`, `cuda` — the two
must match **exactly**: every state column, the foreground, the background, the
guard cells, the stats. MPS keeps float32 times, so there it reports the
overlap of the published sets instead of demanding equality. Exit 1 on failure.

It needs a Python with torch, and the one that runs the console has none
([#39](https://github.com/AristidesAI/TDStage/issues/39)). On this Mac the YOLO
worker borrows another project's venv, which has torch because ultralytics
needs it, and `Tools/show_mac.local` — untracked, per machine — exports that
path as `TDSTAGE_YOLO_PYTHON`. Use the same interpreter here.

## Do the phones agree where one performer is? `calib_check.py`

This one is not a test of the console's code; it is a check on the rig, run
through the console at `/api/rig/calib`, and it is here because it runs from
the same place.

A marker measured from its black square instead of its crop marks is 11 per
cent small. The phone then believes it stands 11 per cent nearer that marker,
and because LiDAR depth is metric, its whole cloud slides away from the marker
along that line — about 0.66 m at 6 m. Two phones on opposite sides slide in
opposite directions, so **one performer appears twice**, and nothing else in
the console notices.

With exactly one person on stage, this does. Each phone's view of that person
is reduced to one floor point, then pushed away from the phone by about one
body depth first — a phone sees only the near surface of a body, so without
that correction every opposite pair would read as a fault.

{: .warning }
> **Never run on real phones** ([#41](https://github.com/AristidesAI/TDStage/issues/41)).
> Its evidence is its own code and CI, and nothing more; it is on
> [the proof-level page](../reference/status.html) as Designed. The arithmetic
> above is read from the code, not measured on a stage.
