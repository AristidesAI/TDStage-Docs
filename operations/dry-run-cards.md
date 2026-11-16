---
title: A dry run, card by card
parent: Operations
nav_order: 15
---

# A dry run, card by card

{: .no_toc }

The test cards for the London dry run of 18 November 2026: three phones, the
console on a laptop, no TouchDesigner, 75 minutes after placement. They are
here because the shape repeats. Every short session on a borrowed stage has the
same parts: things to settle before the clock starts, a few timed runs with
marks typed into the log, a stream check, and a reset so the next person finds
the rig as they left it.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## The shape of the session

| London | Card |
|---|---|
| before 10:45 | 1. Before you start, during placement |
| 10:45 | 2. Maturity run A |
| 10:53 | 2. Run B |
| 11:01 | 2. Run C |
| 11:09 | 2. Run D, done about 11:17 |
| 11:20 | 7. F1 live minute, two people walking |
| 11:25 | 3. Inverted body, first run (arm A, the defaults) |
| 11:35 | 3. Inverted body, second run (arm B, depth only) |
| 11:45 | Settings back |
| 11:50 | 9. One take per phone model, only if we are on time |
| 12:00 | End. Upload after the window |

That is 56 minutes of work in 75 before card 9; card 9 runs only on the slack.
The card numbers are the ones the first version of the plan used, so a caller
with the old sheet and a caller with this one name the same thing. If a run
overruns, drop card 9 first, then shorten the inverted-body positions.

Two rules hold for the whole session. A caller says each step aloud, and
someone writes the laptop's clock time at the start of every card and every
move. The log is read by those times afterwards, so a minute nobody wrote down
is a minute that cannot be scored.

## Card 1. Before the clock starts

Placement runs until 10:45 and every one of these fits inside it.

**Phones.** The same build on all three. Note each phone's model, height, and
whether it is landscape, portrait or flipped. Do not edit the UDP Port field on
a phone's Live page, nor the Host and Port fields under "Send replays somewhere
else" on its Playback page: a value above 65535 crashes the app, and it can
crash again at relaunch. Change ports from the console only. If a phone
relaunches with a dark screen, triple-tap to light it, look for a red Device ID
message, then on that phone's card in the console press Wake, and once the
screen is up press Blackout again.

**Console.** Start it once, from the repository root, in a Command Prompt:

```
WebConsole\windows\show.bat --listen 9000
```

Why that line and not `run.bat`, and why not the "Send telemetry here" button,
is on [A session without TouchDesigner](no-touchdesigner.html). Run it once:
a second `show.bat` leaves two stray windows, a minimised one whose title begins
"TDStage bridge" and a console window saying "NOT started: another console is
already running". Close both. Open the minimised bridge window from the taskbar
once; if it never prints "receiving on :9003", close every TDStage window and
any stray python.exe and start again.

**Colour on.** In the Live view press **Colour ON for all phones**, then check
that each phone's camera view shows a real picture. By default the phones send
depth and confidence with no colour, and the person model has nothing to read.

**Live view settings.** People only: **Consensus**. Under Client output (F1
contract): **Send /track** pressed so it reads **Sending /track**, and
**Record /track** on, the button beside it. Write down the console's version.

**The logger.** In its own window, from the repository root, started before
placement and left running until the wrap:

```
mkdir C:\logs
WebConsole\.venv\Scripts\python Tools\live_log.py --out C:\logs\live-wed.jsonl.gz
```

What it prints, what lands in the file, and how the marks below are scored is
on [Logging a session](live-log.html). If you close the window by accident,
start it again with the same line; it appends.

**Performance.** Run in **Full**. The Full button is greyed out when no preset
is applied, because it is the mode in force, and the load line under the
buttons begins "Mode full". Lite exists for a laptop that also runs
TouchDesigner. Press it only if the load line shows the console or the keypoint
worker at 90 per cent or more for longer than a few seconds, and then keep it
for every run of card 2.

## Card 2. Maturity: four runs, 30 s of empty stage after each

Pressing **Stage is empty now** counts the whole room as learned at once, so a
seeded run matures at a Maturity fraction of 0.05 and of 0.15 alike. That
decides what four runs can measure, and the two designs answer different
questions.

**All four seeded.** A 0.15 and B 0.05 with the stage box as it is; C 0.15 and
D 0.05 with the box drawn to the test area plus 0.5 m. This compares the two
boxes. It cannot tell the two fractions apart.

**Two seeded, two unseeded.** A 0.15 seeded, box as it is; B 0.15 unseeded;
C 0.05 unseeded; D 0.15 seeded, box drawn to the area. A against D is the box;
B against C is the fraction, and it is the only way to see it. In simulation
the unseeded runs matured at the same time at both values, so no difference is
itself a result.

Before run A, write down the three numbers the Stage cut section shows. "As it
is" means those, not the shipped defaults (Stage half-width 9, Stage z min -9,
Stage z max 9). For the smaller box, read the test area's edges off the Live
view's floor grid: half-width is half the area's width plus 0.5 m, z min and
z max are the front and back edges each 0.5 m further out. The sliders stop at
3 for the half-width and at -3 / 3 for z, a 6 by 6 m box, in 0.5 m steps. If
the area plus 0.5 m is smaller than that, set the minimums and write down what
the sliders show, not what you calculated. Leave the floor cut and the wall as
they are, so the runs compare with earlier replays.

Each run takes about 7 minutes:

1. Live view, Tuning, Expert settings on, group segmentation: set **Maturity
   fraction**, and for the runs with the smaller box the three box values.
2. Restart the console, so its background starts empty. In the console's
   window press Ctrl+C once; Windows asks "Terminate batch job (Y/N)?"; type
   `N` and press Enter, and the console starts again by itself after 3 s. If
   `Y` went in by mistake, start `WebConsole\windows\run.bat --listen 9000`
   from the repository root, not `show.bat`, which would start a second bridge.
