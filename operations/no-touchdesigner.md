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
**Without TouchDesigner you still need it**, for a reason that is easy to miss:

`run.bat` starts the console with `--tdp4-port 0`, which turns off the
console's own phone-facing listener. That flag exists so TouchDesigner can own
UDP 9003 the instant it launches. With no TouchDesigner and no bridge, nothing
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

## Then point the phones' telemetry at it

`run.bat` starts the console listening for telemetry on **UDP 9001**, because
on a show machine TouchDesigner owns 9000. The phones, if they were set up for
a normal show, are sending to 9000 - where nothing is listening today.

**Press Send telemetry here** on the console's Dashboard. It retargets every
phone to the console's own listener. Until you do, the phones stream depth
perfectly and read as dead: no health, no battery, no thermal state, and
`Start show`'s verdict names every phone as failed while it is working.

That trap is not specific to today, but today it is certain rather than
possible, because there is no TouchDesigner to be listening on 9000 at all.

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
into TouchDesigner. It is the one to watch over a remote desktop, because it is
the only one there is today.

## What is missing, and what that costs

| Absent | Consequence |
|---|---|
| TouchDesigner's GPU merge and its point cloud | No show visuals. The console's own merged view is a diagnostic picture, not an output |
| The tox's stage cut, floor and wall planes | The console has **its own** cut with the same arithmetic, so the cut is available - but a cut set in the tox is not set here, and the two are separate settings |
| NDI out | Nothing to send: NDI carries finished visuals from TD |
| The consensus view in TD | The console still sends a copy of every `/track` bundle to 7001 for it; with no TD listening those datagrams go nowhere, which is harmless |
| TD's own telemetry and health rows | The console's Rig health covers the phones; nothing covers the hub, because there is no hub |

**What is not missing: the client outputs.** `/track` and the field stream are
the console's, not the tox's. A content machine can be fed, and a receiver can
be tested end to end, with no TouchDesigner anywhere on the network. That is the
whole reason a day like this is worth running.

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
[the session logger](live-log.html) alongside it. On a day with no hub, the
console's own log and that file are the entire evidence trail.

## See also

- [Running the console](../console/running.html) for the flags, the ports and
  what binds which
- [Logging a session](live-log.html) for the record
- [When something fails](failure.html) for the phone-by-phone recovery actions,
  which are unchanged by the hub's absence
