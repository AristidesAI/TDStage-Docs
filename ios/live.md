---
title: The LIVE page
parent: iOS app
nav_order: 2
---

# The LIVE page

LIVE is the page you use when you mount a phone and when you need to know why
a phone is not reaching the receiver. It shows what the phone is sending, where
it is sending it, and what is wrong with the link.

The app has three pages. A glass pill at the bottom of the screen switches
between LIVE, RECORD and PLAYBACK. The pill carries a coloured dot: red while a
take is recording, green while a take is replaying, orange while a start is
armed. Nothing else on the pill changes, so the three shapes stay in the same
places in the dark.

Everything on this page is UDP. There is no TCP mode and no TCP fallback.

{: .note }
The field labelled **TD/Mac Host** is stored under the UserDefaults key
`stage.tcpHost`. That key name is historical. It holds the **destination IP
address** and says nothing about transport. The TCP streamer was deleted from
the app.

---

## The header: START and STOP

Top left shows the app name and `Device <n>`, the device id this phone stamps
into every packet.

Top right is one button:

| Button reads | Phone state | Pressing it |
|---|---|---|
| START (green) | idle | Starts LiDAR capture and the point stream |
| STOP (red) | streaming | Stops the point stream. The socket stays up |
| START (grey) | device id never set | Refused. See below |

STOP stops the point flow only. The UDP socket stays open and the phone keeps
sending its hello every two seconds, so a receiver still sees the phone on its
roster. Telemetry keeps running.

The screen does not auto-lock while the app is in the foreground, whether the
phone is streaming or stopped. A locked phone cannot hear remote commands, so
the app holds the idle timer off from launch.

### The red "Set a unique Device ID" banner

A fresh install carries device id 1 and a flag saying nobody has chosen it.
While that flag is unset and the id is still 1, START is refused and a red
banner appears above the stats. Two phones on one id overwrite each other's
frames.

Three things clear it, and any of them counts even if the number does not
change:

- the **Device ID** stepper further down this page,
- the banner's own **This is phone 1** button,
- a device id pushed from the console.

The refusal also goes out as telemetry, so a console operator who pressed Start
sees the reason rather than silence.

---

## The stats row

Five figures across the top, refreshed twice a second. They are health, not
signal: the app deliberately does not update them per frame.

| Stat | Reads | Notes |
|---|---|---|
| FPS | Measured delivery rate | Blank when nothing is streaming. During a replay it is the replay's rate |
| POINTS | Valid depth cells in the last frame sent, in thousands | Counted by the packer. Not the grid size |
| UDP | OFF, CONNECTING or LIVE | Local socket state only. See the caveat below |
| MARKER | Last marker id seen, or blank | Green while a marker is in view |
| THERMAL | OK, WARM, HOT or CRIT | The device thermal state |

{: .warning }
**UDP LIVE does not mean anything is arriving.** A UDP socket reaches ready
with no receiver in existence, because there is no handshake to fail. It proves
a local socket was created. Only the console or TouchDesigner can confirm
frames are being received.

Under the stats row, one line describes the stream itself:

```
TDP4/UDP → 192.168.0.23:9003 · 256×192 · 41203 frm · 128744 pkt · 0 drop
```

The grid size appears once the first captured frame has revealed it. `drop`
counts frames the phone abandoned because a newer frame arrived while the older
one was still queued. Latest wins, by design.

If the app has an error to report, it appears in red at the bottom of this card.

---

## Mount captions

A thin `▲ THIS WAY UP ▲` caption runs along each long edge of the screen. The
interface is portrait locked, but phones are usually mounted rotated 90 degrees,
because the depth sensor's wide axis runs along the phone's long side.

Tap the caption on the edge that is pointing at the sky. It goes white. Tap it
again to clear it, and both captions go dim, which means automatic.

