---
title: Installing and preparing a phone
parent: iOS app
nav_order: 6
---

# Installing and preparing a phone

Getting the app onto a phone, and the phone onto a rig. Work through this at
base, with internet, days before the phone travels. You cannot do several of
these steps at a venue.

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
- **Internet, not the show LAN.** TestFlight talks to Apple, so a rig network
  with no route out cannot install or update the app.

Do both at base.

{: .warning }
**Check which app and which build a phone actually has before you trust
anything on these pages.** The two apps are at different places. The ARKit
app's invitation now serves **1.1 (4)**, uploaded on the evening of 2026-11-03
(its 1.1 (3) went up 2026-10-27). This app, TDStage, has not been uploaded
since **1.0 (1)** and has never carried a build 3, so any note or invitation
that mentions "1.0 (3)" is describing the ARKit app's export, not this one.
<br><br>
A phone running TDStage 1.0 (1) predates a number of later changes, among them
the thermal ladder taking effect, so it is months behind the source these pages
describe. The older readiness and remote-test notes in the source repository
predate those changes too, and describe the build of their date rather than the
current build.
<br><br>
Read the version and build in TestFlight, or from the phone's own telemetry on
`/device/app`: it reports its app name, version, build number and the commit it
was built from. That is the authority, because it comes from the running
binary. Compare it against the build you believe you are running before you
report a behaviour, and before you conclude anything from a measurement.

### Test builds expire, and that is the plan