3. Wait until all three phones show on their device cards, then **40 more
   seconds**. A phone joining can blank `/track` for the whole rig for a few
   seconds up to half a minute later. From here on nobody touches a phone or a
   tripod.
4. Press **Record /track** again. A restart switches it off, and without it the
   run has no `/track` file from the console's side.
5. With the stage empty, type `A seed` in the logger window and press Enter.
   For a seeded run then press **Stage is empty now**; for an unseeded run
   press nothing. Wait until the logger prints "/track publishing (settled)",
   or the `/track` line in the Live view no longer says "learning background"
   or "background settling". After 90 s without that, type `A nosettle` and go
   on anyway; the log keeps the time.
6. Two people walk on: type `A in 2`. Then, for 3 minutes: walk around and
   cross each other; both stand still for 20 s; 20 s within an arm's length of
   each other; walk along the edges of the area.
7. Both leave every phone's view: type `A out`. After 30 s of empty stage,
   nobody in view of any phone, type `A end`.

Each restart starts `/track`'s frame number, its clock and the performer ids
again from 0 and 1, so a receiver's capture shows a reset at every run. That is
expected.

What the log answers per run: the time from the seed mark to publishing; of
the 3 minutes, the share with `/track` settled, with no performer, and with the
right number of performers; any second of the empty stage with a performer,
with the source named; and the preset the run ran in.

## Card 7. The F1 live minute

With two people walking, read the live F1 stream for at least 60 s, with your
own decoder outside TouchDesigner, or from the `WebConsole` folder with the
client's `sms_td.py` in your Downloads folder:

```
.venv\Scripts\python ..\Tools\f1_probe.py --seconds 60
```

Write down the probe's summary lines (field frames per second, clusters max,
pose rows, age p50 and p95, where age is arrival minus capture time), the full
text of any traceback if it stops, and the clusters count against `/track`'s
performer count over the same seconds. If your own decoder runs, also note the
message count per type (SMSF, SMSP, SMSS). About 3 minutes.

## Card 3. The inverted body, twice

Only if it is safe: a spotter for every inverted position, a mat, and only
positions the person chooses to do.

Set-up: start one take per phone from the console's Record button, not Arm
record, and check that every phone's Record page shows RECORDING before the
first position; on the current builds a Record pressed while a take runs does
nothing. Colour on, **Record /track** on (press it again if the console
restarted), the logger running. The spotter stays out of every phone's view
except while spotting; where a spotter must stand in, say so aloud and
write the time, in both runs.

Positions, 10 s each, about 3 m from the nearer phone and inside at least two
phones' views:

1. Stand upright, the baseline.
2. Lie on the floor side-on to phone 1, head to its left; then head to its right.
3. Lie across a table at hip height, both directions.
4. A handstand or headstand against a wall with the spotter, or hang upside down
   from a bar if one exists.
5. A slow cartwheel or a forward roll.
6. If a cyr performer is there: 60 s slow, then 60 s at performance speed.

**First run, arm A, about 10 minutes.** People only Consensus, Send /track
reading Sending /track as in card 1. Type `armA start` into the logger before
the first position and `armA end` after the last.

**Second run, arm B, about 10 minutes.** Press the **Cyr wheel (arm B)**
button in the Live view's People only panel. [The depth-only run](depth-only.html)
has the seven values it sets and the three conditions that are not optional:
Stage is empty now first, one person inside the stage box, Rotate and retry
off. One more for this card: Max performers 1 sends the most confident body
each tick with no memory, so a spotter in view, or a standing wheel, can take
the one id from the inverted performer; the spotted seconds are read
separately. The preset's apply is in the log, so arm B needs no typed marks.
Afterwards press **Reverse cyr preset**; it puts back exactly what was set
before.

After each recorded run, check that every phone's Record page says "Live
capture running" and not "RECORDING". A lost stop leaves the next run with no
take, silently. Do not press Stop while a phone shows "ARMED": it does not
cancel the countdown and the take starts anyway; the console's Cancel arm button
does.

## Settings back

About 5 minutes. Maturity fraction 0.15 and the box back to the three numbers
written down before run A; **Reverse cyr preset** if it is still applied;
People only Consensus, which is this session's setting and not the console's
own default of Off; Rotate and retry off, which it should have been all day.
The console saves settings to `WebConsole\config.json`.

## Card 9. One take per phone model

Only if card 3 has ended by 11:45, so that settings back is done by 11:50. It
moves the phones, so it is the last thing and nothing follows it. Three
generations in one rig (a 12 Pro Max, a 16 Pro Max and a 17 Pro) is the first
chance to measure all three LiDAR units from the same spot. One tripod, one
spot, aimed at the same empty part of the room, about 3 to 5 m of floor and a
wall in view. For each phone in turn: mount it, Record 10 s with nobody in
view, then 10 s with one person walking slowly straight away from it. Note
which take is which phone. What comes out: valid depth, high-confidence share,
noise and flying pixels per 0.5 m band, per model.

## After the window

Upload the takes, the `WebConsole\logs` folder (it holds the `/track`
recordings and the console log), `WebConsole\config.json`,
`C:\logs\live-wed.jsonl.gz`, any receiver-side `/track` captures, and the
clock-time notes.

## See also

- [A session without TouchDesigner](no-touchdesigner.html) for the start
  line, the telemetry port, and what the absent hub costs
- [Logging a session](live-log.html) for the logger, the marks, and the scored
  table the Wednesday-night read produces
- [The depth-only run](depth-only.html) for the cyr preset row by row and the
  three conditions
- [Getting the room out of the cloud](background.html) for the stage box and
  learning a background
