---
title: When something fails
parent: Operations
nav_order: 6
---

# When something fails

For each part of the rig: what takes over by itself, what an operator does,
and whether it has actually been seen working.

The status column is the important one. "Verified" means a test or a run
showed it. "Not verified" means it is designed and written but has not been
seen working on hardware. **Gap** means there is no fallback today.

Read the gaps first. They are at the bottom of this page.

## During a show

### A phone's app crashes or is killed

Automatic: the phone resumes streaming when the app relaunches. The console's
auto-recover restarts a phone that comes back without streaming, within about
twelve seconds.

Operator: relaunch the app. Nothing else.

Status: covered by an automated interface test. **Not verified on a rig.**

### A phone dies outright

Automatic: the other phones carry on. The dead phone's identity coasts
briefly, then is released after three seconds rather than frozen, so the
receiving side sees it go rather than seeing a performer stand still forever.

Operator: swap in a spare and set its device id from the console. A fresh
install refuses to stream until its id is confirmed, which prevents a spare
silently colliding with a phone already on the rig.

Status: the id guard is tested. **A spare swap has not been done on a rig.**

### A phone overheats

Automatic: the frame rate steps down as the phone gets hotter, and recovers
after about forty five seconds of cooling.

Operator: shade it or give it air. The console shows capture pressure per
device.

Status: the ladder is tested. **A real heat test has not been run.**

### The wired link routes nowhere

Automatic: the stream falls back to Wi-Fi after five seconds.

Operator: re-seat the cable. A direct cable address can drift, in which case
the console can re-teach the phone where to send.

Status: code review and unit tests. **Not verified on a rig.**

### The receiving bridge process dies

Automatic: the launcher restarts it within two or three seconds, and
TouchDesigner picks it up again when it reappears.

Status: verified. There is also a direct socket path when no bridge is
running.

### The legacy relay is left running beside the bridge

What happens: every frame arrives twice. The console drops the duplicate, so
nothing breaks, but it warns and tells you to stop the relay.

Status: verified by recreating it.

### TouchDesigner crashes

Automatic: the phones keep streaming and the console keeps producing its
outputs.

Operator: reopen the project. The console re-seeds the phone positions when
the link comes back.

One catch worth knowing: phone health reaches the console **through**
TouchDesigner. Until it is back, the phones look dead even though they are
streaming. The console can be told to take telemetry directly.

Status: verified.

### The console crashes

Automatic: the launcher restarts it within about three seconds. The show
state survives the restart. TouchDesigner's point cloud is unaffected.

Cost: the outputs to other systems pause for the restart.

Status: verified.

### The console's configuration file is corrupt

Automatic: it loads the newest backup that parses, keeps the bad file aside
with a timestamp, and logs an error saying so.

Operator: copy another backup into place with the console stopped.

Status: verified by deliberately breaking one and watching a six phone roster
come back.

### Two performers are confused for each other

Automatic: the output flags the identity as uncertain for the whole crossing,
so the receiving side can treat it as provisional rather than trusting it.

This is a property of the measurement, not a bug. See
[Evidence and claims](evidence.html).

## Between shows

| Lost | Way back |
|---|---|
| The TouchDesigner project, damaged or badly edited | Every change is saved as a numbered version. A drift check shows whether a saved project's code matches version control, and can extract its code as plain files. |
| Learned background and floor | Re-learn on an empty stage. Checkpoints are included in every snapshot. |
| Roster, markers, settings | The console keeps its last fifty saves, and they are in every snapshot. |
| A phone's settings after a reinstall | The console keeps each phone's profile and can push it back. |
| Printed markers | Print them again from the console at the rig's size. |
| Everything | Snapshots contain the repositories as bundles that clone with no network, plus uncommitted work as patches. Verified by rebuilding a working tree from one. |

## The gaps

These have no fallback today. They are listed plainly because a gap you know
about can be planned around, and a gap you discover during a show cannot.

**No hot standby for the show machine.** If it dies, the rebuild is from a
snapshot onto another machine. Whether the rig runs one machine or two is
still an open decision.

**The outputs to other systems stop if the console stops.** TouchDesigner's
own point cloud keeps running, so the visuals continue, but anything
consuming the tracking output loses it until the console restarts. It does
restart by itself, but there is a pause.

**App distribution past ninety days.** Test builds expire. For a production
running months ahead that means a re-upload roughly every quarter, or moving
to a distribution route that does not expire. The decision is outstanding.

## Routine that prevents most of this

- Take a snapshot before risky work and before travelling.
- Run the drift check after every project save.
- Keep the change ledger current after a working session.