The selection is only consulted when gravity cannot decide, which happens when
the camera stares straight down or straight up. Real gravity stays
authoritative everywhere else. The declared edge also rides the hello and the
telemetry, so a receiver knows what the operator declared.

---

## NETWORK

### This device

The phone's own LAN address, with a refresh button. Read it out when a console
operator asks for it. Tap and hold to copy.

### TD/Mac Host

The destination IP address for the depth stream, the telemetry and the control
replies. Type four numbers separated by dots. Names are not resolved on this
path.

While the field has focus the button beside it reads **Done**. Otherwise it
reads **Connect**. Either one pushes the edited address into the live streamer.

The field writes on every keystroke, so a half typed address is normal while
you are typing. Only complete addresses are remembered for the Cable and Wi-Fi
buttons.

### Link

A read-only label saying which interface the depth stream is actually using,
followed by two buttons.

| Label | Meaning |
|---|---|
| USB cable | The destination is a `169.254.x` address and a cable is attached |
| cable missing | The destination is a cable address and no cable is attached. Nothing can leave |
| Ethernet | The stream left on a wired interface, which is what a PoE rig wants |
| Wi-Fi (Ethernet waiting) | Wired is up and preferred, but the stream is on Wi-Fi |
| Wi-Fi (Ethernet idle) | Wired is up but not preferred |
| Wi-Fi (cable idle) | A cable is attached but the stream is on Wi-Fi |
| Wi-Fi | Wi-Fi, no wired interface |

**Cable** and **Wi-Fi** switch the destination between the last complete cable
address and the last complete network address, so an operator does not retype
an address at a get-in. Each button is disabled when there is nothing to switch
to.

The phone cannot work out the computer's cable address by itself. Both ends of
a USB-C link pick a random `169.254.x` address, and iOS blocks the broadcast
that would discover the other end. The phone learns the address from the source
of the first control packet it receives, which is why the console has to send
to it once before the Cable button lights up.

A caption under the buttons explains any disabled state, rather than leaving a
dead button with no reason.

### Prefer Ethernet (PoE / cable)

On by default. While it is on and a wired interface is up, every outgoing UDP
connection requires wired Ethernet. If the wired link drops, the next attempt
is built without the requirement and goes out over Wi-Fi. When it comes back,
the streamer reconnects onto it.

Cellular is never used for show traffic.

Wi-Fi costs roughly 8 ms and adds jitter against roughly 0.55 ms on a cable
(**measured, real phone (one phone)**). Leave this on for a cabled rig.

### UDP Port

The destination port for the depth stream. Default 9003.

### Device ID

A stepper, 1 to 9. The id is stamped into every packet and into the telemetry
namespace, so it must be unique across the rig. Stepping it counts as a
deliberate set and clears the fresh-install guard.

Changing it re-points the stream, the hello and the telemetry together.

### Blackout, Calibrate, and the control port

Three controls on one row.

- **Blackout Screen** sets the screen brightness to zero and hides the status
  bar. The page itself is not drawn at all while blacked out, so it stops
  consuming power on a screen nobody can see. A tiny dot in the top right
  corner stays lit: green when the socket is up, red when it is not, red while
  recording, green while replaying. Triple-tap anywhere to wake the screen.
  **Wake Screen** restores the previous brightness.
- **Calibrate** swaps the rear LiDAR from the capture path to ARKit marker
  tracking. The two cannot share the sensor, so this is a hard swap: the point
  stream stops. Pressing **Stop Calibrate** stores the solved pose and resumes
  streaming if the phone was streaming before. While calibrating, a line below
  reports the translation jitter in metres and how many markers have been seen.
  When a stored calibration exists, the line reads `Stage extrinsic locked`.
- `ctl :9010` is the port the phone listens on for remote commands. It is not
  editable here.

Marker calibration works end to end in the code and has unit tests. It has not
been confirmed on a phone against a printed marker (**built, not verified**).

#### What the phone sends when it is not calibrated

