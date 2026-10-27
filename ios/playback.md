---
title: The PLAYBACK page
parent: iOS app
nav_order: 4
---

# The PLAYBACK page

PLAYBACK is the library and the transport. It lists every take on the phone
with its provenance, and controls everything about what goes down the wire when
one is replayed.

A replay re-enters the streamer one step after the packer, so a receiver cannot
tell it from a live phone except by one string in the hello. That is why the
details on this page matter: what you are about to send is whatever the take was
recorded with, unless you change it here.

While a take replays, the camera is off. The LiDAR must not compete with the
replay for thermal headroom, and a phone that captured and replayed at once
would be sending two clouds down one socket.

---

## The header

Top right is a round button: green play, or red stop while a replay is running.
It is disabled when no take is selected and while a take is recording.

The line under the title reads the state: `Choose a take below`,
`Selected: <name>`, `ARMED · 5s`, `Importing…`, `REPLAYING <name>`,
`PAUSED · <name>`, or `Recording — stop it before replaying`.

When nothing is playing, the outcome of the last import, armed start or refused
action is shown in a panel under the header.

---

## Now playing

Five figures while a replay runs.

| Stat | Reads |
|---|---|
| SENT | Frames sent so far this replay |
| FPS | The rate the player is actually pushing through the socket |
| LOOPS | Completed loops |
| SPEED | The current speed multiplier |
| DROP | Frames abandoned by the streamer |

Under them, the same wire line the other pages show, plus the device id the
replay is being sent as. A replay depends on the network exactly as much as a
live stream does. A green socket is still not a reachable receiver.

---

## PLAY

This section appears once a take is selected.

### Transport row

Four buttons: step back one frame, play or pause or resume, step forward one
frame, stop. The step and stop buttons only act on a running replay.

### Scrub bar

A frame-accurate slider, with the frame number, the elapsed and total times,
and the loop count. Releasing the slider seeks.

### Speed

Four preset buttons (0.25×, 0.5×, 1×, 2×) and a slider from 0.05× to 4×. The
recorded intervals are scaled by this figure.

Timing follows the recorded intervals. A take recorded at 28 fps replays at
28 fps, and a dropout stays a dropout, because a replay that silently
regularised the stream would hide exactly the faults it exists to reproduce. A
single gap is capped at 5 seconds, so one bad timestamp cannot park a replay
forever.

### Loop

On by default, with an optional gap of up to 5000 ms between loops.

### Pose sent with the take

| Option | What is sent |
|---|---|
| As recorded (default) | The pose the take was recorded with |
| Current pose | This phone's pose now. Use this for a take made before the rig was calibrated, replayed on the calibrated rig |
| Identity | No transform. The cloud arrives in raw camera space |

### Planes on the wire

| Option | What is sent |
|---|---|
| As recorded (default) | Every plane in the file |
| Depth+conf | Confidence kept, colour dropped |
| Depth only | Depth alone |

Planes are dropped from each frame before it is sent. Depth is always kept.
This lets an RGB take be replayed depth-only to A/B the link budget without
re-recording.

### More playback controls

A collapsed group.

- **Rewrite timestamps to now.** On by default. The frame clock keeps moving
  forward, so latency meters read sensibly and a loop never steps backwards.
  Off replays the recorded clock verbatim, which is only useful for offline
  analysis: a receiver that judges latency will see a take-aged stream.
- **Trim.** Three buttons: *Set in here*, *Set out here*, *Clear*. "Here" is
  the frame now playing. The same code runs for the buttons and for the remote
  verb, so they cannot disagree about what "here" means.
- **Pre-roll.** A countdown of up to 30 seconds before the replay starts. This
  is the same setting the RECORD page uses.
- **Restart live capture when playback stops.** Off by default.

Every control in this section applies to a running replay on its next frame.
Nothing restarts.

---

## PLAYBACK NETWORK

A replay goes down the same socket, over UDP, to the same destination as the
live stream. That identity is the whole point of replaying from the phone
rather than from a computer. This panel exists so you can see it is true, and
override it deliberately without touching the live configuration a show depends
on.

| Row | What it shows |
|---|---|
| Replay goes to | The destination in use. Green when it matches the live stream, orange when overridden |
| Send replays somewhere else | Off by default. Turns the override on |
| Host | Only shown when the override is on. Blank follows the live host |
| Port | Only shown when the override is on. Default 9003 |
| Send as | This phone's device id, or another id from 0 to 9 |

**Send as** stamps a different device id into every replayed packet, so one
phone can stand in for another on a receiver's roster. The point stream, the
hello and the telemetry all move to that id together, so the receiver sees one
device standing in rather than two halves.

The telemetry destination and the control listener are not affected by this
panel. Only where the replayed depth goes.

When a replay stops, the socket is put back on the live destination. The live
stream never inherits a test receiver's address.

---

## TAKES

The library. A header shows the take count, a sort picker (Newest, Longest,
Largest), a refresh button, and **Import**.

Under the header: total size on disk, total recorded duration, free space; and
a reminder that a take is one self-describing file that imports onto any other
phone and plays as if it were recorded there.

### A take's row

Each row shows an icon, the name, the duration, the date, and a one-line
summary: grid, planes, frame count, measured fps, size, codec, plus `imported`
and `recovered` where they apply. Typed notes appear in italics underneath.

The icon is a waveform while that take is the one replaying, a stack otherwise,
and a warning triangle when the take was never cleanly closed.

Tap a row to select it. Tap again to deselect. A selected row shows its
actions:

| Action | Notes |
|---|---|
| Play | Disabled while a take is recording |
| Info | Expands the details block below |
| Export | The iOS share sheet. Disabled while that take is being written |
| Rename | Asks for a name. Refused while the take is in use |
| Delete | Asks for confirmation, and says the size and duration first. Cannot be undone |

Export, Rename and Delete are all disabled for the take currently being
written, and while an import is running.

### The details block

What makes a take usable a month later: which phone, which pose, which grid,
what it was pointed at.

| Row | Reads |
|---|---|
| Device | The recording phone's device id |
| Phone | The hardware model identifier |
| App / OS | Which app and which iOS version recorded it |
| Pose at record | `identity`, `gravity` or `marker` |
| Nominal rate | The capture rate that was configured |
| Recorded | Present only on a decimated take: 1 frame in N |
| Codec | `shuffle+deflate`, `lz4` or `raw` |
| Bytes / frame | The honest measure of what compression achieved on this content |
| Dropped writing | Present only when frames were dropped |
| Origin | `recorded on this phone` or `imported` |
| Sent to | The destination address and port at record time |
| Closed | `cleanly`, or `no footer — recovered by scan` |
| File | The file name on disk |

The fields are selectable, so they can be copied into a session note.

### Empty library

The page says so, and explains that a `.tdp4rec` from Files, AirDrop or Mail
opens straight into the app, whichever phone and whichever of the two apps
recorded it.

---

## Import

**Import** opens a file picker that accepts the take type and, deliberately,
any data file, because a take that arrived by a route which lost its type
label can still be picked: the import validates the bytes, not the label.

A take arriving from outside the app switches the phone to this page on its
own, because this is where the outcome is reported and where the take can be
played.

Import and export are described in full on
[the RECORD page](record.html#export-and-import).

---

## What a receiver sees during a replay

Everything a live phone sends, with two differences:

- the hello JSON carries `source: playback` and the take's name,
- the telemetry reports `playback` rather than `live` for its source.

Nothing else changes. Same destination port, same packet layout, same
fragmentation, same latest-wins. The telemetry namespace, the stream
description, the plane mask and the grid size all describe the replay rather
than the camera that is switched off.
