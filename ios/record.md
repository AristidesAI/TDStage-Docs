---
title: The RECORD page
parent: iOS app
nav_order: 3
---

# The RECORD page and takes

RECORD turns the live stream into a file called a take. You set a take up once,
before anyone is on the floor, then press one button.

## What a take is

A take is the wire itself.

The streamer assembles the complete TDP4 frame, then cuts it into UDP packets.
The recorder taps that assembled frame, one step before the packets. Playback
hands the same bytes back at the same point.

That has three consequences, and they are the reason the recorder was built
this way:

1. There is no second packer. Nothing in the recording path has to be kept in
   step with the wire format, because it *is* the wire format.
2. A replay is indistinguishable from a live phone to every receiver. Same
   socket, same destination, same fragmentation, same latest-wins policy, same
   hello, same telemetry shape. The only difference is one string: the hello
   says `source: playback` and the telemetry reports `playback` instead of
   `live`.
3. Whatever the phone is sending is exactly what lands in the file. There is no
   separate recording quality to configure.

{: .note }
A receiver must never need to know whether a stream is live or replayed. If a
fix requires a change on the receiver to make playback work, the fix is wrong.

A take is also portable by design. Every frame carries its own grid size,
intrinsics and pose in its own header. The device id on the wire comes from the
phone that *plays* the take. Nothing in the file refers to the recording phone
except as provenance. A take recorded on one phone replays on any other, and
takes are interchangeable between this app and its ARKit sibling.

Files are named `<name>.tdp4rec` and live in `Documents/Takes`, with a `.json`
sidecar beside each one that mirrors the file's own metadata so that listing a
folder of multi-gigabyte takes never opens one. The sidecar is a convenience.
It never travels, and it never needs to: the file is self-describing, and an
import rebuilds the sidecar from the file.

---

## The record button and the status line

Top right is a round record button.

| It shows | Meaning | Pressing it |
|---|---|---|
| A red circle | Ready | Arms or starts a take |
| A dim red circle | Refused: not enough free space | Nothing |
| A number | Counting down a pre-roll | Cancels the armed start |
| A red square | Recording | Stops the take |

The button is disabled while a replay is running. Stop the replay first.

Recording starts the live capture if it is not already running, because you can
only record what is being streamed. If the capture will not start, the reason
appears instead of a silent failure.

The line under the title reads the current state: `Live capture running`,
`ARMED · 5s`, `RECORDING · 1:23 · T2-20261027-141530`, or
`Replaying <name> — stop it to record`.

## The status card

Five figures, refreshed twice a second.

| Stat | Reads |
|---|---|
| FRAMES | Frames written so far |
| SIZE | Bytes on disk so far |
| DROPPED | Frames the writer could not keep up with. Orange when above zero |
| FPS | Measured delivery rate |
| FREE | Free space in GB. Red below the floor |

Under them, the same wire line the LIVE page shows, because a take only exists
if the wire does. The recorder taps datagrams on their way out, so a dead link
is a dead recording.

### Dropped frames

The live stream matters more than the recording. If the writer falls behind,
because of a NAND stall, thermal throttling, or a phone that is also pushing
several megabytes a second, frames are dropped and counted rather than queued
without bound. A recorder that backs up into the show is worse than a recorder
with a hole in it.

A take with dropped frames is still valid. It has gaps.

The dropped count is written into the file header when the take is stopped, so
it survives export without the sidecar.

---

## LAST TAKE

A one-line summary of the newest take, with a button that selects it and
switches to the PLAYBACK page. It shows the name, the date, the frame count,
the duration, the size, and `recovered` if the take was never cleanly closed.

---

## WHAT GETS RECORDED

These are the live stream's own settings. Change them here and the next take
carries the change. All of them are refused while a take is running, because a
take is one file with one geometry in its header.

| Control | Options | Default |
|---|---|---|
| Planes | Depth, +conf, +conf+rgb | +conf |
| Capture rate | 5 to 60 fps, in steps of 5 | 30 fps |

Below them, an estimate of the write rate and the headroom in minutes.

### Planes

Depth is always sent. The confidence plane adds one byte per cell, and tells
the receiver which cells to trust. The RGB plane adds three bytes per cell.