The phone always stamps a pose into every frame. Without a marker calibration
that pose is the gravity levelling rotation, so the cloud arrives level at any
mounting angle. The "calibrated" bit in the frame stays false. Receivers apply
the pose as given either way.

---

## Link diagnostics

Every problem with the link, worst first, each with the evidence and a concrete
next action. Problems are always visible. The healthy checks are hidden behind
the **All** button, because a screen of green ticks is how a real fault gets
missed. The header says `all clear` or `N to fix`.

The findings the app can raise:

| Finding | Level | Raised when |
|---|---|---|
| No network interface | error | No usable IPv4 interface at all |
| No destination set | error | The host field is empty |
| Destination is not a valid address | error | The host field is not a dotted quad |
| Pointed at a cable address with no cable | error | Destination is `169.254.x` and no cable interface is up |
| Cable address looks stale | error | Sending to a cable address is producing errors |
| Transport errors (n) | error | The socket reported send errors |
| Not listening for commands | error | The control listener is down |
| No USB cable | warn | Wi-Fi only |
| Cable attached but the Mac's cable address is unknown | warn | A cable is up and the phone has never been told the far address |
| Streaming over Wi-Fi with a cable attached | warn | A cable address is known and unused |
| No commands received yet | warn | Nothing has ever sent to the control port |
| Telemetry is going to port 9000 | warn | See below |
| Telemetry and depth point at different hosts | warn | Deliberate when the hub and the console are different machines |
| USB cable attached | ok | |
| Sending n frames, no errors | ok | With the UDP caveat stated in the detail |
| Last command from a.b.c.d | ok | This is how the phone learned where the console is |

{: .note }
**The port 9000 warning matters.** TouchDesigner binds 9000. With the hub
running, a console listening elsewhere never sees a telemetry packet and shows
the phone offline while it streams perfectly. The console has a button that
moves the phone to the console's own listen port.

A cable address is not stable. The far end re-assigns its `169.254.x` address
whenever the link is re-established, so a remembered cable address goes out of
date on a replug. Re-learn it from the console rather than retyping the old
one.

---

## PROCESSING (off = fastest)

The phone is a pure streamer. This panel exists so each optional stage can be
switched on for an A/B measurement, not because a show needs any of them.

**Raw Streamer Mode (master)** is on by default. While it is on, the frame path
is acquire depth, pack, send, and the three toggles below it are skipped
whatever they say. They are greyed out to make that visible rather than
silently ignored. The caption under the switch says which state you are in.

| Toggle | Default | What it does |
|---|---|---|
| Raw Streamer Mode (master) | On | Skips every optional per-frame stage below |
| Lens rectification | Off | Resamples the depth grid to the ideal pinhole model of the header intrinsics. The receiver does this better |
| QR marker detection | Off | Runs the on-phone marker detector at about 3 Hz. Forces a colour render at its own cadence, so it is never free |
| Skeleton / person detection | Off | Runs the on-phone pose detector. Its results have no wire: this is a cost measurement only |
| Apple depth filtering (keep OFF) | Off | Apple's temporal and spatial depth smoothing with hole fill |

All four of the first group apply live, with no capture restart.

**Apple depth filtering** is not covered by the master switch, because it is a
capture-format setting rather than per-frame work. Changing it restarts the
capture session. Leave it off: the show path wants raw depth, where an invalid
cell is NaN rather than an invented value.

Performer separation happens on the receiver, using the angles between several
phones. No on-device API can do it: one body per device, and world tracking
needs camera motion.

---

## CAPTURE

One toggle.

**Colour** is on by default. It controls whether a colour grid is built at all.
The RGB plane only rides the wire when **Colour** is on *and* the plane set on
the RECORD page includes `+rgb`. With Colour off, the RGB plane is dropped even
if the plane set asks for it.

The capture rate and the plane set live on the RECORD page, because what the
phone sends is also exactly what a take records.
