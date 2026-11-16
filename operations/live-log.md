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

Standard-library Python 3, so it runs on the show PC as it is. On Windows, call
the console's own interpreter and give it a folder that already exists:

```
WebConsole\.venv\Scripts\python Tools\live_log.py --out C:\logs\live-wed.jsonl.gz
```

`--out` does not create the directory, so `C:\logs` has to be there first. On a
Mac, or anywhere `python` is already the right one:

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

To check the logger itself on a machine with no console running, which is the
cheap thing to do the morning before a session:

```
WebConsole\.venv\Scripts\python Tools\live_log.py --selftest
```

It stands up a fake console on loopback, logs it, and reads the file back
through every report. It passed 55 of 55 on the dev Mac on 17 November 2026, at
`cd5f2a8`. A failure there is the tool or the interpreter, before anything about
the rig is in question.

**On screen it prints events, not samples**, each with the clock time: the
keypoint worker restarting, with the reason the console gave; the worker's state
changing; the console going quiet and coming back; `/track` starting and
stopping, including **`/track output OFF`** and **`Record /track OFF`**, which
are the two an operator most needs to see the moment they happen. A quiet
screen means nothing happened.

Since 17 November a console restart no longer ends a `/track` recording: the
console saves the switch and resumes recording **into a new file** at the next
boot, warning that it has. So `Record /track OFF` on the screen means an
operator turned it off, not that a restart did, and the frames sent while the
console was down are in no file at all.

## What lands in the file

One JSON object per line, gzipped when the name ends `.gz`:

```json
{"t": "2026-11-18T10:04:31.512+00:00", "ts": 1794996271.512, "ms": 14.2, "live": {...}}
```

`live` is the console's whole `/api/live` answer, so the file holds everything
that endpoint knows at that second, not a chosen subset.

It also **reads logs other tools wrote**: UTF-16 with or without a byte-order
mark, UTF-8 with one, stray cp1252 bytes, and a bare `/api/live` object per
line. That matters on Windows, where PowerShell's own redirection writes UTF-16
and `Add-Content` adds a BOM, so a log captured by hand is still readable. When the console does
not answer, the line says so instead:

```json
{"t": "...", "ts": ..., "ms": ..., "error": "timed out"}
```

**Those lines are kept on purpose.** A console that stopped answering is the
evidence; a log that skipped the gap would hide it.

### What one sample holds

`/api/live` answers with these groups, so a log line holds all of them a
second. What each is worth reading afterwards:

| Group | What is in it |
|---|---|
| `store` | The sequence number and one row per device: id, source, point count, frame rate, age. The honest answer to "were the phones actually sending" |
| `tdp4`, `bridge` | The two ingest paths: running, the port, frames, errors, and `collisions`, the device ids two sources were sending as at once. `bridge.dup` counts frames the other path had already stored |
| `person` | The person filter: the mode, which backend answered, whether a fresh Apple Vision mask existed, and the consensus voters and their statistics |
| `obs`, `yolo` | The two person observers' own state. `yolo.restarts` and `yolo.lastRestart` are the two the screen prints as events |
| `track` | The `/track` emitter: whether output is on, its rate, its latency, the performer count. **Read `track` before anything else in a run**: with output off, its figures freeze |
| `trackRec` | Whether `/track` was being recorded, which is a different switch from output |
| `ndi` | Whether NDI is available and whether it was publishing |
| `sim` | The built-in simulator: running, how many devices, which rig and planes. A run with this running is not a run with phones |
| `settings`, `presets` | Every setting's value at that second, and each preset's state. This is where the run table reads the maturity fraction, the cut and the wall from, rather than from memory |
| `load` | What the console cost: its own CPU as a percentage of one core, the keypoint worker's, per-thread figures where the platform gives them, each subsystem's last timing in `parts`, and `mode`, the performance preset (`full` means none) |
| `rgbRate`, `gc` | Colour arrival rates, and Python's garbage-collector counters for a memory question |
| `import_error` | Set when a module the console wanted would not import. Empty is the normal answer |

Two fields are worth knowing by name, because they are what a restart argument
turns on later: `yolo.restarts`, the count so far, and `yolo.lastRestart`, the
log line from the most recent one. The second carries the console's own reason, so the
report says "the worker restarted because nothing answered inside the limit"
rather than only that it restarted.

## Typing marks as it runs

While it is running, type a note and press Enter. It goes into the log with its
clock time. Free text is fine for anything you want to find later.

Four marks are special, and typing them turns a session into something
scoreable. Each is a run name, then the word:

| Type this | When |
|---|---|
| `A seed` | as you press **Stage is empty now** |
| `A start` | instead of `seed`, for a run you deliberately do not seed |
| `A in 2` | as two people walk on (the number is how many) |
| `A out` | as the last one leaves |
| `A end` | after the 30 seconds of empty stage |

`A` is whatever you call the run - use `A`, `B`, `C` for four runs in a morning.
All four marks have to be present for a run to score; a run missing one is
reported as missing it rather than guessed at. Case does not matter, and **the
first mark of each kind is the one used** - type a second `in` and the report
names it as ignored rather than quietly replacing the first.

One thing to know before the day: if you abort a run and type its `seed` or
`start` again **before its `end`**, the unfinished attempt is dropped and the
new one is scored, with a line in the report saying so. Once a run has its
`end`, a later `seed` under the same name is the ignored repeat instead, so a
genuinely separate run wants a new name.

Two more marks bracket an inverted-body attempt rather than a maturity run:

| Type this | When |
|---|---|
| `armA start` | as the performer goes up, or as the arm begins |
| `armA end` | as it finishes |

`armB` and `armC` likewise. Those are read by the intake report below, which
also finds two of the arms **without** any marks at all: it reads the interval
the cyr preset was applied over as arm B, and the interval `Rotate and retry`
was on as arm C. So a session that forgets the marks still gets scored for the
arms that are visible in the settings, and the marks are what the depth-only
arm needs, since it is the one nothing in the settings records.

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
| Valid | **NO when `/track`'s output was off for any sample in the run.** Its `/track` columns then froze and mean nothing. Read this one first |
| Maturity fraction, box, floor cut, wall | The settings that run actually used, read out of the samples rather than from memory |
| Seeded | Whether the run began with **Stage is empty now** (a `seed` mark) or without it (a `start` mark) |
| Worker restarts | The keypoint worker's restart count at the end of the run |
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

Two notes the report prints for itself, worth knowing before you plan the runs:

**Seeded runs cannot be compared on maturity fraction.** Pressing Stage is empty
now makes the learned share 1.0 whatever the fraction is set to, so two seeded
runs that differ only in that setting score alike by construction. To compare
fractions, run unseeded - `start` instead of `seed`.

**The false-performer count is sampled once a second**, so it counts seconds
whose single sample showed a performer. One that lived under a second can fall
between samples. Every frame is in the `/track` recording or the client's own
capture if the exact count matters.

### Everything in one read

```bash
python Tools/live_log.py --intake live-wed.jsonl.gz
```

The report to run first after a session, and the one to paste into a write-up.
It answers, in order: how many samples the log holds and how many of them went
unanswered, the span it covers; every keypoint-worker restart with the reason
and every gap where the console went quiet; `/track`'s rate and latency; the
maturity runs from their marks; and the inverted-body arms, from their marks and
from the settings. `--marks` works here too, for marks written on paper.

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
