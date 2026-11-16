---
title: A session without TouchDesigner
parent: Operations
nav_order: 14
---

# A session without TouchDesigner

{: .no_toc }

The console does not need TouchDesigner. It receives the phones, merges their
clouds, finds the people and sends `/track` and the field stream on its own. If
the hub is not available - no licence on the machine, no time to set it up, or
a test that is about the console rather than the visuals - this is what to run
and what you will and will not see.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

{: .warning }
> **Steps marked UNVERIFIED have not been run on a Windows machine without
> TouchDesigner.** They are read from `WebConsole\windows\*.bat` and
> `server.py` on main, which is the same thing as being right about what the
> scripts do and not the same thing as having watched it work. A reviewer is
> going through this path now; this page will be corrected from what they find
> rather than left as reasoning.

## What to start

**Run `WebConsole\windows\show.bat`, not `run.bat`.** [UNVERIFIED on a machine
without TouchDesigner]

`show.bat` starts two things: the TDP4 bridge, then the console. On a show
machine that is for TouchDesigner's benefit - the bridge receives the phones
outside TD and hands whole frames to both readers through a memory-mapped file.
**Without TouchDesigner you still need it.**

`run.bat` starts the console with `--tdp4-port 0`, which turns off the
console's own phone-facing listener. On a show machine the bridge owns 9003 and
feeds both readers; the flag is 0 so that the fallback shape also works, where
TouchDesigner binds 9003 itself and has to be able to do it the instant it
launches. So with no TouchDesigner and no bridge, nothing
is listening on 9003 and the console has no point data at all - the page comes
up, the phones appear, and the stage stays empty.

So either start the bridge (which `show.bat` does), or give the console the
port itself. Arguments pass through `run.bat`:

```
WebConsole\windows\run.bat --tdp4-port 9003
```

[UNVERIFIED] That is the simpler shape when nothing else wants the port, and it
takes the bridge out of the picture. The bridge is still the better choice if
TouchDesigner might join later in the day, because then nothing has to be
restarted.

## Telemetry: start the console on 9000, do not retarget the phones

`run.bat` starts the console listening for telemetry on **UDP 9001**, because
on a show machine TouchDesigner owns 9000. The phones, set up for a normal show,
send to 9000 - where nothing is listening today.

**Start the console on 9000 instead.** Arguments pass through `show.bat` to
`run.bat` and on to the server, and the last `--listen` wins:

```
WebConsole\windows\show.bat --listen 9000
```

UDP 9000 is already open in `firewall.bat`, so nothing else has to be changed.

{: .warning }
> **Do not press Send telemetry here for this.** It does not just redirect the
> stream: it pushes a **profile** that writes `stage.oscPort` into each phone,
> because that key cannot be moved with a plain control message. The phones then
> hold 9001, and from 23 November - when TouchDesigner is licensed again and
> expects telemetry on 9000 - they are silent to it until somebody retargets
> them back.
>
> The one thing to check before `--listen 9000`: if the client's own bus runs on
> the same laptop it republishes on UDP 9000 too, and the two collide. The
> console logs a note about this when it starts. If that bus is on the machine,
> give it `--out-port 9200` or keep the console on 9001 and accept the cost
> below.

**If telemetry does not reach the console at all**, which is what happens if you
leave it on 9001 with the phones on 9000, the session still mostly works and
loses a specific set of things. The console learns each phone's address **only
from telemetry** - both code paths that set it are telemetry paths - so with
none arriving it never learns where the phones are:

| Still works | Gone |
|---|---|
| Depth frames, the merged cloud, people, `/track`, the field stream | Every `/ctl` command: no Start, Stop, Blackout, Wake, calibrate |
| The roster, markers, registration, the stage cut | Battery, thermal state, frame rate, the clock sync |
| Recording and replaying takes on the phone itself | Any health row that comes from the phone's own report |

You can test a receiver that way. You cannot run a rig that way, which is why
`--listen 9000` is the answer and not a workaround.

## Before a model run: the phones must send colour

The person model needs a colour plane, and **the phones do not send one by
default**. The default plane set is depth and confidence, and the profile the
console pushes carries the same default unless the phone is already streaming
colour.

So for anything that depends on the model - the maturity runs, person masks,
hands, F1 presence from consensus - set the planes to **depth+conf+rgb** on
every phone first, and check the stream line says so. A model that never sees a
picture reports nobody, which looks exactly like a model that is working on an
empty stage.

## What the console shows you

Everything that does not come from the tox:

| | Where |
|---|---|
| Every phone's health, link, battery, thermal state, frame rate | Dashboard |
| The merged point cloud, from the same frames TouchDesigner would have read | Live view's stage view |
| Who is on stage, as the console sees them | Live view, and `/track` |
| The field stream, presence and poses | The F1 client output panel |
| Markers, registration, the stage cut, the person settings | Their own pages |
| The load line: console CPU, keypoint worker CPU, the parts' milliseconds | Under the preset buttons in People only |

The stage view in the browser is **the console's own picture**, not a window
into TouchDesigner. Watch it over the remote desktop; today it is the only
picture of the cloud there is.

## What is missing, and what that costs

| Absent | Consequence |
|---|---|
| TouchDesigner's GPU merge and its point cloud | No show visuals. The console's own merged view is a diagnostic picture, not an output |
| The tox's stage cut, floor and wall planes | The console has **its own** cut with the same arithmetic, so the cut is available - but a cut set in the tox is not set here, and the two are separate settings |
| NDI out | Nothing to send: NDI carries finished visuals from TD |
| The consensus view in TD | The console still sends a copy of every `/track` bundle to 7001 for it; with no TD listening those datagrams go nowhere, which is harmless |
| TD's own telemetry and health rows | The console's Rig health covers the phones; nothing covers the hub, because there is no hub |

The client outputs are not missing. `/track` and the field stream are the
console's, so a content machine can be fed and a receiver tested end to end with
no TouchDesigner anywhere on the network. That is what a day like this is for.

## Before you start, and while it runs

`WebConsole\windows\doctor.bat` is the environment check: it reports the
interpreter, the ports, the USB links it can see and whether the firewall rules
are in place. Run it first. It changes nothing.

{: .note }
The console restarts itself if it exits - `run.bat` loops with a three-second
wait, because the show machine is operated remotely and an exited console with
nobody in the room is worse than a restarted one. **Close the window to stop
it**; Ctrl+C in that window will be followed by a restart. If a second console
is already running on the same configuration file, the script says so and
changes nothing rather than fighting for the port.

To keep a record of the session, run
[the session logger](live-log.html) alongside it, with the console's own
interpreter and a folder that already exists:

```
WebConsole\.venv\Scripts\python Tools\live_log.py --out C:\logs\live-wed.jsonl.gz
```

On a day with no hub, the console's own log and that file are the entire
evidence trail.

## See also

- [Running the console](../console/running.html) for the flags, the ports and
  what binds which
- [Logging a session](live-log.html) for the record
- [When something fails](failure.html) for the phone-by-phone recovery actions,
  which are unchanged by the hub's absence