Wire cost per phone, **calculated from the wire format** at 256×192 and 30 fps:

| Plane set | Bytes per frame | Per phone | Eight phones |
|---|---|---|---|
| depth | 98 424 | 23.6 Mbit/s | 189 Mbit/s |
| depth+conf | 147 576 | 35.4 Mbit/s | 283 Mbit/s |
| depth+conf+rgb | 295 032 | 70.8 Mbit/s | 566 Mbit/s |

Eight phones on `depth+conf` is about 30 per cent of a gigabit link. Eight
phones on `+conf+rgb` does not leave comfortable room on one.

{: .note }
**There is no longer a Depth grid picker.** It was removed on 2026-10-27,
because the format selector in the capture code accepted the target and
deliberately ignored it: the phone captured and sent 256×192 whatever the
picker said. A control that does nothing is worse than no control, because it
gets planned against. The key still exists, is reported in telemetry and rides
in a profile, but it is not a bandwidth or thermal lever.

### Capture rate

The rate the renderer is asked for. It applies live, with no capture restart.

A thermal ladder can lower it on top of the chosen rate without overwriting the
choice, so the phone returns to the chosen rate by itself once it has cooled.
See [Settings](settings.html) for the ladder's own controls.

---

## CAPTURE (goes into the take) and PROCESSING (goes into the take)

These are the same keys the LIVE page shows, deliberately duplicated so that a
take can be set up without leaving this page. Change one and the other moves
with it. They are refused while a take is running.

Both sections are described in full on [the LIVE page](live.html). The captions
here say what each setting means for the file rather than for the stream.

---

## TAKE SETUP

| Control | Default | What it does |
|---|---|---|
| Auto-name takes | On | Names each take from a prefix and a timestamp |
| Prefix | Empty | Replaces the `T<id>` head. Shown with the next name |
| Name | Empty | Used only when auto-naming is off |
| Notes | Empty | Free text stored inside the take's metadata block |
| Compress frames | On | Byte-shuffle and deflate, per frame, lossless |
| Record every frame / 1 frame in N | Every frame | A decimation, 1 to 10 |
| Pre-roll | None | A countdown of up to 30 seconds before the take arms |
| Duration cap | None | Stop after up to 120 minutes |

An auto-name is `T<device id>-yyyyMMdd-HHmmss`, or `<prefix>-yyyyMMdd-HHmmss`
when a prefix is set. Names are sanitised and capped at 64 characters, and a
clash gets a `-2`, `-3` suffix rather than overwriting.

### Compression

Each frame is compressed on its own. Two lossless steps: the f16 depth plane is
split into all its high bytes followed by all its low bytes, and an RGB plane
into separate R, G and B planes; then the result is deflated. A smooth depth
field has near-constant high bytes, and only the low byte carries the sensor
noise, so the compressor sees long runs where before it saw an alternating
pattern.

Because every frame stands alone, seeking, looping and crash recovery stay
cheap.

