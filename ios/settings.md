---
title: Settings reference
parent: iOS app
nav_order: 5
---

# Settings reference

Every setting the app holds, with the key it is stored under, its default, what
it does, and whether a console can set it remotely.

All settings live in iOS UserDefaults under keys beginning `stage.`. Every
default is registered once at launch, and every reader goes through
UserDefaults with no inline fallback, so a fresh install and a reset agree.

## How to read the Remote column

This is the column that matters, because remote control is how a console drives
a phone across a stage.

| Remote | Meaning |
|---|---|
| **`set` number** | `/tdlidar/ctl/set <key> <number>` reaches it. The value is clamped as stated |
| **`set` text** | `/tdlidar/ctl/set <key> <string>` reaches it. Text is trimmed and validated |
| **verb** | A dedicated control address also exists. See [the control surface](ctl.html) |
| **profile** | Only a whole pushed profile document can change it |
| **no** | No remote path exists. Either the phone sets it, or a person does on the phone |

Two authorities, deliberately at different trust levels. `/ctl/set` is a narrow,
numerically clamped, per-key surface. A profile is a whole document applied in
one go, and it is the only way to re-point a phone's identity or its ports. A
key the profile schema does not list is dropped, so a profile cannot reach
anything below that does not say `profile`.

{: .note }
Every setting a person can change on the phone's screens is reported back at
2 Hz as a JSON object on `/tdlidar/<id>/device/settings`, keyed by these same
UserDefaults keys. That is how a console shows the phone's real state rather
than the last value it happened to send. A key absent from that object is a
control the app does not have, and the console hides that row.

An unknown key sent to `/ctl/set` is ignored. Nothing writes arbitrary
UserDefaults.

---

## Identity and network

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.deviceId` | `1` | profile | The device id stamped into every packet and into the telemetry namespace. Must be unique across the rig. The stepper on the LIVE page is 1 to 9 |
| `stage.deviceIdSet` | `false` | no | Has a person ever chosen the id on purpose. While this is false *and* the id is still 1, START is refused |
| `stage.tcpHost` | `""` | `set` text | **The destination IP address.** A legacy key name: it is not a transport. The depth stream, the telemetry and the control replies all read it. Up to 253 characters |
| `stage.udpPort` | `9003` | profile | Destination port for the depth stream |
| `stage.udpPlanes` | `"depth+conf"` | `set` text, profile | Which planes ride the wire. Only `depth`, `depth+conf` and `depth+conf+rgb` are accepted. Anything else is refused, not coerced |
| `stage.oscHost` | `""` | `set` text | Telemetry destination. Blank means use `stage.tcpHost` |
| `stage.oscPort` | `9000` | profile | Telemetry destination port |
| `stage.ctlPort` | `9010` | profile | The port the phone listens on for commands |
| `stage.preferWired` | `true` | `set` number, profile | Require wired Ethernet for outgoing connections whenever a wired interface is up |
| `stage.hostCable` | `""` | no | The last complete cable address the phone learned. Powers the LIVE page's **Cable** button |
| `stage.hostWifi` | `""` | no | The last complete network address. Powers the **Wi-Fi** button |
| `stage.markerExtrinsic` | empty | no | The last marker calibration solve, as 16 floats. Written by a calibration and cleared by `/ctl/calibclear` |

{: .warning }
`stage.tcpHost` and `stage.oscHost` are deliberately **not** in the profile
schema. Which link a phone uses is the operator's choice, and nothing may
override it. A cached profile is re-applied at boot and on a full self-heal: if
a host lived in that document, pressing **Cable** and then taking a heal a few
seconds later would walk the phone back onto Wi-Fi on its own. An explicit
`/ctl/set stage.tcpHost` still works, because that is a person at a console
deciding.

In practice an operator does not send that by hand. Pressing **Send telemetry
here** on the console's device row sends the address over the control channel,
which is the supported way to point a phone at a machine. The phone's own
on-screen advice names the same button.

`stage.hostCable` and `stage.hostWifi` are the only two keys with no registered
default. They read as empty until the phone learns an address.

---

## Capture

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.targetFPS` | `30` | `set` number (5 to 60), verb `fps`, profile | The capture rate asked of the renderer. Applies live. The RECORD page's stepper moves in fives |
| `stage.depthgrid` | `"256x192"` | `set` text, verb `depthgrid`, profile | Requested depth-grid size. Accepts `WxH`, `max`, `min` or a bare width, each number from 16 to 4096 |
| `stage.depthfilter` | `false` | `set` number, verb `depthfilter`, profile | Apple's temporal and spatial depth smoothing with hole fill. **Must stay off for a show.** Changing it restarts the capture session |
| `stage.colorEnabled` | `true` | `set` number, profile | Build a colour grid at all. With this off, the RGB plane is dropped even if the plane set asks for it |
| `stage.stabilization` | `0.3` | `set` number (0 to 1), profile | **This app ignores it.** Kept so that one profile document serves both this app and its ARKit sibling, which does read it |

