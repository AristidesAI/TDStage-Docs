---
title: Installing and preparing a phone
parent: iOS app
nav_order: 6
---

# Installing and preparing a phone

Getting the app onto a phone, and the phone onto a rig. Work through this at
base, with internet, days before the phone travels. Several steps cannot be
done at a venue.

## What the phone must be

| Requirement | Why |
|---|---|
| iPhone Pro with LiDAR, iPhone 12 Pro or later | The app streams the rear LiDAR depth. There is nothing to capture without it |
| iOS 26.0 or later | The deployment target. The interface uses iOS 26 glass effects, so iOS 18 cannot run it |
| iPhone, not iPad | The app ships an iPhone slice only, portrait locked |
| Mains power for the whole session | Capture and streaming will flatten a battery |

The app declares ARKit as a required capability, which is what the App Store
uses to gate installation. There is no LiDAR capability key to declare.

---

## Installing from the test build

The app is distributed privately as a test build, not on the App Store.

1. On the phone, install Apple's TestFlight app.
2. Accept the invitation. One invitation per app, per tester.
3. Install the build from inside TestFlight.

### Two things this needs that a venue often cannot give you

- **An Apple Account, signed in on the phone.** TestFlight will not install
  anything without one.
- **Internet.** Not the show LAN. TestFlight talks to Apple. A rig network with
  no route out cannot install or update the app.

Do both at base.

{: .warning }
**Check which build a phone actually has before you trust anything on these
pages.** The invitation shared externally serves at most build 1.0 (3). That
build predates a number of later changes, among them the thermal ladder taking
effect, so a phone installed from the existing invitation today is running
software months behind the current one. The older readiness and remote-test
notes in the source repository predate those changes too, and describe the
build of their date rather than the current build.
<br><br>
Read the build number in TestFlight, or from the phone's own telemetry: it
reports its app name, version, build number and the commit it was built from.
Compare that against the build you believe you are running before you report a
behaviour, and before you conclude anything from a measurement.

### Test builds expire

A test build stops working 90 days after it is uploaded. A production running
for months therefore needs either a re-upload roughly every quarter, or a
distribution route that does not expire.

That decision is open. Do not plan a long run on the assumption that it is
settled.

---

## First launch

Open the app on the phone, with the phone on the network you intend to use.

### Permissions

iOS asks for two things, and both must be allowed.

| Prompt | Why the app needs it | If declined |
|---|---|---|
| Camera | The LiDAR depth stream | Nothing is captured |
| Local Network | Sending depth and telemetry, and receiving commands | **No packets reach the app at all.** The phone appears dead to the console while looking fine on its own screen |

Motion is used to work out how the phone is mounted, so the cloud arrives level
at any mounting angle. Raw motion does not prompt.

{: .note }
A declined Local Network permission is one of the hardest faults to read,
because the phone's own screen looks healthy. If a phone is silent and
everything else checks out, look in Settings, the app's entry, Local Network.

### The device id

A fresh install carries device id 1 and a flag saying nobody chose it. While
that flag is unset and the id is still 1, the app refuses to start streaming
and shows a red banner on the LIVE page. Two phones on one id overwrite each
other's frames, and the symptom is a stream that delivers almost nothing or
delivers corrupt frames.

Give each phone its own id, 1 to 9, before it leaves base. Use the **Device ID**
stepper on the LIVE page, or push it from the console. If the phone really is
phone 1, press the banner's own confirm button: the point is that a person
chose, not that the number changed.

Write the id on the phone's case, or on its mount.

### The destination address

The **TD/Mac Host** field on the LIVE page holds the destination IP address for
the depth stream, the telemetry and the control replies.

{: .note }
That field is stored under the key `stage.tcpHost`. The key name is historical
and means nothing: it holds an **address**, not a transport. Everything this
app sends is UDP. There is no TCP mode, and the TCP streamer was deleted.

Leave the ports at their defaults unless a console tells you otherwise: depth
on 9003, telemetry on 9000, control on 9010.

There is nothing to connect. The phone starts sending when you press START.

A phone can learn the address of a console on a USB cable, but it cannot work
it out alone: both ends of a cable pick a random link-local address, and iOS
blocks the discovery broadcast. The phone reads the address off the first
command packet it receives, so the console has to send to the phone once before
the LIVE page's **Cable** button becomes usable.

---

## Phone settings before it ships to a venue

Do all of these at base. Several of them cannot be undone remotely, and one of
them needs internet.

| Setting | Set it to | Why |
|---|---|---|
| iOS version | Updated, at base, with internet | A venue network may have no route to Apple, and an update mid-get-in costs the slot |
| Automatic app and iOS updates | **Off** | An update restarts the phone and replaces the build during a run |
| Passcode | **Off** | A phone that locks needs a human with hands on it. The console cannot unlock one |
| Auto-Lock | **Never** | Belt and braces. The app holds the screen awake while it is in the foreground, but a system that locks the phone anyway makes it deaf |
| Do Not Disturb, or a Focus that silences everything | **On** | A notification banner over a mounted phone is a light source on stage, and a call takes the camera |
| Low Power Mode | **Off** | It throttles the phone. The app reports its state in telemetry so a console can see it, but it should never be on |
| Wi-Fi networks you do not want | Forgotten | Stops the phone wandering onto a hotel or venue network mid-show |

The app holds the screen awake whenever it is in the foreground, streaming or
stopped, and re-asserts that every time it comes back to the foreground. It
does this because a locked phone cannot hear a command, and every remedy an
operator has is delivered over that control port.

### Blackout, not screen off

Use the app's own **Blackout Screen** on the LIVE page rather than letting the
phone sleep. It sets brightness to zero, hides the status bar and stops drawing
the page, while leaving the phone awake and reachable. Triple-tap to wake it.

A blacked-out phone keeps one tiny dot lit in the top right corner: green when
the socket is up, red when it is not, red while recording, green while
replaying.

---

## Before you call a phone ready

A short check on the phone itself.

1. The LIVE page shows a device id, and the red banner is gone.
2. **This device** shows an address on the network you expect.
3. **TD/Mac Host** is the receiver's address.
4. **Link diagnostics** reads `all clear`, or every remaining item is one you
   understand.
5. Press START. FPS settles, POINTS is non-zero, and the wire line shows frames
   and packets rising with no drops.
6. Blackout the screen, and confirm the console still sees the phone.

Then confirm it from the other end. A UDP socket reaching "live" proves a local
socket was created and nothing else: only the console or the receiver can
confirm that frames are arriving.

---

## Two phones, two apps

There is a second app, built on ARKit, used to A/B the capture path. The two
install side by side and share nothing: not settings, not takes, not a device
roster entry.

Run only one of them at a time on a given phone. Both want the same rear LiDAR
and the same ports.

Takes are interchangeable between them. Both export one file type under one
identifier, with identical declarations, so a take recorded in either app opens
into either app.