Ratios against the raw wire bytes, **measured, simulation** (synthetic frames
with the shared-world simulator's noise model):

| Content | Raw LZ4 (the old codec) | Shuffle and deflate |
|---|---|---|
| 256×192 depth+conf | 3.07× | 5.05× |
| 320×240 depth only | 2.41× | 3.79× |
| 256×192 depth+conf+rgb | 4.41× | 6.42× |
| Deliberately harsh depth only, 1 cm uniform noise | 1.50× | 1.90× |

Expect 2× on noisy depth-only content and up to 6× on depth+conf+rgb. The floor
is the sensor: noise in the low mantissa bits is incompressible by any lossless
codec.

Encode cost is about 1.4 to 2.8 ms per frame and decode about 0.2 to 0.4 ms
(**measured, Mac, synthetic frames**). Noisy RGB has been seen at about 7 ms per
frame on a Mac, and a phone is slower. Per-frame encode cost on a real phone at
30 fps has not been measured (**not yet verified**).

Turning compression off writes the wire bytes as they are: the biggest files
and no CPU cost. It is the A/B control.

### Decimation

Recording one frame in N makes a long take at a fraction of the size. Playback
honours the recorded intervals, so a decimated take replays at its reduced rate
rather than being sped up.

### Pre-roll and armed starts

A pre-roll is a countdown on this phone. To start several phones together, the
console sends an armed start over the control port instead. See
[the control surface](ctl.html).

An armed start is a shared-second start, not a frame lock. On a LAN the packet
jitter it adds is sub-millisecond, which is far tighter than the tens of
milliseconds that separate two iPhones' notions of now. Frame-locking several
phones is separate, later work.

---

## STORAGE

| Control | Default | Range |
|---|---|---|
| Free | read-only | |
| Refuse to start below | 2.0 GB | 0.5 to 32 GB |
| Auto-stop a take below | 0.5 GB | 0.2 to 16 GB |
| Keep only the newest N | Keep every take | 0 to 50 |

The free-space figure is the amount the operating system will actually hand
over, not the raw free blocks.

The app refuses to start a take below the first floor, and stops a running take
by itself at the second. An auto-stop writes its reason into the recorder's
status line, and reports it in telemetry.

`Keep only the newest N` runs after a clean stop, never during one.

Takes live in `Documents/Takes`, which means they are visible in the Files app
and over a cable in Finder.

### Disk cost

Write rate at 256×192 and 30 fps, **calculated from the wire format** and then
divided by the compression ratios above:

| Plane set | Uncompressed | Compressed, best case | Compressed, assume this |
|---|---|---|---|
| depth | 3.0 MB/s | 0.8 MB/s | 1.5 MB/s |
| depth+conf | 4.4 MB/s | 0.9 MB/s | 2.2 MB/s |
| depth+conf+rgb | 8.8 MB/s | 1.4 MB/s | 4.4 MB/s |

The best case uses the simulated ratios above. The column to plan with assumes
only 2×, which is what the harshest synthetic noise produced and therefore the
safer assumption for a real stage.

The headroom figure the app shows assumes the same 2×, deliberately, so that
"about N minutes left" never over-promises. No take has yet been recorded on a
real phone and measured against these figures (**not yet verified**).

---

## If the app dies mid-take

The file is still readable. There is no index to lose: a reader walks the
records by their own length fields from the start of the file, and drops a
truncated final record. That is the entire crash story.

A take closed cleanly carries a footer. A take that was not shows `recovered`
in the library and in its details, and plays normally. At the next launch the
app gives any such take a sidecar so it lists without being opened.

---

## Export and import

### Getting a take off a phone

PLAYBACK page, tap the take, then **Export**. That is the standard iOS share
sheet, so any of these work:

- AirDrop to a computer or another phone. Fastest for multi-gigabyte files.
- Save to Files, then a cloud folder or a drive.
- Mail or Messages, for short takes.
- A cable: Finder, the phone, Files, TDStage, Takes. Drag the `.tdp4rec` out.
  The `.json` beside it is optional.

Export is disabled while that take is being written, because a copy of a file
the writer still holds would be torn.

Send the whole file untouched. Do not zip individual takes, since they are
already compressed, and do not change the extension.

### Getting a take onto a phone

Either:

- **Open it.** Tap a `.tdp4rec` in Files, Mail or AirDrop and choose this app.
- **Import.** PLAYBACK page, **Import**, then pick one or more files.

Both routes land in the same code. It validates the file before copying it,
refuses junk, short-circuits a file that is already in the Takes folder, and
rebuilds the sidecar from the file itself. The copy and the index walk run off
the main thread, because a take can be gigabytes.

The outcome appears as a line of text on the PLAYBACK page, and the last take
imported becomes the selected one, so AirDrop and then Play is two gestures.

Opening several files at once delivers them one at a time. They are folded into
one queue rather than imported concurrently, and the page says how many are
waiting.

Refusals, in the app's own words:

| Message | Meaning |
|---|---|
| could not read the file | The source could not be opened at all |
| not a TDStage take (.tdp4rec) | No valid header |
| the take has no readable frames | A valid header with nothing in it |
| copy failed: … | The destination write failed, for the stated reason |

A take whose format version is newer than the installed build is refused up
front rather than half-played.

Both this app and its ARKit sibling export one file type under one identifier,
with byte-identical declarations, so "Open in" works for either.