{: .warning }
`stage.depthgrid` is inert on the show path. The format selector accepts the
target and deliberately ignores it, so setting this value changes nothing about
the grid that is captured or sent. It is still stored, reported and carried in
a profile. A change is refused while a take is recording, because a take is one
file with one geometry in its header.

---

## Processing

The phone is a pure streamer. These exist so each optional stage can be
switched on for a measurement.

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.rawmode` | `true` | `set` number, verb `rawmode`, profile | **The master switch.** On: acquire depth, pack, send. The three keys below are force-skipped whatever they say |
| `stage.lensrect` | `false` | `set` number, verb `lensrect`, profile | Static lens-distortion rectification of the depth grid. A per-frame resample of every cell on the phone. The receiver does this better |
| `stage.markers` | `false` | `set` number, verb `markers`, profile | On-phone marker detection at about 3 Hz. Forces a colour render at its own cadence, so it is never free. A calibration turns it on implicitly |
| `stage.skeleton` | `false` | `set` number, verb `skeleton`, profile | On-phone person and pose detection. Its results have no wire, so this is a cost measurement only |
| `stage.flipZ` | `true` | `set` number, profile | Negates Z for the receiver's convention. **Read only by the on-phone pose engine**, which has no wire, so it has no effect on what is streamed |

All of the first four apply live, with no capture restart.

---

## Geometry and show behaviour

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.mountedge` | `0` | `set` number (0 to 2), profile | Declared sky side: 0 automatic, 1 left edge up, 2 right edge up. Consulted only when gravity is degenerate, which happens when the camera stares straight down or up. Also rides the hello and the telemetry |
| `stage.showActive` | `false` | no | Auto-resume streaming on launch. START sets it, STOP clears it. A profile's own `autoStart` field is what a console pushes instead |
| `stage.thermalLadder` | `true` | `set` number, profile | Let the frame-rate ceiling drop when the phone is hot. Off holds the configured rate |
| `stage.thermalSeriousFPS` | `25` | `set` number (5 to 60) | The ladder's `serious` rung, in absolute fps |

The ladder only ever lowers the rate, on top of the operator's choice, without
overwriting it. The phone returns to the chosen rate by itself once it has
cooled. It acts on the worse of the device thermal state and the capture
system's own pressure.

---

## Recovery

No remote path exists for any of these. They are not in the `/ctl/set`
whitelist and they are not in the profile schema, so today they can only be
changed by editing the app's stored defaults, which no screen does
(**not yet verified** in operation).

| Key | Default | What it does |
|---|---|---|
| `stage.recovery.enabled` | `true` | Master switch for the in-process watchdog |
| `stage.recovery.stallSeconds` | `4.0` | Streaming but no frame for this long, then self-heal |
| `stage.recovery.linkSeconds` | `12.0` | Streaming but transport down this long, then re-dial |
| `stage.recovery.allowExit` | `false` | Allow the last-resort tier, which quits so a supervised phone relaunches. Only meaningful under Single App Mode |
| `stage.recovery.crashLoopCount` | `3` | This many unclean boots, inside the window below, means safe mode |
| `stage.recovery.crashLoopWindow` | `240.0` | The window, in seconds |
| `stage.recovery.safeMode` | `true` | Honour the crash-loop floor at all |
| `stage.recovery.profileURL` | `""` | An optional URL to refresh the profile from at boot |

### What safe mode forces

