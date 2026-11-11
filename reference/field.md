---
title: The field stream
parent: Reference
nav_order: 6
---

# The field stream

{: .no_toc }

The second output for another system, beside [the tracking output](track.html).
Where `/track` sends a handful of typed messages per performer over UDP, this
one sends the occupied space itself, a few kilobytes per frame, over a
WebSocket. It follows the client's 0.4 draft of the field contract; this page
says what the console puts on that socket and what each number was computed
from, so that a receiver knows what it is looking at.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## In one paragraph

The console listens on TCP port 9001 (`--f1-port`) and, while at least one
client is connected, sends three binary message types: a **field** (which
5 cm voxels of the stage volume are occupied, and how certainly), a
**presence** list (where the people are, as floor footprints, with no
identity), and about once a second the **sensor poses** (where each phone is).
Default rate is 15 Hz (`--f1-hz`). Each of the three starts with the same header
shape: a four-letter magic, the contract version `0.4.1`, a flags byte, a
frame id and a timestamp in seconds on the console's clock. Nothing is
acknowledged. A slow client gets the newest message of each kind, never a
queue of stale ones.

{: .note }
The byte layouts are the client's, from their 0.4 draft note of 22 October
2026, and the console's encoder is parity-tested against their own decoder.
Their decoder is not redistributed here. The struct strings below are what
the console packs; for the authoritative definition of each field, read the
draft.

## Connecting

A plain WebSocket upgrade on `/`; no subprotocol, no authentication, binary
frames only. Two query parameters change what a client receives, and both are
off unless asked for:

| Connect to | You get |
|---|---|
| `ws://host:9001/` | Field, presence and poses. The contract. |
| `ws://host:9001/?points=1` | The same, plus the merged points themselves as a fourth message type, `TDMP`, which is ours and not part of the draft. One point in four, as `x y z` float32 triples after a 20-byte header. A decoder that rejects unknown magic must not ask for this. |
| `ws://host:9001/?presence=1` | **Presence and nothing else**: no field, no poses, no description, no points. For a client that only wants to know where the people are, which is what TouchDesigner's consensus view connects for. The presence bytes are byte-identical to the ones a field client receives. |
| `ws://host:9001/?describe=1` | The same, plus `SMSD`, a description of each sensor behind the source: kind, nominal rate and window, range, field of view, a name. Sent first on connect, again whenever the set of phones changes, and every 10 s as a keep-alive. This is the console's proposal for the draft's open item on a description message; it is opt-in for the same reason as the points. |

Asking for presence only can also save the console the work, not just the
bytes - **but only while every connected client is presence-only**. One
ordinary client alongside it and the field is built as usual, for them. The
other condition is that presence has a people source of its own to come from;
where presence is derived from the field, the field is built whatever the
clients asked for.

The console sends nothing while no client is connected, and it also stops
computing the field, so attaching a client costs the console a few tens of
milliseconds per tick at show load from that moment. Once the last client has
disconnected the smoothing resets; a client that reconnects sees a field that
builds up over a few frames rather than one that remembers the last client's
view.

Pings are answered with pongs; a close frame is answered and the socket
closed. The console's `/healthz` and `/api/state` report the number of
attached clients and the milliseconds each tick costs.

## The field, `SMSF`

Header `<4sBBBBIdHHf3fI`: magic, major, minor, draft, flags, frame id, time,
source id, window in ms, voxel size in metres, the origin of the voxel grid
(x, y, z), and the count of voxels that follow. Then the count of voxel keys
as three int16 each, sorted, and the same count of uint8 weights, padded to a
four-byte boundary.

What goes in:

- **The points** are every phone's cloud registered into the stage frame and
  person-filtered exactly as the console's own Live view shows them. Metres,
  Y up, origin at the centre of the stage floor, the same frame as `/track`.
- **The volume** is 12 m across, 4 m high and 8 m deep, centred on the stage
  origin, so the grid origin is (-6, 0, -4). Points outside it are dropped
  before voxelisation.
- **Voxels** are 5 cm. A voxel's weight is smoothed over time: each frame
  blends the new occupancy half way toward the old, and a voxel leaves the
  field when its weight falls below 8 of 255. So 255 means seen in every
  recent frame, and a voxel that was occupied once fades out over a few
  frames rather than vanishing.
- **The window** is the span of capture times across the phone frames that
  were merged, plus one frame period. It says how old the oldest contribution
  is relative to the newest.
- **The time** is the newest capture time among the merged frames, converted
  to the console's clock through the per-phone clock sync. A phone that has
  no sync yet contributes its arrival time instead, which reads a little
  late rather than wrong.
- **The source id** is 1, always. The draft treats a fusion as one source, so
  a receiver sees one producer whatever the phone count.
- **The SDF flag** is off. The console sends occupancy only; an engine that
  wants a distance field computes it.

## Presence, `SMSP`

Header `<4sBBBBIdHHH2x`: magic, version, flags, frame id, time, source id,
count, window. Then one row of four float32 per person: `x`, `z` on the
floor, `r` the footprint radius, `h` the top height.

