---
title: Logging a session
parent: Operations
nav_order: 13
---

# Logging a session

{: .no_toc }

`Tools/live_log.py` samples the console once a second and writes the lot to a
file, so a test session leaves a record instead of an impression. It also scores
runs, if you type four short marks as they happen.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## Starting it

Standard-library Python 3, so it runs on the show PC as it is:

```bash
python Tools/live_log.py
```

That logs the console on the same machine, port 9080, to
`live-<date>-<time>.jsonl.gz` in the current directory. For a console on another
machine, which is the usual shape on a show - the laptop runs the console, you
watch from elsewhere:

```bash
python Tools/live_log.py --url http://192.168.1.20:9080 --out C:\logs\live-wed.jsonl.gz
```

`--every` changes the sample interval from its default of one second. Ctrl+C
stops it.

**On screen it prints events, not samples**, each with the clock time: the
keypoint worker restarting, with the reason the console gave; the worker's state
changing; the console going quiet and coming back; `/track` starting and
stopping. A quiet screen means nothing happened, which is the point.

## What lands in the file

One JSON object per line, gzipped when the name ends `.gz`:

```json
{"t": "2026-11-18T10:04:31.512+00:00", "ts": 1794996271.512, "ms": 14.2, "live": {...}}
```

`live` is the console's whole `/api/live` answer, so the file holds everything
that endpoint knows at that second, not a chosen subset. When the console does
not answer, the line says so instead:

```json
{"t": "...", "ts": ..., "ms": ..., "error": "timed out"}
```

**Those lines are kept on purpose.** A console that stopped answering is
evidence, and a log that silently skipped the gap would hide the only thing
worth knowing about it.

Two fields are worth knowing by name, because they are what a restart argument
turns on later: `yolo.restarts`, the count so far, and `yolo.lastRestart`, the
log line from the most recent one. The console's own reason for a restart is in
the second, which is the difference between "the worker restarted" and "the
worker restarted because nothing answered inside the limit".

## Typing marks as it runs

While it is running, type a note and press Enter. It goes into the log with its
clock time. Free text is fine for anything you want to find later.

Four marks are special, and typing them turns a session into something
scoreable. Each is a run name, then the word:

| Type this | When |
|---|---|
| `A seed` | as you press **Stage is empty now** |
| `A in 2` | as two people walk on (the number is how many) |
| `A out` | as the last one leaves |
| `A end` | after the 30 seconds of empty stage |

`A` is whatever you call the run - use `A`, `B`, `C` for four runs in a morning.
All four marks have to be present for a run to score; a run missing one is
reported as missing it rather than guessed at.

If the marks were written on paper instead, `--marks` takes them as a file of
`10:12:30 A seed` lines and merges them in.

## Reading it back

```bash
python Tools/live_log.py --summary live-wed.jsonl.gz
```

The events of a finished log: the same lines the screen printed, from the file.

```bash
python Tools/live_log.py --runs live-wed.jsonl.gz
```

A table, one row per marked run. What each column answers:

| Column | What it tells you |
|---|---|
| Maturity fraction, box, floor cut, wall | The settings that run actually used, read out of the samples rather than from memory |
| Performance | The engine's tick rate and the keypoint budget. **Runs are comparable only at the same values** |
| Seed to publishing | Seconds from the seed mark to `/track` first reporting a learned scene. "never" if it did not |
| Populated s | How long people were on stage |
| `/track` settled | The share of the populated time the engine called itself mature |
| No performer | The share of the populated time `/track` carried nobody. The number the maturity runs exist to produce |
| Right count | The share where the performer count matched the number you typed in `in N` |
| Empty s | How long the stage was empty at the end |
| Empty s with a performer | **False performers.** A count, with where they came from - the model's masks or geometry - in brackets |

Empty-stage samples start four seconds after `out`, to let people get past the
edge of the cut rather than counting them as phantoms.

## What the table is for

The four maturity runs on 18 November exist to answer one question with a
number: how long after a seed does `/track` publish people, and does it then
keep publishing while they are there. **No performer** and **Seed to
publishing** are that answer. **Empty s with a performer** is the other half:
whether the configuration that publishes quickly also invents people.

{: .note }
The Performance column is there because of a measured trap. The performance
presets change the engine's tick rate and the keypoint budget, and two runs at
different settings are not comparable - a slower engine shows up as a longer
settle and a different false-performer count for reasons that have nothing to
do with what you were testing. The column makes that visible in the table
instead of in somebody's memory.

## See also

- [Evidence and claims](evidence.html) for what counts as a measurement and how
  to label one
- [Running the console](../console/running.html#performance-modes) for the
  presets this table's Performance column reports
- [The depth-only run](depth-only.html) if the body on stage is in a wheel