After repeated crashes, a boot ignores the profile for these keys and runs the
cheapest possible frame path. If the phone is dying repeatedly, the app stops
reproducing the configuration that killed it.

```
stage.rawmode      true
stage.lensrect     false
stage.markers      false
stage.skeleton     false
stage.colorEnabled false
stage.depthfilter  false
stage.udpPlanes    "depth"
stage.depthgrid    "256x192"
stage.targetFPS    30
```

A phone in safe mode says so in its telemetry, and a console operator can clear
the crash history with `/tdlidar/ctl/reset`.

---

## Recording

None of these are in the profile schema, deliberately. A pushed show profile
must never arm or disarm a recorder, or point a phone at a different take
during a get-in.

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.rec.compress` | `true` | `set` number | Byte-shuffle and deflate each frame, losslessly |
| `stage.rec.frameDivisor` | `1` | `set` number (1 to 30) | Record one frame in N. The stepper on the phone offers 1 to 10 |
| `stage.rec.maxMinutes` | `0.0` | `set` number (0 to 240) | Hard duration cap. 0 means until the disk floor. The stepper offers 0 to 120 |
| `stage.rec.minFreeGB` | `2.0` | `set` number (0 to 64) | Refuse to start a take below this. The stepper offers 0.5 to 32 |
| `stage.rec.autoStopGB` | `0.5` | `set` number (0.1 to 32) | Stop a running take below this. The stepper offers 0.2 to 16 |
| `stage.rec.preroll` | `0.0` | `set` number (0 to 30) | Countdown seconds before Record arms |
| `stage.rec.autoName` | `true` | `set` number | Name takes from a prefix and a timestamp |
| `stage.rec.namePrefix` | `""` | `set` text | Replaces the `T<id>` head of an auto-name. Capped at 64 characters |
| `stage.rec.notes` | `""` | `set` text | Free text stored in the take's metadata block. Capped at 500 characters |
| `stage.rec.keepLast` | `0` | `set` number (0 to 200) | Keep only the newest N takes. 0 keeps everything. The stepper offers 0 to 50 |

Take names never travel through `/ctl/set`. They arrive on the dedicated
recording verbs, so a name cannot be mistaken for a number.

---

## Playback

| Key | Default | Remote | What it does |
|---|---|---|---|
| `stage.rec.loop` | `true` | `set` number, verb `rec/play` | Loop a replay |
| `stage.rec.loopGapMs` | `0.0` | `set` number (0 to 10000) | Gap between loops. The stepper offers 0 to 5000 |
| `stage.rec.speed` | `1.0` | `set` number (0.05 to 4), verb `rec/play` | Scales the recorded intervals |
| `stage.rec.extMode` | `0` | `set` number (0 to 2) | Pose sent with the take: 0 as recorded, 1 the phone's current pose, 2 identity |
| `stage.rec.rewriteTime` | `true` | `set` number | Rewrite each frame's capture time to now, so the frame clock keeps moving forward |
| `stage.rec.planeKeep` | `7` | `set` number (1 to 7) | Plane filter applied before sending: 1 depth, 2 confidence, 4 colour. Depth is always kept |
| `stage.rec.playDeviceId` | `0` | `set` number (0 to 99) | Replay under another device id. 0 means this phone. The stepper offers 0 to 9 |
| `stage.rec.resumeLiveAfterPlay` | `false` | `set` number | Restart the camera when a replay stops |
| `stage.rec.netOverride` | `false` | `set` number | Send replays somewhere other than the live destination |
| `stage.rec.host` | `""` | `set` text | The override host. Blank follows the live host |
| `stage.rec.port` | `9003` | `set` number (1 to 65535) | The override port |

Every playback key reaches a replay that is already running. None of them needs
a restart.

---

## Two safety rules the remote surface enforces

**Non-finite numbers are dropped.** A NaN or an infinity is a legal value in an
OSC float, and used to crash the phone on the integer conversions behind these
keys. One stray console value, one dead phone. Non-finite values are now
dropped, and the rest are bounded before any key sees them.

**A missing argument on a processing toggle means off, never on.** A stray
pulse from a mistyped control must not switch depth rectification or on-device
pose detection back on during a show. The one exception is the master switch:
turning raw mode on *is* doing less, so a bare pulse arms the fast path rather
than disarming it.