How a person is found: the voxels are projected onto 10 cm floor cells, cells
whose column holds weight are connected into components, and a component is a
person when it covers at least 6 cells (about 0.06 m²), reaches between 0.30
and 2.60 m, and is no wider than 1.20 m in radius. Wider than that is set or a
wall, not people; two people in a hug are about 0.8 m. A column counts only
if its weight is at least 190, which under the smoothing above means present
in about two consecutive frames, so a one-frame flicker of a stale mask does
not raise a body.

Two things to settle before building on it:

- **Presence is always people**, whatever the field carries. If the console's
  person filter is off, the field holds everything the phones see, but
  presence is computed from a people-only view, because with the filter off a
  chair passed the body-shape test as a body on the rig (2026-10-25).
- **There is no identity.** Rows are not in a stable order and carry no id.
  For who is where, use [the tracking output](track.html); this list is for
  how many and roughly where.

## Sensor poses, `SMSS`

Header `<4sBBBBIdHH`: magic, version, flags, sequence, time, source id,
count. Then one 56-byte row per phone, `<HBBfd3f4ffff`: sensor id, pose
source, fixed flag, nominal rate, the time the pose was read, position
(x, y, z), orientation as a quaternion (x, y, z, w), then three figures of
merit: position sigma in mm, rotation sigma in millidegrees, and the fit
residual in mm.

Sent about once a second, from each phone's registered extrinsic, which is
the same transform that places its points. Pose source is 0 (calibration)
and the phone is flagged fixed; the console does not yet move phones by
tracking them. The residual is filled only for a marker-calibrated phone,
with the marker solve's RMS error; otherwise it is NaN. Both sigmas are NaN:
they are not measured, and a receiver should not read NaN as zero.

## What was measured, and on what

| Figure | Value | Configuration |
|---|---|---|
| Field size, one person, one phone | about 9.5 KB per frame mean, 13.2 KB at p95, at 1,383 voxels at 5 cm; the stray-blob fix later the same day brought the field to 1,286 voxels, bytes not re-recorded | Recorded take T1 replayed as one phone into an isolated console, person mode Vision, 2026-10-28 |
| Field rate | 14.3 fields per second | Same run, `--f1-hz` at its default |
| Age at the console, capture to field out | p50 47 ms | Same run; the console's own stamp, not a client's |
| Multi-phone density and latency | not measured | Needs the three-phone session |

A client's `age` is arrival time minus the frame's time, and only means
something on a machine that shares the console's clock. `Tools/f1_probe.py`
measures density and latency with the client's own decoder, from `~/Downloads`
where their licence lets it live, so the numbers are what their consumer would
see. Run it on the show machine.

## Recording the stream: `f1_dump.py`

`f1_probe.py` measures the stream and throws it away, and the console records
`/track` only, so nothing kept the field bytes themselves. `f1_dump.py` does:

```bash
python3 Tools/f1_dump.py --port 9001 --out logs/f1-D-cross.f1bin
python3 Tools/f1_dump.py --read logs/f1-D-cross.f1bin   # counts per kind, span, rate
```

One length-prefixed record per WebSocket binary message: `f64` host arrival
time in Unix seconds, `u32` payload length, then the `SMSF`, `SMSP` or `SMSS`
payload as sent. Nothing is decoded on the way in, so **the
client receives the bytes their own consumer would have seen**, per scenario,
rather than this project's interpretation of them. The file is flushed after
every message, so Ctrl-C and a crash lose the same nothing.

It is stdlib only, and its WebSocket client is `f1_probe.py`'s, unchanged.
`--read` reports counts per kind, the time span and the rate, and decodes with
the client's own `sms_td` from `~/Downloads` when that is there.

`phone_session.py`'s scored scenarios run it per scenario beside the `/track`
recording, and the files it writes are what the delivery folder collects as
`f1-*.f1bin` ([the delivery folder](../operations/evidence.html#the-delivery-folder)).

## What the stream does not promise

- **Delivery.** TCP delivers what it sends, but the console sends a slow client
  only the newest message of each type. A client that stalls for a second
  gets one field, not fifteen.
- **Presence identity or order.** See above.
- **Pose accuracy figures.** The sigmas are NaN until somebody measures them.
- **A field with nobody listening.** Nothing is computed, so the first frame
  after a connect is a cold start, and `/healthz` reports zero clients and
  zero cost while that is so.
- **Anything measured on a rig.** Every figure behind this page is simulated.
  The conformance run that reports 14 requirements passing was made on the
  development Mac against the client's decoder read from a local downloads
  folder, so a fresh clone cannot reproduce those rows; the same tool on the
  Windows runner, which has no decoder and no phones, reports 7 passing and 15
  needing a rig. Density and latency with several phones streaming have not
  been measured at all
  ([#29](https://github.com/AristidesAI/TDStage/issues/29)). The byte layouts
  are solid - they are parity-tested - and what the stream does under load is
  not yet known.