A test build stops working **90 days after it is uploaded**. On 2026-10-30 the
decision was taken to live with that rather than move to the App Store or
Apple Business Manager: the apps stay on TestFlight, **re-uploaded about every
80 days**, through to the premiere in April 2027 ([#16](https://github.com/AristidesAI/TDStage/issues/16)).

Eighty rather than ninety is the whole point of the decision. It leaves ten
days of margin, so a build that fails review, an expired certificate or a week
when nobody is free does not land on a show date.

That commits somebody to at least two more uploads to carry the apps through
the April 2027 premiere (an 80-day cadence from the 2026-11-03 upload lands
them in late January and mid April), each one a bump, an archive, an upload
and the testers accepting it. It is nobody's favourite afternoon, and it is cheaper than the alternatives: the App Store
means review of an app that is not for the public, and Business Manager means
an organisation and its paperwork.

{: .warning }
**The expiry is a show-stopper.** An expired build gives no warning and does
not degrade: the app refuses to launch, on every phone at once, because they
were all uploaded the same day. Treat the re-upload date as a production
deadline.

The phones do not warn themselves: each reports its build's archive date and
age on `/device/built`, and the console's Rig health does the warning, at 75
days, escalating to an error at 85, so the rig tells you before the calendar
does. That warning counts from when the build was **archived**, not uploaded,
so it fires early by however long a build waited before upload. That is
pessimistic on purpose. A build made without the script's stamp (an Xcode
Archive) reports no date and never warns.

### Doing the re-upload

Both apps go together, because a rig running two builds from different weeks is
a debugging problem nobody needs:

```bash
./Support/testflight.sh                      # bump, archive, export the IPA
./Support/testflight.sh --upload             # …and upload it
```

The same script exists in both repositories. Without `--upload` the IPA lands
in `build/export/` for Transporter; with it, three App Store Connect
environment variables have to be set, and they are **Ari's key**, so nobody
else can push the upload button.

Each run stamps the build with its archive date, which is what the phones then
report. `--no-bump` runs the same archive and export without touching the build
number. The script also passes the short git hash of HEAD into the build, as
the `TDStageGitCommit` key in its Info.plist, which the phone reports as the
commit on `/device/app`; when the app source has uncommitted changes the script
says so, because then the hash is not the whole story. An Xcode Archive gets
neither stamp, so that phone reports an empty commit as well as the missing
date described above.

{: .note }
Two signed builds were exported on 2026-11-03, both stamped that date:
**TDStage AR 1.1 (4)** was uploaded that evening, so it stops launching on
2027-02-01 and Rig health starts warning on 2027-01-17. **TDStage 1.0 (2)** is
exported and signed but not uploaded; its ninety days do not start until
somebody uploads it. Both archives predate two app fixes committed later the
same day, the watchdog's 30 s hold on a withheld relaunch and blackout
surviving a relaunch, so a tester on 1.1 (4) still sees a relaunched phone come
back lit.

---

## First launch

Open the app on the phone, with the phone on the network you intend to use.

### Permissions

iOS asks for two things, and both must be allowed.

| Prompt | Why the app needs it | If declined |
|---|---|---|
| Camera | The LiDAR depth stream | Nothing is captured |
| Local Network | Sending depth and telemetry, and receiving commands | **No packets reach the app at all.** The phone appears dead to the console while looking fine on its own screen |

The app uses motion to work out how the phone is mounted, so the cloud arrives
level at any mounting angle. Raw motion does not prompt.

{: .note }
A declined Local Network permission is one of the hardest faults to read,
because the phone's own screen looks healthy. The app's stats come from its own
counters, and a UDP socket reaches ready whether or not anything can leave, so
the phone reports frames and packets rising while nothing reaches the LAN.
Nothing on the phone contradicts it. If a phone is silent and everything else
checks out, look in Settings, the app's entry, Local Network.

### The device id

A fresh install carries device id 1 and a flag saying nobody chose it. While
that flag is unset and the id is still 1, the app refuses to start streaming
and shows a red banner on the LIVE page.

Two phones sharing an id wreck each other's frames. The id is in the packet
header of every datagram, and a receiver reassembles fragments per
`(device id, frame id)`, so two phones on one id look to the receiver like one
stream whose packets interleave, and it assembles frames from two phones'
halves. The symptom is a cloud that delivers almost nothing, or geometry that
cannot exist, and it reads like a hardware fault. Hence a refusal rather than a
warning.

The guard is on the *flag*, not on the number, so phone 1 is reachable: the
banner's own confirm button clears it without changing anything.

The refusal is reported as well as shown. The phone writes `START refused:
Device ID N was never set on this phone` to its `/device/rec/note` telemetry, so
a Start pressed in the console is answered with the reason rather than with
silence. Setting or confirming the id clears the note.

Give each phone its own id, 1 to 9, before it leaves base. Use the **Device ID**
stepper on the LIVE page, or push it from the console. If the phone really is
phone 1, press the banner's own confirm button: the point is that a person
chose, not that the number changed.

The stepper applies the network settings the moment the number changes, so
changing the id on a phone that is already streaming re-points the stream and
the telemetry namespace at once, with no stop and start.

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

Nobody types the phone's address into the console either: it learns one from
the source address of the telemetry the phone sends it. The phone also
advertises its control listener over Bonjour as `_tdlidar-ctl._udp`, so a
receiver on the same network that browses for that service finds every phone
and its control port. [The control surface](ctl.html) has the listener's
details.

A phone can learn the address of a console on a USB cable, but it cannot work
it out alone: both ends of a cable pick a random link-local address, and a
discovery broadcast needs an entitlement the app does not have. The phone reads
the address off the source of a command packet that arrives over the cable, so
the console has to send to the phone once (its **Send telemetry here** button) before the
**Cable** option in the LIVE page's Link picker points anywhere.

Cable is one of four choices in that picker: Auto, Ethernet, Cable and Wi-Fi,
with a **Prefer Ethernet (PoE / cable)** toggle shown under Auto only. The
Ethernet choice, for a phone on a PoE adapter, learns the show machine's address
the same way, from a command packet's source address, and until it has one the caption
under the picker says what is missing: no Ethernet adapter with an address, or
Ethernet up but the show machine's address on it unknown, with the console's
**Send telemetry here** or a typed TD/Mac Host as the fix. [The LIVE
page](live.html#link) describes each choice and what the Link line then reads.

---

## Phone settings before it ships to a venue

Do all of these at base. You cannot undo several of them remotely, and one of
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

A blacked-out phone keeps one tiny dot lit in the top right corner. The
recorder's colour wins over the socket's: red while recording, green while
replaying, orange while a start is armed, and otherwise green when the socket
is up and red when it is not. A blacked-out phone that is quietly recording
still says so.

Blackout is remembered, under `stage.blackout`: a phone that auto-resumes
after a crash, a reboot or a watchdog relaunch goes dark again if it was dark
when the app died, while a phone you open by hand at the stand comes up lit.
The console's half of this, which builds carry the fix, and what to do on the
builds that do not, are under
[a phone's app crashes](../operations/failure.html#a-phones-app-crashes-or-is-killed).

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
install side by side and share nothing on the phone: not settings, not takes.
The console's roster is keyed by device id, so whichever app streams with a
given id fills that row.

Run only one of them at a time on a given phone. Both want the same rear LiDAR
and the same ports.

Takes are interchangeable between them. Both apps also expose their
`Documents/Takes` folder in the Files app and in Finder over the cable
(`UIFileSharingEnabled` in each `Info.plist`; this app also sets
`LSSupportsOpeningDocumentsInPlace`), which is how a take leaves a phone at a
get-in with no build and no cable tool; the steps are on [the RECORD
page](record.html#getting-a-take-off-a-phone). Both export the take type under one
identifier, `aristides.lintzeris.tdstage.take`, with the same conformances,
description and filename-extension tag, so a take recorded in either app opens
into either app.

The two declarations are **semantically** identical rather than byte-identical.
The keys appear in a different order in the two `Info.plist` files, and the
ARKit app declares a second type, `aristides.lintzeris.tdstage.imu`, for its
IMU sidecar. Neither difference affects "Open in", which matches on the
identifier and the extension tag. What would break it is changing the
identifier, the tag or the conformances in one app and not the other.
