---
title: The Stroud running plan
parent: Operations
nav_order: 16
---

# The Stroud running plan
{: .no_toc }

Tracking at Brunel's Goods Shed, 24 to 26 November 2026.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

**Version 2, 17 November 2026**, written against the code on `main` at
`beaa18f` and tox v95. Version 1 was written on 10 November against an older
commit; everything below has been re-checked against the code since, and the
figures that moved are marked. Questions for the Default Ltd team are in the
open list at the end; answers can go on the project's issue tracker or by
email.

**For** the Default Ltd team on site at Stroud and for the remote operator in Sydney. It says
who does what, when, with which kit, and what to do when something fails.

**Read this first.**
- **Nothing in this system has run on a stage.** No stage test has taken place: the Sydney
  three-phone test has not run, and the London session of 18 November is a dry run of the
  procedure, not a measurement of the rig. Stroud is the first time the whole system runs
  together in a venue: six phones, the Windows show PC and the client's content. Every number
  below carries an evidence label (next list) so you can see how far it is proven.
- **The code this plan describes is on `main` at `beaa18f`,** and the show laptop runs
  TouchDesigner 2025.33230 with tox v95. The padlock now locks phone placements for every
  browser and program rather than one tab, the console refuses to apply a clouds alignment
  graded WARN, and the bridge and console windows on Windows switch off QuickEdit so a stray
  mouse drag cannot pause them [simulated: that code has not been run in a Windows console
  window, and Edit > Mark from the window menu still selects and still pauses]. TouchDesigner also refuses "Solve Level" and "Set Floor To
  Origin" while the console places the phones. The release line (section 1.4) names the exact
  versions the PC leaves London with.
- **What is still open is written as [to be filled after the 18 November session].** No figure
  is invented to fill one.
- **Windows CI has not run since 10 November,** so nothing in this plan has been re-checked on
  a Windows runner since that date. Everything marked as checked on a Mac was checked on a Mac.
- **Times.** Stroud is on GMT (UTC+0). Sydney is on AEDT (UTC+11), 11 hours ahead. Every
  time is given in Stroud time with Sydney time beside it: the tables have a column for each,
  and in the text Sydney is in brackets, for example 09:00 (20:00 Syd).
  The times are proposals: the site lead sets the real call times.

**Evidence labels** used in this plan (as in `Notes/System-Analysis-2026-11-09.md`):

| Label | Meaning |
|---|---|
| measured on rig | Real phones streaming into this system, at home. Does not depend on the room. |
| living room | Real phones placed around one furnished room at home. A room, not a stage. |
| take replay | A recorded phone take played back through the shipped code. |
| simulated | Synthetic phones or scenes, or GitHub's test machines. No live phone in the loop. |
| measured on the development Mac | A script or tool timed on Ari's Mac, not on the show PC. |
| designed | Worked out from the code, a calculation or documentation. Never run on the thing it is for. |
| unknown | Not measured. |

**Words used in this plan.**

| Word | Meaning |
|---|---|
| Show PC | The Windows workstation that runs the tracking (and, in the 20 October Stroud plan, the content). |
| Standby | A second machine, prepared in advance, that takes over if the show PC dies. |
| Bridge | The small program that receives the phones' data and hands it to TouchDesigner and the console. Runs in its own window, titled "TDStage bridge", which starts minimised: you see it only as "TDStage bridge" on the Windows taskbar. |
| Console | The tracking web console (a program in its own window, titled "TDStage Web Console", and its web page at http://localhost:9080). It manages the phones and produces the client outputs. |
| Phone card, side panel | On the console's All phones page each phone has a card (Start, Blackout, Ping). Clicking a card opens that phone's side panel with the rest: Stop, Lock pose, its placement cell and "moved since lock". |
| Start show, Standby | Buttons in the console's top bar that act on every phone at once. Start show starts every phone with its screen dark, checks that each came up and arms Auto-recover (which restarts a phone that is up but not streaming). Standby stops capture on every phone, darkens the screens and disarms Auto-recover. |
| TD, tox | TouchDesigner, and the TouchDesigner component file (`TDStageConductor.tox`) that fuses the phones into one point cloud. |
| Show .toe | The TouchDesigner project file prepared in London: the tox inside, its switches already set (1.4). It is the file the operator opens. |
| /track | The tracking stream to the client's software: performer positions, hands, ids (OSC over UDP, port 7000, data contract F1 v0.3). |
| F1 0.4 | The second client stream: occupancy field, presence and sensor poses over a WebSocket on port 9001. |
| NDI | A video-over-network format. The console can send a rendered view of the point cloud as an NDI source. |
| PoE | Power over Ethernet: one network cable carries both power and data to each phone. |
| UPS | Uninterruptible power supply: a battery that keeps the show PC, switch and router on through a power blip. |
| Padlock | The lock button at the top right of the console page. While on, the console refuses every change to its phone placements (edits, layouts, applied alignments, Undo, Push poses) from any browser or program, and the locked browser page itself sends nothing. A marker calibration sent to a phone would still change that phone's placement in TD, so none is sent while locked. |
| Anchor phone | The phone whose taped position defines the stage coordinates. Every other phone is placed relative to it. |
| Align | Software placing each phone in stage coordinates from what the phones see. |
| Background learn | TD and the console record the empty stage so that walls, set and screens are not mistaken for people. |
| Spot check | A person stands on the stage centre (O); the console reports how far the phones' agreed position of them is from O. |
| O, G0, S0 | O: stage-floor centre, origin of all coordinates. G0: the floor point under the middle of the gauze. S0: the same under the grey screen. |
| Take | A recording made on a phone: exactly what the phone streamed, replayable later. |
| Snapshot | A copy of all code, settings and learned state, made by `Tools/backup_state.sh`, from which the standby is refreshed. |
| Preflight | A go / no-go checklist program (`Tools/phone_session.py --preflight`) that checks every phone and the console. Each line reads PASS, WARN (look at it) or FAIL (blocks, unless Ari accepts it in the chat: 5.2 step 12). |
| OK, WARN, FAIL (alignment) | The grade the alignment gives each phone: OK is a clean match; WARN means it is unsure, and a WARN has been badly wrong in simulation. |
| UDP, OSC | UDP: the network message type every phone stream uses; each packet is sent once with no resend, so a lost packet costs one frame from one phone. OSC: a message format sent over UDP, used by /track. |
| DHCP | The router handing out network addresses to the phones. |

**Coordinates.** The client contract of 3 September fixes metres, Y up, and the origin O on the
floor at the centre of the performance area. The directions come from the console's stage frame
(the coverage study, `Notes/Stroud-Coverage-Layout.md`): +Z points toward the gauze, -Z toward
the grey screen, and +X is your right when you stand at the gauze facing the screen. The z sign
on /track is confirmed with the content lead in 8.2 step 4.

---

## 0. At a glance

| Day | Stroud (GMT) | Sydney (AEDT) | What happens (from the Stroud plan of 20 October) | Tracking work |
|---|---|---|---|---|
| From about 19 Nov | London | | Show PC and network built and tested in London | Acceptance kit, remote access, phones installed, standby prepared (2.1) |
| Tue 24 | 08:00-18:30 | 19:00 Tue - 05:30 Wed | Set-up: screens, projectors, phones, network, calibration, lighting; technical rehearsal without performers | Get-in (2.2) |
| Wed 25 | 08:00-18:30 | 19:00 Wed - 05:30 Thu | Performers from the morning: interaction scenarios, three layers, lighting tests, recordings | Performer day (2.3) |
| Thu 26 | 08:00-17:30 | 19:00 Thu - 04:30 Fri | Performers: refine, compare gauze options, record; review; pack down | Performer day, then pack-down (2.4) |

The plan assumes **six phones in two side rows of three**. The shape was settled with the
client on the call of 27 October and confirmed in his email of 28 October (the coverage study's
`study_6` layout). The count of six is still formally open: it is what we proposed and what the
client's email says he is buying for, and the decision waits on a measured body range. Six is the count the coverage model supports and nothing else: at a 5 m body range it
leaves 4 per cent of the volume unseen and 58 per cent in two or more views, and three
12 Pro Max among the six make that 6 per cent and 54 per cent [simulated]. **No measured body
range exists**, so the count rests on the model alone: [to be filled after the 18 November
session: the measured range per phone model]. Phones bought for the rig should be of the
16 Pro or 17 Pro class rather than older ones, because the narrower lens of a 12 Pro Max costs
coverage. Eight phones fit the gigabit link on the ARKit grid (4.4) but need a new layout, a
TouchDesigner Commercial or Pro licence (open question C6), and at that count the switch is the
untested part: the one in the kit list publishes 192 KB of buffer for the whole switch, less
than one colour frame, and the arithmetic puts a colour phone in an overflowing pair 24 % of
the time at six phones and 32 % at eight [calc].

---

## 1. Roles, talking, remote access

### 1.1 Roles

Names are for Default Ltd to fill in (open question C1). One person can hold more than one
role outside performer sessions; during a performer session the stand runner should not also
be the operator.

| Role | Who | Does | Does not |
|---|---|---|---|
| **Site lead** | Default Ltd | Owns the schedule, the venue and the performers' consent. Decides whether a session stops for a fix. The one voice for the client side. | |
| **Tracking operator** | On site, named by Default Ltd; ideally the same person all three days | Runs the show PC, the console page and TouchDesigner's few switches in this plan. Keeps the log in the group chat. First responder on every failure card. Runs the end-of-day backup. | Change settings, phone placements or TouchDesigner beyond this plan without Ari. Install or update anything on the show PC. |
| **Stand runner** | On site; within reach of the stands during every performer session | Relaunches a phone app, re-seats a cable or adapter, puts a knocked phone back on its marks. Keeps people and equipment off the stands. | Adjust a stand, a clamp or a phone for any other reason. |
| **Content lead** | Client side: whoever runs the real-time content | Confirms the client outputs (section 8). Reports anything odd in the tracking as seen in the content. | |
| **Remote engineer** | Ari, in Sydney | Runs the alignment and the checks remotely, reads the console, decides settings, guides every failure card, writes the reply to each day's handover. | Touch the show PC's desktop without telling the operator. |

Staffed stands are this plan's answer to issue #44 (a crashed or rebooted phone stays down
until someone opens the app). No decision on #44 is recorded; if Default Ltd chooses
supervised phones in Single App Mode instead, the stand runner's relaunch step changes.

### 1.2 How we talk

- **Group chat (one thread for the whole test).** Every reading, alarm, failure and fix goes
  in with its time. The handover (section 11) goes here. This is the record.
- **Video call with screen sharing**, open during the get-in and during Ari's live hours. The
  operator wears a headset. The tool is Default Ltd's choice (open question C9).
- **Phone call** for anything urgent. Numbers go on the printed address sheet (4.2), not in
  this document.
- **Who decides.** A failure card says who acts. Stopping a performer session is the site
  lead's call. Ari advises. A change to settings or placements is Ari's call. If Ari does not
  answer within 10 minutes: do not re-align; keep the current placements, log the reading and
  carry on; Ari re-aligns in his next live window. The site lead alone decides a switchover to
  the standby (10.7).
- **Ari's live hours (proposal, open question A4).** Tuesday: the whole get-in, 08:00-18:30
  (19:00-05:30 Syd). Wednesday and Thursday: 08:00-13:00 (19:00-00:00 Syd) live, on call by
  phone until 18:30 (05:30 Syd). Outside live hours the operator works from the cards and
  the chat.

### 1.3 Remote access and its fallback

The show runs entirely on the local network. **It should need no internet** [designed; not
yet tried with the internet unplugged: done once in London, 2.1]. Internet is for Ari's
remote access.

1. **Tailscale on the show PC and the standby** (a private network link to Ari's machine).
   Through it Ari opens the console page and runs most reads in this plan from Sydney.
   `firewall.bat` allows the Tailscale range on the console page (TCP 9080) and the F1
   stream (TCP 9001) [designed]. Installed when the PC arrives in London (2.1).
   The standby, parked with its cable out of the show switch, has no internet from the show
   network. Ari reaches it only through its own path (a phone hotspot from a phone that is not
   on a stand, joined on the standby's Wi-Fi) or after a switchover. The standby's Wi-Fi never
   joins the show router: that would put it on the show network beside the show PC.
2. **Screen sharing of the signed-in desktop**, for TouchDesigner and Windows. Use a tool that
   shows the session already running at the PC. **Do not use Windows Remote Desktop**: it can
   start a separate session with its own temporary folder, and a TouchDesigner started there
   does not find the bridge's file and receives nothing [designed,
   `Notes/Windows-Show-Machine-Setup.md`, "The bridge's file"]; it also locks the PC's own
   screen while connected [designed, standard Windows behaviour].
   Which tool: open question C9.
3. **Internet at the venue**: the satellite connection Default Ltd brings (Stroud plan,
   "Hardware"). Its latency and upload speed are [unknown].

**Fallback, in order:**
1. A second internet path for the show PC only: a phone hotspot from a phone that is **not**
   on a stand, joined on the PC's Wi-Fi [designed].
2. The operator points their own laptop or phone camera at the PC screen on a video call, and
   Ari talks them through the card.
3. No contact at all: the operator follows the failure cards alone. The show runs on.

### 1.4 The release line (Ari fills it in before the PC leaves London)

| Item | Value |
|---|---|
| Tracking code on the show PC and the standby (commit) | `beaa18f` on `main`, or the newer commit named in the handover |
| TouchDesigner tox | v95, with "Console Link Active" switched on (v95 is saved with every new switch off, including the consensus view and the prop receiver) |
| Show .toe (what the operator opens in TouchDesigner, 5.2 step 6) | [Ari: made on the show PC in London: the release tox inside, the switches of 5.2 step 6 already set, TD's log (the `logtable` table) open in a pane, saved by the clean-save rules (no venue placements or runtime rows baked in, #38). Its path, for example `C:\Show\TDStage\<name>.toe`. The same file on the standby.] |
| The phone app on every phone (version, build, commit) | [to be filled before the PC leaves London: the build the phones run]. The TestFlight build the phones hold today is 1.1 (4), which predates the 6 November recording fixes, and a newer build has **not** been uploaded yet. Whoever installs the phones must confirm the build number on each one. |
| Preflight command | `WebConsole/.venv/Scripts/python.exe Tools/phone_session.py --preflight --phones 1,2,3,4,5,6 --marker-mm <mm> --expect-version <v> --expect-build <n> --expect-commit <c> --expect-tox <vNN>` [Ari fills the values] |
| Phone capture settings | ARKit capture, the app defaults, the same on every phone [to be filled after the 18 November session: edge-cleanup settings; colour on every phone or on some]. Any phone that runs without colour is named here: its preflight "planes" and "colour" FAILs are then expected (5.2 step 12). |
| Console settings that differ from the defaults | [to be filled after the 18 November session: time-aware consensus (`latency.consensusFreeSpeed`, `latency.labelDilate`), both 0 by default] |

---

## 2. Timeline

### 2.1 Before Stroud

| When | What | Who |
|---|---|---|
| Not yet run | A stage test with real phones. The Sydney three-phone test has not happened, so every placeholder in this plan is still open. The London session of 18 November is a dry run of the procedure, not a measurement. | Remote operator |
| By about 14 Nov | Show PC with Default Ltd in London, so the acceptance can run by 19 Nov (3 November notes) | Default Ltd |
| On the day the PC arrives | Remote access installed: Tailscale and the screen-sharing tool. Static address set (4.2). TouchDesigner and its licence. | Default Ltd with Ari |
| By about 20 Nov | This plan with the 18 November session's answers filled in. The release line (1.4). The Stroud marks file for the frame check (7.2). | Remote operator |
| By 19 Nov | **Acceptance kit** on the show PC: install, firewall, environment check, power and updates, the stack end to end, the network tests through the real switch, TouchDesigner on the bridge, the licence, the vision rate, TouchDesigner frame time, a restore drill. The acceptance note and its tool (`Tools/showpc_acceptance.py`) are in the repository. Its report comes back to the remote operator before the PC leaves London. | Default Ltd with Ari |
| By 19 Nov | **One PoE adapter on one phone for 2 hours** under capture: does it charge AND carry the network at the same time, and does the phone stay cool enough (#33). Decides PoE or the USB option (4.3). | Default Ltd |
| 19-23 Nov | Phones: the TestFlight build installed on each (**not 1.1 (4)**, which is missing the 6 November recording fixes; wait for the newer build or accept that recording is unfixed), Device ID set 1-6, a label with the number on each phone and its stand. One phone streams into the show PC over its adapter. | Default Ltd with Ari |
| 19-23 Nov | **Standby prepared** (10.7 and `Notes/Stroud-Standby-and-Restore.md` section 2): installed once, restored from a snapshot, given the show PC's address, its cable out of the switch. Kept on and signed in to the show account, its show .toe open (10.7). | Default Ltd with Ari |
| 19-23 Nov | **Show .toe** made on the show PC and copied to the standby (1.4). | Ari with Default Ltd |
| 19-23 Nov | UPS bought or hired, sized from the PC's measured draw with the content running, and tested with the PC under load (4.5). | Default Ltd |
| Before the PC leaves London | The stack run once for 10 minutes with the internet unplugged (TouchDesigner's licence included). A snapshot to the USB drive (note its size, 3), the standby refreshed from it. This plan and the address sheet printed. | Operator with Ari |

### 2.2 Tuesday 24: get-in

| Stroud (GMT) | Sydney (AEDT) | What | Who | Section |
|---|---|---|---|---|
| 08:00 | 19:00 Tue | Venue open. Screens, projectors and lighting start (client team). Tracking kit unloaded and checked against the kit list. | Site lead, operator | 3 |
| 08:30 | 19:30 | Floor taping: G0, S0, centreline, O, side lines, phone feet, aim crosses, marks. | Operator and one helper | 6.1 |
| 09:30 | 20:30 | Network and power: UPS, switch, router, show PC on its table; cables run to the six stand positions and taped down. | Operator | 4 |
| 10:00 | 21:00 | Show PC bring-up at the venue. Ari joins the call. | Operator, Ari | 5.2 |
| 10:45 | 21:45 | Stands up, phones mounted, linked, streaming. Link test with the real phones (5 minutes). UPS pull test. | Operator, Ari | 5.2, 4.5 |
| 11:30 | 22:30 | Level, aim, measure heights, lock each phone. Seed the placements in the console. | Operator and helper; Ari reads | 6.3 |
| 12:30 | 23:30 | Lunch | | |
| 13:15 | 00:15 Wed | **Alignment, 13:15 to 14:00,** then it stops whatever state it is in (7.1 step 8). The performance area must be empty and still from 13:15 to about 14:45 (alignment, background learn, spot check): book this with the site lead (open question C2). Screens and gauze hung in their show positions before 13:15; set pieces go in after the alignment. | Ari runs; operator places the structures | 7.1 |
| 14:00 | 01:00 | Structures away, set pieces in their show positions. | Operator | 7.1 |
| 14:15 | 01:15 | Background learn, spot check at O, marks check, padlock on, first re-check reading. Snapshot and standby refresh. | Operator, Ari | 7.1, 7.2, 11 |
| 14:45 | 01:45 | **Client outputs confirmed** with one person on the stage. | Content lead, operator, Ari | 8 |
| 15:30 | 02:30 | Technical rehearsal without performers (screens, light, content). The tracking stays as it is; the operator watches the console. | Client team; operator | 9 |
| 17:00 | 04:00 | One switchover drill to the standby, with the phones streaming, timed step by step, then the switch back to the show PC, also timed. | Operator, Ari | 10.7 |
| 18:00 | 05:00 Wed | End-of-day: re-check, backups, standby refresh, handover. | Operator; Ari reads | 11 |

### 2.3 Wednesday 25: performer day

| Stroud (GMT) | Sydney (AEDT) | What | Who | Section |
|---|---|---|---|---|
| 08:00 | 19:00 Wed | Morning check: phones started, preflight GO, re-check at O. | Operator, Ari | 5.3, 7.3 |
| 08:45 | 19:45 | Short output check with the content running. | Content lead | 8.2 |
| 09:00 | 20:00 | Performers. Before each session: Start show, re-check at O if anything moved. Recordings only with written consent. | Operator, stand runner | 9 |
| 12:30 | 23:30 | Break: re-check at O, copy the console logs, phones to Standby to cool (top bar, all phones: padlock off, Standby, padlock on). | Operator | 7.3 |
| 13:30 | 00:30 Thu | Padlock off, Start show (phones back, Auto-recover armed again), padlock on. Performers. Ari on call by phone. | Operator, stand runner | 9 |
| 17:30 | 04:30 | Last session ends: re-check at O (the day's drift reading). | Operator | 7.3 |
| 18:00 | 05:00 Thu | End-of-day: backups, standby refresh, takes copied [method: C10], handover. | Operator; Ari replies in his morning | 11 |

### 2.4 Thursday 26: performer day and pack-down

As Wednesday until the review, then:

| Stroud (GMT) | Sydney (AEDT) | What | Who |
|---|---|---|---|
| 15:00 | 02:00 Fri | Review with everyone | Site lead |
| 16:00 | 03:00 | Final re-check at O while the phones are still mounted (the last drift reading). Recordings stopped. Final snapshot. Logs and takes copied to the SSD and to the second drive before anything is unplugged (takes: [method: C10], each phone with its capture stopped; how long depends on the minutes recorded, 11 step 7). The phones keep their takes and the PC its logs until the copies are checked. | Operator |
| 16:30 | 03:30 | Pack-down. Phones, PC, drives and cables last, after both copies exist. Takes stay on the phones until the copies are checked. | Operator, crew |

---

## 3. Kit list

**Per phone (six, plus spares, open question C3):**
- iPhone Pro with LiDAR, on TDStage AR (the release line). The 3 November notes name
  refurbished iPhone 15 Pro, on iOS 26 or later. TDStage AR has never run on a 15 Pro
  [unknown]: one second of recording on the first one confirms its field of view.
- Lighting stand reaching 2.5 m (the lens sits at 2.25 m), a clamp on a small ball head, a
  sandbag.
- Network and power, one of (4.3): a PoE adapter (PoE in, USB-C power and Ethernet out) and a
  short USB-C lead; or the USB option: a USB-C Ethernet adapter with power pass-through and
  a USB-C charger.
- Cat6 lead from the switch to the stand (15 m in the 26 October list; length to suit).
- A label with the phone's number on the phone and on the stand.
- A small bottle or cone for aiming.

**Network and power (shared):**
- PoE+ switch (the Netgear GS316EPP was discussed on 3 November: 15 PoE+ ports, 231 W,
  gigabit, no 2.5 G port). A spare switch if one can be found (open question C4).
- A small router for the show network: hands out addresses (DHCP) with one reservation per
  phone, Wi-Fi on the same network as the phones' fallback, internet port to the satellite
  connection.
- One Cat6 lead switch to show PC, one switch to router, one spare.
- UPS with sine-wave output, sized in 4.5 (about 1500 W for a 4090 PC; for a 5090 PC likely the
  2000 W, 3000 VA class), and a plug-in power meter if the UPS has no display.
- Extension leads; a cable plan so that only the PC, its monitor, the switch and the router
  are on the UPS.

**Machines:**
- Show PC (Windows 11, NVIDIA RTX: a 5090 in the 3 November notes, a 4090 in the 20 October
  plan), monitor, keyboard, mouse.
- Standby machine (the 20 October plan lists Mat Collishaw's RTX 4090 PC as a backup machine;
  open question C5), its own monitor, keyboard and Cat6 lead. Kept unplugged from the switch.
- The operator's laptop or tablet for the video call and the chat.

**Floor and alignment:**
- 30 m tape measure, 5 m tape, chalk line, coloured gaffer tape, marker pens.
- An inclinometer (an app on a phone that is not on a stand).
- The printed markers: A3, 10 for the layout (6.2), with their printed size measured.
- Alignment structures [to be filled after the 18 November session: crossed flat boards ("pluses", each arm at
  least 0.9 x 1.2 m) or another structure; how many] (7.1).

**Drives and spares:**
- USB drive for snapshots, 32 GB or more, so it holds several days of them: a snapshot of the
  development Mac was 423 MB, and one that also held TouchDesigner project files 5.5 GB
  [measured on the development Mac]. Check the size of the first show PC snapshot in London.
- 2 TB SSD (USB-C) for takes and logs, and a second drive for their second copy (11 step 7).
- Two spare adapters, spare USB-C and Cat6 leads, a spare phone if available.
- A small fan, for a phone that runs hot (10.9).

**Paper:** this plan, the address sheet (4.2), the placement table (6.2), the acceptance report.

---

## 4. Network and power

### 4.1 Layout

```
 stand 1..6 phones --(one Cat6 each, power + data)--> PoE+ switch ---Cat6---> show PC  10.0.0.10
                                                          |
                                                          +------Cat6------> router  10.0.0.1
                                                                              (DHCP, Wi-Fi fallback)
                                                                              internet port -> satellite
 standby PC  10.0.0.10 (same address)  -- cable OUT of the switch until a switchover --
             its Wi-Fi never joined to the show router (1.3)
 UPS: show PC + monitor, switch, router.   Standby on a different socket.
```

Every stream between the phones and the PC is UDP on the local network [designed, the
project's transport rule]. Ports the PC receives: 9003 (phone depth), 9000 (phone telemetry,
TouchDesigner), 9001 and 9013 (console), 9004 (TouchDesigner), 9080 (console page), 9001 TCP
(F1 0.4). `firewall.bat` opens them (setup note, section 1). F1's TCP 9001 and the console's
internal UDP 9001 share a number and do not conflict [designed].

### 4.2 Address sheet (print it; fill in what is not yet known)

The 10.0.0.x numbers are the example from the setup note. Any private range works if every
line agrees.

| Device | Address | Set where |
|---|---|---|
| Router (gateway, DHCP) | 10.0.0.1 | router's own page |
| Show PC | 10.0.0.10, static, gateway 10.0.0.1 | Windows network adapter settings |
| Standby | 10.0.0.10, static, **cable out of the switch** | its own adapter settings (`Notes/Stroud-Standby-and-Restore.md` 2.4) |
| Phone 1 to 6 | reserved, for example 10.0.0.101 to 10.0.0.106 | router reservation, by the hardware address of that phone's network adapter (a swapped adapter needs a new reservation) |
| Every phone's destination (the app's "TD/Mac Host" field; stored as `stage.tcpHost`) | 10.0.0.10 | on the phone, or pushed from the console |
| Show PC's Tailscale name | [fill in] | Tailscale |
| Router Wi-Fi name | [fill in] | router; every phone joins it (6.3 step 1) |
| Switch's own page (for power-cycling a port, 10.6) | [fill in], on the show network | the switch's setup; its login stays with the switch's paperwork, not in this document |
| Switch ports | for example: phone N on port N (1 to 6), spare phones on 7 and 8, show PC on port 15, router on port 16 | label each lead at both ends with its port |
| Phone numbers for the call tree | [fill in] | |

### 4.3 How the phones connect: PoE or USB (#33)

| Option | When | What changes |
|---|---|---|
| **PoE (planned)** | The bench test of 2.1 passes: one adapter on the phone model and iOS going to Stroud, charging and Ethernet together under capture, cool enough over 2 hours | One Cat6 per phone, nothing else at the stand. The app's "Prefer Ethernet (PoE / cable)" is on by default; the phone's Live page Link line must read **Ethernet**. |
| **USB** | The bench test fails or was not run | A USB-C Ethernet adapter with power pass-through at each phone, plus a charger at each stand: mains power at every stand. Link line still Ethernet. |
| **Wi-Fi with a charger** | Last resort for a phone whose wired link cannot be made to work | That phone streams over the router's Wi-Fi. One or two phones only [unknown beyond that]. |

Power-cycling a switch port does not restart a phone or its app: the phone has its own
battery. It does reset the adapter's network link, which is useful (3 November notes)
[designed].

No adapter has been tested on an iPhone yet, as far as the project's records show [unknown,
#33].

### 4.4 Bandwidth

- **The grid decides whether colour fits the link, so say which grid.** On the ARKit grid
  (256 x 192), which is what the app sends in its default capture path, colour from every
  phone fits one gigabit link: about 450 Mbit/s on the line for six phones (45 per cent of
  gigabit), 525 for seven and 600 for eight [designed; the simulator's bytes match the
  arithmetic, simulated].
- **On the AVFoundation grid (320 x 240) it does not fit at eight.** The same arithmetic gives
  703 Mbit/s for six phones, 820 for seven and 937 for eight, which is 94 per cent of the link
  before anything else on it [designed]. A 17 Pro on that path sends 320 x 240, so if any phone
  is switched to the AVFoundation capture path, count it at the higher figure and keep the
  phone count down.
- The bridge took 114,500 packets a second with none lost on the development Mac [simulated];
  eight colour phones need 49,000. Its rate on the show PC: the acceptance kit measures it
  [unknown].
- **What no paper figure answers:** how the switch handles several phones' frames arriving at
  the same moment. The gate is the real phones through the real switch at the get-in: every
  phone streaming colour, 5 minutes, at most 0.1 % of frames lost (5.2 step 9) [unknown until
  run].
- If the gate fails: colour on fewer phones [to be filled after the 18 November session: which phones keep
  colour first]. 2.5 GbE is not needed for Stroud on ARKit [designed]. A phone running without
  colour gives an expected FAIL on its "planes" and "colour" lines in the preflight (5.2 step
  12): name it in the release line or the handover.

### 4.5 Power and the UPS

- On the UPS: show PC, its monitor, the PoE switch (it powers every phone's adapter) and the
  router. The standby goes on a different socket or circuit.
- Size: an RTX 4090 PC can draw 600-850 W under load and the PoE budget for eight phones is
  about 200 W, so about 1.1 kW at the top: a UPS of about 1500 W with sine-wave output, loaded to
  at most 80 % of its watt rating [designed, nameplate figures]. The 3 November notes name a
  5090, which draws more: a 5090 PC under load with the switch, monitor and router can pass
  80 % of a 1500 W unit, so it likely needs the 2000 W (3000 VA) class [designed]. Size it from
  the PC's measured draw with the content running, read in London (2.1).
- It is for riding through a blip, a pulled plug or a tripped circuit, and for an orderly stop:
  a few minutes at about 1 kW [designed]. It is not for running the show.
- `power.bat` already keeps Windows from sleeping on battery as well as on mains [designed].
- **Get-in test** (Tuesday, 5.2 step 10): with the phones streaming, pull the UPS's own mains
  plug for 30 seconds. Pass: no phone drops from the console's list, TD's cloud is continuous,
  the PC does not sleep [designed; not yet run].
- Overnight power: open question C11.

---

## 5. Show PC bring-up

Commands are typed in **Git Bash** on the show PC (installed for the backups), from the
checkout folder, unless a step names `cmd`. Ari can type the read-only ones from Sydney over
Tailscale, with the PC's Tailscale name in place of `localhost`. In these lines the checkout is
`C:\Show\TDStage` (`/c/Show/TDStage` in Git Bash); the release line names the real folder.
The readings the steps save (small JSON files) go in `C:\Show\readings`, outside the checkout:
make it once with `mkdir -p /c/Show/readings`; from the checkout, the commands write to
`../readings/`.

### 5.1 In London: the acceptance kit

Run once when the PC arrives (2.1). Its note and tool are in the repository
(`Notes/ShowPC-Acceptance.md`, `Tools/showpc_acceptance.py`); this plan refers
to them and does not repeat them. It settles what has
never run on a real Windows PC [unknown]: TouchDesigner reading the bridge's file, the vision
model on the graphics card, hand tracking at runtime, a real network card and switch, and the
client's content on the same graphics card. Its report goes to Ari before the PC leaves
London.

### 5.2 At the venue, Tuesday (after the move from London)

1. PC on the UPS, its cable in the switch, power on. Sign in to the show account. Use the same
   account all three days.
2. `cmd`: `ipconfig`. The wired adapter still reads 10.0.0.10.
3. Double-click `WebConsole\windows\doctor.bat`. Pass: no FAIL. The compute section says
   `yoloDevice=auto resolves to cuda`.
4. `cmd`: `WebConsole\windows\power.bat --check`. Pass: no line starts `[NO  ]`, and the last
   line reads "N of N settings as wanted" with both numbers the same (the Windows Update pause
   counts while it has 7 days or more left). Press a key to close it.
5. Double-click `WebConsole\windows\show.bat`. The console window opens, and the browser opens
   http://localhost:9080. The bridge window starts minimised: it shows only as "TDStage bridge"
   on the taskbar. Leave both windows alone from now on (rule 1).
6. Open TouchDesigner **at the PC or through the screen-sharing tool, never through Windows
   Remote Desktop** (1.3). File > Open > the show .toe named in the release line (1.4). It holds
   the release tox with these switches already set; check each on the parameters of the
   TDStageConductor component:
   - Point Cloud page: `Udpport` 9004, `Udpactive` on;
   - Console page: `Console Link Active` on;
   - Level page: `Segment Off Main Thread` on, `GPU Merge Path` on.
   TD's log (a table named `logtable`, left open in a pane of the show .toe; the newest line is
   at the bottom) reads "TDP4 via tdp4_bridge" once the phones stream. Whenever TouchDesigner asks
   whether to save, choose **Don't Save** (rule 5).
7. Console, Live view, side panel: under "People only", press **Consensus** (person mode: a
   point counts as a person only where the phones' views agree). Under "Tuning", group latency:
   "Consensus: see-through votes" on (a phone that sees through a spot votes it empty). Under
   "Tuning", group vision, the person-detection model (YOLO): "YOLO model" `yolo26n-seg`, "YOLO
   compute" auto, "YOLO rate" 30 Hz (setup note section 3). Then the console settings in the
   release line.
8. Phones on, linked (6.3 step 1), streaming. Each phone's card on the All phones page:
   online, Link Ethernet, about 30 fps.
9. **Link gate** (`cmd`, from the checkout): colour on for every phone (Live view side panel,
   "Phone cameras": **Colour ON for all phones**), then
   `WebConsole\.venv\Scripts\python.exe Tools\link_test.py --expect 6 --seconds 300 --grid 256x192`.
   Pass: the "over 300 s" line shows `phones 6` and at most 0.100 % lost [unknown until run].
   The last line can still read "RESULT: FAIL" for another reason: if it names only "phones
   under 29.1 fps" with "no loss", that is those phones' own frame rate (heat, for example), not
   the network, and the gate passes. Write the line in the chat. Fail: 4.4, last point.
   Afterwards Ari sets colour per phone as the release line says, if it is not every phone.
10. UPS pull test (4.5).
11. `doctor.bat` again with everything running. Pass: no FAIL in "Firewall", "Bridge file and
    TEMP" or "Power and Windows Update".
12. After the alignment (7.1): the preflight from the release line. Pass: it ends `GO`, or
    `NO-GO` only because of the expected "planes" and "colour" FAILs of phones that the release
    line or the handover names as running without colour. Read every WARN. Any other FAIL blocks
    until Ari accepts it in the chat.

### 5.3 Every morning (Wednesday, Thursday), about 30 minutes

1. If the PC was switched off, or TD was restarted: 5.2 steps 1-7 and 11, then re-learn TD's
   background on the empty stage (7.1 step 11) before the first session. A restarted TD does not
   apply its saved background until it learns again (10.5 step 5). If it ran overnight: check
   the console window is open, "TDStage bridge" is on the taskbar, and the console page answers.
2. Padlock off. **Start show** (top bar: it starts every phone from Standby, checks each one
   came up and arms Auto-recover). Every phone streaming, Link Ethernet, about 30 fps, screen
   dark (a lit one: its card's Blackout). Padlock on.
2a. Stage cut unchanged: TD's Stage Cut page and the console's Stage cut section show the four
    numbers written on the address sheet (7.1 step 10a). If not, padlock off, put them back,
    padlock on, and say so in the chat.
3. The preflight (release line). Pass: as 5.2 step 12.
4. Re-check at O (7.3). Write the reading in the chat.
5. If TD ran overnight: re-learn its background on the empty stage (7.1 step 11) only if
   anything in the set moved overnight.
6. If anything in this check changed (a background re-learn, a re-align, a placement or a
   setting): snapshot and refresh the standby (11 steps 4-5), as the standby note asks.

---

## 6. Phone placement

### 6.1 Taping the floor

From `Notes/Stroud-Coverage-Layout.md` ("Tape-measure setup"). Everything is measured from
the gauze and the grey screen, not from the walls. One person on the tape, one on the chalk
line.

1. **G0 and S0.** Measure the gauze's bottom batten end to end (expect 6.00 m) and mark its
   midpoint on the floor below it: G0. The same under the grey screen: S0.
2. **Centreline.** Chalk line G0 to S0. Check it is 8.00 m. If it is not, tell Ari the
   measured length before going on: every position below scales with it, and Ari re-runs the
   placement study if it is off by more than 0.2 m.
3. **O**, the origin, 4.00 m from G0 along the centreline.
4. **X axis.** Square off at O with a 3-4-5 triangle: mark A on the centreline 3.00 m from O
   toward the gauze; the point 4.00 m from O and 5.00 m from A is on the X axis. +X is to your
   right when you face the screen. Do both sides and chalk the cross line.
5. **Side lines** at x = +4.00 m and x = -4.00 m: square off the centreline 1.0 m from G0 and
   1.0 m from S0 on each side and chalk a line through each pair.
6. **Phone feet.** On each side line, mark each phone's z from the cross line through O
   (table 6.2). Check with the two diagonal tapes to G0 and S0 in the table: both within 3 cm.
7. **Aim crosses.** A small taped cross at each phone's floor aim point (table 6.2).
8. **Markers** (A3, flat): each centre on its (x, z), long edge parallel to the cross line,
   top of the image toward the screen. [to be filled after the 18 November session: whether the markers are
   used at Stroud; if not, skip this step.]
9. **Marks for the frame check** (7.2): O plus [Ari: the Stroud marks list, by 18 Nov]. Use a
   different tape colour from the phone marks.
10. Photograph the taped floor from both ends and post the photos in the chat.

### 6.2 Where each phone goes (side rows, six phones)

From the coverage study (`Notes/Stroud-Coverage-Layout.md`, `study_6`). The console loads these
placements and the markers in one step: the **Side rows** button for six phones (Stage 3D page, side
panel, under "Stroud plan"), or
`curl -s -X POST localhost:9080/api/venue/layout -H 'Content-Type: application/json' -d '{"layout":"study_6"}'`.
Do not use the **Front + back** button for six: that is a different layout.

| Phone | Side | x (m) | z (m) | z from gauze line | Lens height | Tilt down | Floor aim point (x, z) | Tape to G0 / S0 |
|---|---|---|---|---|---|---|---|---|
| 1 | +X | +4.00 | +3.50 | 0.50 m | 2.25 m | 32.5 deg | (+0.98, +1.67) | 4.03 / 8.50 m |
| 2 (anchor) | +X | +4.00 | 0.00 | 4.00 m | 2.25 m | 35.0 deg | (+0.90, +0.83) | 5.66 / 5.66 m |
| 3 | +X | +4.00 | -2.50 | 6.50 m | 2.25 m | 35.0 deg | (+0.86, -1.83) | 7.63 / 4.27 m |
| 4 | -X | -4.00 | -2.50 | 6.50 m | 2.25 m | 35.0 deg | (-0.86, -1.83) | 7.63 / 4.27 m |
| 5 | -X | -4.00 | 0.00 | 4.00 m | 2.25 m | 35.0 deg | (-0.90, +0.83) | 5.66 / 5.66 m |
| 6 | -X | -4.00 | +3.50 | 0.50 m | 2.25 m | 32.5 deg | (-0.98, +1.67) | 4.03 / 8.50 m |

Markers (A3 sheets, centres): M1 (0.00, 0.00) at O; M2 (-2.75, +1.75); M3 (+2.75, +1.75);
M4 (-2.25, -1.00); M5 (+2.25, -1.00); M6 (-2.75, +0.75); M7 (+2.75, +0.75); M8 (-2.00, 0.00);
M9 (+2.00, 0.00); M10 (0.00, +3.50).

What this layout gives, from the coverage model at a 70 by 55.5 degree lens and a 4.5 m body
range: 92 % of the volume (feet, torso and head height) seen by at least one phone, 43 % by two
[designed]. **The lens figure is not a measured one**: the coverage note says so itself, and the
same note's narrower-lens tables give 70 % and 22 % at one field reading and 66 % and 19 % at
the other. Section 0's pair, 4 % unseen and 58 % in two or more views, comes from a different
tool at a 5 m range with a 71 degree lens, which is why the two unseen shares differ; neither
is a measurement of this room. The body range itself has not been measured on a
person [unknown]: [to be filled after the 18 November session: the measured body range; if it is well under
4.5 m, Ari sends a revised table].

- **Anchor: phone 2** [designed, proposal; open question A5]. It is the middle of the +X row
  and the nearest to O (4.0 m), so 1 deg of error in its aim moves the whole stage frame by
  about 7 cm at O [designed]. Take the most care with it.
- Every stand is 1 m outside the 6 m width and outside the projected images; none is in
  projector 2's beam as modelled in the coverage study (projector 2 assumed just behind the
  gauze; the 20 October plan has not fixed its position) [designed]. Once projector 2's
  position is fixed, tell Ari before taping.
- Phones on opposite sides are 8 m apart. The middle of the area is 4.0-5.3 m (in plan) from
  every phone [designed, the layout table].

### 6.3 Mount, level, aim, lock

For six phones, from the alignment protocol worked out for the Sydney test.

1. **Link first, on the table.** Each phone: TDStage AR open (the cyan icon), Device ID as its
   label, destination 10.0.0.10. Join each phone to the router's Wi-Fi (name on the address
   sheet): a phone whose cable fails then falls back to it (10.6 b); one that has not joined just
   stops. Its card on the All phones page shows it online.
2. **Mount** in landscape, all six the same way up. Lens over its foot mark: within 2 cm for
   phone 2 (the anchor), 5 cm for the others. Stand legs outside the area, footprints taped,
   sandbag on every stand.
3. **Tilt down** (table 6.2) within 1 deg: the inclinometer flat on the back of the mounted
   phone. Tilt matters only for coverage; the phone levels its own data from gravity.
4. **Roll:** the phone's side panel (click its card on All phones) shows its placement cell as
   `<mode> p<tilt> r<roll>`: it must read `levelled`, with `r` 0.0 within 0.5 deg. A phone in
   `marker` mode is cleared before any alignment.
5. **Aim.** A bottle on the phone's aim cross. Ari reads each phone's picture centre from the
   console and posts its target position in the chat. Turn the phone about the vertical until
   the bottle sits on that target in the picture at
   `http://localhost:9080/api/rgb/<phone>.jpg?scale=4`. Pass: phone 2 within 4 picture
   pixels, the others within 12 [designed].
6. **Lock the head.** Measure the lens height (floor to the centre of the LiDAR lens, the
   top-left lens cluster) to 1 cm and type it into that phone's height in the console. In its
   side panel, Pose: **Lock pose**. Pass: "moved since lock" reads 0.00 deg.
7. **Cables** taped down along the stand and across the floor every 0.5 m, a loop at the clamp.
8. Bottles off the floor.

---

## 7. Alignment and the re-check cadence

### 7.1 Alignment protocol

**[to be filled after the 18 November session: the protocol below is the one the 9 November analysis
recommends (section 4.4) and Wednesday tests. Version 2 of this plan replaces any step the
test changes: the structure, its size and number, the pass lines, whether markers or a walk
set the frame.]**

Ari runs the console steps from Sydney; the operator does the physical ones and TouchDesigner's
switches.

1. **State check.** Every phone `levelled`, roll within 0.5 deg, and "moved since
   lock" under 0.5 deg (the stands stood through lunch; over 0.5: card 10.2 step 2 first).
   TouchDesigner Level page: Level Status "not solved" or "cleared (identity)"; all six trims 0;
   View page Flooroffset 0.
2. **Seed** the placements: the **Side rows** button for six phones (Stage 3D side panel, 6.2), then the measured
   heights (6.3 step 6).
   Markers page: the printed marker size [to be filled after the 18 November session: whether markers are used
   at all; marker calibration has never run end to end, #35]. No phone left in marker mode.
3. **Structures** placed, the performance area clear of people, nobody in any phone's view
   [to be filled after the 18 November session: type and size]. Proposed positions [designed]: S1 at O (the
   only place both rows see well, 4.1-4.6 m from phones 2 and 5), then one in each row's
   shared zone, for example at M7 (phones 1 and 2), M5 (phones 2 and 3), M6 (phones 5 and 6)
   and M4 (phones 4 and 5). Never bins, tubes, round objects or people. The side-row layout
   itself has not been simulated for alignment [unknown]: every alignment figure in this section
   comes from simulations of the Sydney three-phone layout. The link between the two rows rests
   on the structure at O, near the planned body range (open question A11).
4. **Save the state:**
   `curl -s localhost:9080/api/state > ../readings/state-before-align.json`
5. **Preview twice** (writes nothing), saving each result:
   `curl -s -X POST localhost:9080/api/align/rig -H 'Content-Type: application/json' -d '{"anchor":2,"apply":false,"usePlan":true}'`
   then poll `curl -s localhost:9080/api/align/job` until done, and save it:
   `curl -s localhost:9080/api/align/job > ../readings/align-preview-1.json` (the second
   preview: `align-preview-2.json`).
6. **Apply only if** every phone is OK in both previews, the two previews agree within 1 deg
   and 5 cm, and each phone is within 2 deg and 0.15 m of its taped placement. The
   console itself now refuses to apply a clouds WARN. Apply:
   the same line with `"apply":true`. It runs a fresh third solve: poll until done and save it,
   `curl -s localhost:9080/api/align/job > ../readings/align-apply.json`. Press **Undo** once
   (the arrow at the top left, beside the page title; its tooltip reads "Undo last config
   change") if any phone is WARN or the applied result is more than 1 deg or 5 cm from the two
   previews.
7. **Judge** by what stands above the floor, not by grades: each structure appears once, not
   twice; each phone's frustum (the drawn shape showing where it looks) points the way the
   real phone faces; one person standing still on O shows as one body at (0, 0).
8. **Cut-off: the alignment stops 45 minutes after it starts** (about 14:00 on the 2.2
   timeline), whatever state it is in. The site lead writes the actual stop time in the chat
   when the slot starts. If no alignment has been applied and passed steps 6 and 7 by then,
   keep the taped placements and write "frame source: taped placements" in the chat. In the
   simulations of the Sydney layout, taped placements kept after a refused alignment were off
   by a median of 2-14 cm, depending on how carefully they were taped and aimed [simulated,
   analysis 4.3 item 1].
9. Structures away.
10. Set pieces in their show positions (screens and gauze were hung before the alignment).
10a. **Stage cut** (version 2 draft; needs the Thursday 12 Nov landing on the show PC). Stage
    empty, padlock off. Set the cut in **both** places, with the same numbers:
    - **TouchDesigner, Stage Cut page:** Show Wall Plane on. Wall Yaw = the direction the
      backdrop faces (0 = upstage). **Fit Wall To Cloud** (Backdrop Wall Cut off): check the pink
      plane sits just in front of the backdrop points, then **Backdrop Wall Cut** on. Ground
      Cutoff: 0.06 unless the act works on the floor (then [decided by the client's takes]).
      Show Wall Plane off.
    - **Console Live view, Stage cut:** Wall cut on with the same Wall yaw and Wall distance;
      Floor cut height [decided by the client's takes]. "Fit wall to cloud" gives the same
      0.25 m margin; type TD's numbers if they differ.
    - Write the four numbers (wall yaw, wall distance, TD ground cutoff, console floor cut) in
      the chat and on the address sheet.
    - A plane set through the stage removes performers with no warning (the console warns only
      when every point is cut): one person walks the downstage edge and the backdrop line, and
      both previews must keep them whole.
11. **Background learn**, stage empty: TouchDesigner Human page, Learn Frames 450, **Learn
    Background**; wait for the log line "background learned (saved)". Level page: Segmode
    **learned** (how TD separates people from the set). Console Live view: **Stage is empty
    now**, wait 30 seconds.
12. **Absolute check** (7.2).
13. **Padlock on** (the button reads **Locked**). Save `api/state` again
    (`curl -s localhost:9080/api/state > ../readings/state-after-align.json`). Snapshot and
    refresh the standby (11, steps 4-5): the alignment is in the snapshot only from now.

Undo puts back every placement one applied alignment moved (one Undo per apply). With the
padlock on, Undo of a placement is refused: unlock first. If Ari cannot be reached, nobody
re-aligns: keep the placements and log the reading (1.2).

### 7.2 Absolute check (the only check against the tape)

The alignment grades only say the phones agree with each other. An error every phone shares
still agrees with itself. Only a person on a known mark catches it [designed].

1. **Spot check at O.** One person stands still on O. While they stand there, run (the time as
   HHMM with no colon, because a Windows file name cannot hold one):
   `curl -s "http://localhost:9080/api/rig/calib?x=0&z=0" | tee ../readings/calib-O-1415.json`
   The reading prints on the screen and is saved. Pass: `spot.err` at most 0.10 m. Go by
   `spot.err` alone: the response's `state` and `spot.ok` use 0.15 m, so a reading between 0.10
   and 0.15 can say "ok" and still fails here.
2. **Marks check** (Ari, from Sydney): the person stands still on each mark in turn, 5 seconds
   each, while `Tools/frame_fit.py --live http://<PC>:9080 --marks <Stroud marks file> --order <marks> --pivot=4.0,0.0`
   samples /track. Pass: common offset at most 8 cm and frame turn at most 1.0 deg [designed;
   the method is checked on synthetic marks only, simulated]. A common offset means: check
   phone 2's stand and aim, and its typed placement.
3. Write the readings in the chat.

`/api/rig/calib` and `frame_fit` have never run with real phones [designed]. Errors under about
5 cm are not visible to the spot check [designed].

### 7.3 Re-check cadence

From `Notes/TASK-BOARD.md` ("Stroud: alignment re-check cadence"). Why: no drift has been
measured over a working day, and a phone that is turned (panned) raises no alarm [unknown;
designed].

- **When:** after the get-in, once aligned with the padlock on; after any **PHONE MOVED**
  alarm; after a phone relaunch (10.1); at each break; before each performer session; at the
  end of each day.
- **The check:** one person stands still on O; while they stand there, run
  `curl -s "http://localhost:9080/api/rig/calib?x=0&z=0" | tee ../readings/calib-<HHMM>.json`
  with the time and no colon, for example `calib-1415.json` (on the show PC in Git Bash, from
  the checkout; or Ari from Sydney). The reading prints on the screen.
- **Pass line:** re-align (7.1) when `spot.err` is over 0.10 m. Otherwise write it down and
  carry on.
- **Record** in the chat: the time, `spot.err`, each phone's "moved since lock" tilt and turn
  from its side panel, and what was done.
- If the response's `state` is `"unknown"` there is no reading: read its `text`.
  - "the empty stage is not learned yet: clear the stage and press Stage is empty now (Live
    view), or wait about 45 s": clear the stage, padlock off, **Stage is empty now** (Live view
    side panel, "People only"), padlock on, wait 30 seconds, check again.
  - "needs one person seen by two or more phones (N saw enough of them; ...)": write that down
    and tell Ari: O should be in view of phones 2 and 5.

---

## 8. Client outputs, and how the client confirms them

### 8.1 What the console sends

| Output | What | Where | Evidence |
|---|---|---|---|
| **/track** (F1 v0.3, OSC over UDP) | Performers (position, velocity, confidence, `clustered`), hands, ids | UDP 7000 to the client bus. At Stroud tracking and content share one PC, so 127.0.0.1:7000 unless the content lead names another address (open question C7) | 22-23 bundles a second, capture to send p50 94-131 ms, on a loaded Mac with a simulated six-phone rig [simulated]. Never run on real bodies (#17). Hands on Windows untested with phones [unknown] |
| **F1 0.4** (WebSocket) | Occupancy field (SMSF), presence (SMSP), sensor poses (SMSS), each with its capture time | TCP 9001 on the show PC | Requirements check against the 0.4 draft on the development Mac on 27 October, with Default Ltd's decoder `sms_td.py`: 14 PASS, 4 built, 0 FAIL, 7 need the rig [simulated]. Without that decoder (GitHub's Windows test machine) the same tool reads 7 PASS, 3 built, 15 need the rig. Some PASS rows check plan geometry only, not a measurement. Density and latency with several phones not measured (#29) |
| **NDI** | A rendered view of the merged cloud, source "TDStage Point Cloud", 960 x 540, 30 fps | From the console, on the show network | Never run on Windows (#26) [unknown]. Needs the NDI runtime on the PC |
| Performers inside TD | The /track performers and hands drawn in TouchDesigner, from a copy sent to 127.0.0.1:7001 | Inside TD. Tox v95 carries the receiver with its switch off and draws nothing. Tox v96 (17 November) draws them in TD's preview, a cylinder per performer and a sphere per hand, with no parameter added and every switch saved as in v95. Which of the two the PC takes is set in the release line (1.4) | [simulated: v96's drawing tested only by replaying a recorded /track file] |

What the outputs mean, briefly:
- Positions are metres in the stage frame ("Coordinates", at the top of this plan). A
  performer's y is on the floor (0) when standing [designed].
- When two performers are too close to tell apart, `clustered` is 1. While each still has a
  blob of their own, both positions are measured and only the identity may be wrong. Once they
  merge, the hidden one moves with its neighbour, velocity 0 and confidence 0.30, for up to
  10 seconds. Treat an id as provisional while `clustered` is 1 (3 November notes, #32)
  [simulated].
- In simulation, performers in their own costumes swapped ids in 0-3 % of crossings; in one
  shared costume 19-40 % [simulated, README].
- During a bridge restart /track pauses for about 2-3 seconds. A phone away for less than about
  36 s is not relearned as background, so its points count again as soon as it returns; how long
  its performers take to come back after that is not measured. A console restart costs about
  34 s with no performers while it relearns the empty stage [simulated, 12 Nov], and ids start
  again afterwards; during a switchover to the standby 3-5 minutes
  [simulated; designed]. What the content does then is open question C8.

### 8.2 How the client confirms them (Tuesday 14:45, and short form each morning)

1. Operator: console Live view shows /track **ON** with its target, the F1 producer up, NDI on
   if wanted.
2. Content lead: start the client's receivers. Their `f1-probe` (from the F1 repository)
   checks /track against the contract. For F1 0.4, their decoder `sms_td.py` in
   TouchDesigner; Ari can also run `Tools/f1_probe.py` for density and age.
3. One person stands still on **O** for 10 seconds. The content reads x about 0, z about 0.
4. The person walks 2 m toward the **gauze**, then 2 m to **+X** (your right facing the
   screen). The content shows the same moves. If the client's z runs the other way, the
   operator, with Ari's agreement: padlock off, Live view side panel, "Client output (F1
   contract)": **Flip Z axis** on (the same setting as Tuning > output > "Flip depth axis"),
   padlock on. It flips z on /track only, not on F1 0.4 [designed]: if the content uses both,
   agree one direction first.
5. The person leaves the stage. /track goes to zero performers within a few seconds (an id is
   held for 3 s after it is lost, then released) [designed].
6. Two people cross once. The content lead watches the ids and `clustered`.
7. NDI: the content lead sees "TDStage Point Cloud" in an NDI monitor or TD's NDI In.
8. The content lead writes **"outputs confirmed"** in the chat, with the time and any number
   that looked wrong.

---

## 9. Show running rules

From the moment the padlock goes on (7.1 step 13) until pack-down. Everyone in the room, not
only the operator.

1. **Never close the bridge window or the console window,** and do not click inside them,
   unless a card says so (10.3 step 5, the switch back in 10.7). Closing one stops it for good
   (it does not restart). If one was closed: cards 10.3 and 10.4. The bridge window starts
   minimised: it is the "TDStage bridge" entry on the taskbar.
2. **Padlock on at all times.** For a task in this plan that needs a press (Start show,
   Standby, Blackout, Stage is empty now, a re-align): padlock off, press, padlock on. While
   on, the console refuses every change to its phone placements (edits, layouts, applied
   alignments, Undo, Push poses) from any browser or program;
   recording, phone commands, settings and person mode still pass from programs, but the locked
   browser page itself sends nothing. A marker calibration sent to a phone would still change
   that phone's placement in TD: none is sent while locked.
3. **Do not touch the stands, clamps or phones,** and keep people, cases and cables clear of
   the stand legs. A bumped stand: card 10.2.
4. **No installs, updates, code changes or restarts** of the show PC during the three days,
   unless a failure card says so. The update pause is set by `power.bat`.
5. **TouchDesigner: never press Level > "Solve Level" or View > "Set Floor To Origin".** (The
   tox refuses both while the console places the phones; do not test that.) The
   operator never saves the tox or the show .toe: when TouchDesigner asks on closing, choose
   **Don't Save**. Any TouchDesigner change is Ari's, saved only with the clean numbered save
   (no venue placements baked in, #38), then snapshotted.
6. **One console only.** Never start a second console, a simulator or a recording playback
   on the show network. A second console has overwritten TouchDesigner's placements before.
7. **Do not press "Send telemetry here"** on a working rig. It is only for TouchDesigner down
   for good (card 10.5).
8. **A phone app is closed only this way:** Home, then flick it away in the app switcher. At
   most 2 per phone in 4 minutes: three unclean exits in 4 minutes put the phone in SAFE MODE,
   which turns its colour off.
9. **Keep the console's Live view open** on the operator's monitor. Closing the browser page
   does not stop the outputs, but some checks run only while it is open.
10. **Do not lower the vision rate** (`vision.yoloRateHz`): it makes the person masks older,
    not fresher.
11. **After any change to a placement** (a re-align, a phone put back): stage empty, TD
    background re-learned, Stage is empty now, 30 seconds, re-check at O. Then snapshot and
    refresh the standby (11 steps 4-5) at the next break.
12. **After any change to the set in view** (screens, gauze, furniture, objects left on the
    floor): re-learn TD's background on the empty stage, then snapshot and refresh the standby
    at the next break. Lighting changes matter to the colour picture the person masks use;
    whether stage lighting changes the depth data is [unknown] (the Sydney test's lights-down
    card looks at it).
13. **Recordings only with written consent** from every performer in view (the Stroud plan's
    consent item). The site lead says which sessions are recorded.
14. **The standby's cable stays out of the show switch** until a switchover, and its Wi-Fi
    never joins the show router. Two machines with one address on one network conflict.
15. **Nothing else on the UPS.** Do not unplug the UPS, the switch or the router.
16. **The stage cut is part of the placement.** Changing Wall Yaw, Wall Distance, Ground Cutoff
    or the console's floor cut is a placement change: rule 11 applies. Never fit or move the wall
    with people on stage.
17. **Cut the backdrop in the console whenever scenery behind the acting area is in view.**
    A person model can fire on a printed figure, a poster or painted flats with no performer
    there. In simulation, keypoints firing on painted back-wall flats made extra /track
    performers in 4-6 % of frames at 8 phones; that path is fixed (12 Nov: a keypoint hit with
    no outline makes no performer) [simulated], but a printed figure the person model also
    outlines would still count. The console's wall cut removes anything behind it. Set the
    backdrop wall (Live view, Fit wall) at the get-in, after placement, on the empty stage
    (rule 16).
18. **Wait 40 seconds after the last phone joins or is moved before a run starts.** A phone
    joining a learned scene, returning after more than about 36 s, or being re-placed promotes
    its whole view at once 16 to 32 s later; `/track` then carries no performers for about 5 s
    and every id changes [measured offline against the real engine on a fake clock, not on a
    rig; #71 open]. Side-by-side runs on 17 November put a number on the whole session's cost:
    on the code this plan describes, `/track` sat settled but sent no performer for **5 to 12
    seconds in every run** of the phone-joining scenario [simulated]. The fix passed those runs
    and lands **after** the 18 November session, so plan the wait, not the fix. Pressing **Stage is empty now** on the empty stage has the same settling
    effect at once and is the quicker way out of it.
19. **Leave Max performers at 0 unless the act has a fixed cast.** The setting exists for the
    opposite case: with a cap, the least confident performers above it are dropped, because
    flooding the client's bus with phantom ids is worse than reporting none, and geometry
    clustering with no working person model has reported 19 bodies on a 6-body scene. The cost
    of setting it is now measured: with the cap at 1 and two walkers in view, the single id
    switched between the two bodies **about 90 times in 150 seconds**, 87 to 97 across runs
    [simulated, 17 November]. So if the cyr act sets the cap, keep one person and nothing else
    body-sized in the stage area for its whole length. Everything else in that panel stays as
    the plan set it.
20. **Stage is empty now learns the room immediately, whatever the maturity fraction is set
    to.** So it is the button for a scene change, and it is also the button that makes a maturity
    comparison meaningless: a run seeded with it cannot be compared with one that was not.
21. **The console refuses a POST from a web page it did not serve** (any `Origin` that is not
    its own host), and refuses a request body over 1 MiB. Nothing in this plan is affected; a
    helper script somebody writes on the day is, if it posts from a browser page.
22. **Two features stay off, and are not part of this plan.** Body points
    (`/track/performer/body`, 17 joints a performer) are experimental and not good enough for a
    show. On this layout with six phones and three people the figures are 101 mm of limb error
    at the median, 539 mm at the 95th percentile, and **13 per cent of the joints it does send
    more than 30 cm out**, with about a quarter of the joints withheld altogether [simulated
    against the simulator's own joints, never on a rig]. Props with their own inertial sensors
    are undecided and nothing of them is planned for Stroud: the receiver is in the console and
    in tox v95 with every switch off, no board has ever run the firmware, and the client has not
    defined what a prop is on their bus.
23. **If the TouchDesigner licence fails on the day,** run the console alone:
    `WebConsole\windows\show.bat --listen 9000`. The phones, the merged cloud, the people,
    `/track` and the field stream are all the console's and keep working; there are no show
    visuals and no NDI, because those are TouchDesigner's. The full procedure is on
    [A session without TouchDesigner](no-touchdesigner.html). Do not press **Send telemetry
    here** to get telemetry in that state: it writes a port into every phone that has to be
    put back afterwards. Start the console on 9000 instead, as that page says.

### 9.1 The cyr wheel act (version 2 draft)

For a solo act with an inverted performer. The person model misses inverted bodies (the
client's rotation proxy: 22 % of upright detections kept at 180 deg [Default Ltd]), so /track
and F1 presence drop the performer on the default settings. TouchDesigner's cloud and the
visuals are not affected. The act runs on depth instead:

1. On cue from the site lead, padlock off, Console Live view, People only: **Apply cyr preset**,
   confirm, padlock on. It sets: person filter Motion, performers from geometry, person mask
   off, max footprint 2.4 m, performer height min 0.3 m, max performers 1, F1 presence from
   depth. **One performer only:** it cannot separate two people who touch.
2. During the act: /track carries one performer from depth; F1 presence carries any body-sized
   cluster that is not background, so a prop, a moved chair or the wheel itself can count.
   Hands: none (they come from the person model).
3. After the act, on cue: padlock off, **Reverse cyr preset**, padlock on. It restores the exact
   values from before the apply, also after a console restart.
4. Rates: on a development Mac the preset ran F1 at 8.3 Hz and /track at 9.7 Hz against 13.8 and
   20.9 at the defaults [simulated]. **[decided by the London acceptance: the rates on the show
   PC with eight phones]**. If they are too low, the act runs on the defaults and /track drops
   the inverted performer: say so to the client before the act, not after.
5. Not yet tested on a real inverted body: **[decided by the client's inverted takes]**.
6. **Rotate and retry** (Settings > Vision, off by default; lands 12 Nov): the alternative that
   keeps the person model. When YOLO finds nobody upright but a phone's depth holds a body-sized
   blob, YOLO looks again at the picture turned 180, 90 or 270 deg (one extra pass a frame).
   On turned upright takes it found the body 99-100 % of the time at 90/180/270 against 0-29 %
   without it, with no false people [simulated]. A phone that sees an upright person is not
   retried. Whether the act uses it, the preset, or both: **[decided by the client's inverted
   takes and the London acceptance]**.

---

## 10. Failure cards

Each card: what you see, what to do, who. "Next break" means the site lead's call.

### 10.1 A phone stops (app crash, phone off, reboot)

**Signs.** The phone's card on the All phones page shows it offline or not streaming; Rig health
(the console's list of checks) lists fewer phones reaching; its part of the cloud is gone in
TD; the phone shows its Home or lock screen.

**Do.**
1. Operator: write the time and phone number in the chat. A session carries on: the other
   phones keep the cloud and /track [designed], with less coverage in that phone's zone.
2. Stand runner, now or at the next break: open TDStage AR from its icon on that phone. If it
   is in the background, Home first, then the icon. Tap only the screen: do not push the phone
   or turn its head. Rule 8 for closing.
3. With **Start show** pressed (it arms Auto-recover), the console restarts that phone's stream
   within about 12 seconds of the app opening [designed; not yet run on the rig]. Otherwise:
   padlock off, Start show, padlock on.
4. A phone opened by hand comes up with its screen lit: only the automatic restarts go dark
   again (#49) [designed; not yet checked on a device]. Padlock off, that phone's card:
   **Blackout**, padlock on. If the button reads Wake, the screen is already dark: leave it.
5. Its card: streaming, Link Ethernet. **A relaunch resets the phone's movement reference,** so
   "moved since lock" says nothing about that phone afterwards: it reads "not locked", or 0.00
   once Blackout takes a new reference wherever the phone points now [designed, from the app's
   code]. Re-check at O (7.3) at the next break. Only after the re-check passes: padlock off,
   **Lock pose** in that phone's side panel, padlock on. Over 0.10 m: card 10.2 step 4.
6. It will not come back (dead, too hot, will not start): carry on without it and tell Ari. A
   spare phone can take its number (Device ID row; the console pushes the stored settings)
   [designed; never tried on the rig]. A spare must be mounted, aimed and locked (6.3) and
   re-checked (7.3); Ari guides.

**Who.** Stand runner (hands), operator (console), Ari (spare).
**Why this matters.** 17 app crashes in 38 launches across three phones during development
[measured on rig, 6 Nov recovery logs]. Nothing relaunches a crashed phone by itself.

### 10.2 A phone moved (knocked, tilted or turned)

**Signs.** The console log says **PHONE MOVED: tilted ...** and the phone's side panel shows
"moved since lock" over 0.5 deg. **A turn about the vertical (pan) raises no alarm**
[designed]. Its signs: a doubled body or a doubled object in the Live view, a person jumping as
they walk into that phone's view, or a re-check at O over 0.10 m.

**Do.**
1. Operator: time and phone number in the chat. The session carries on unless the site lead
   stops it; that phone may place people wrongly until fixed.
2. At the next break, stand runner: the stand back on its taped footprints, the head back to
   its tilt and aim (the bottle on its aim cross, the target Ari posted). "Moved since lock"
   back under 0.5 deg.
3. Re-check at O (7.3). Pass: carry on and log it.
4. Over 0.10 m, or **phone 2 (the anchor) moved**: re-align (7.1 steps 1-13; padlock off; Ari),
   which includes rule 11. If Ari does not answer within 10 minutes: no re-align; keep the
   current placements, log the reading and carry on; Ari re-aligns in his next live window
   (1.2).

**Who.** Stand runner, operator, Ari.
**Size.** 1 deg of turn moves a person 4 m away by about 7 cm [designed].

### 10.3 The bridge restarts (2-3 seconds blank)

**Signs.** TD's cloud freezes or empties for about 2-3 seconds, then comes back. /track pauses
for the same time (the console reads the same data). The bridge window, which starts minimised
("TDStage bridge" on the taskbar), shows `bridge exited (code N) at <time> - restarting in 2 s.`

**Do.**
1. Nothing, if it comes back within about 5 seconds. Operator: log the time and the exit code
   (click "TDStage bridge" on the taskbar to see the window; do not click inside it).
2. Do not close the bridge window. Do not start `show.bat` again (it would start a second
   bridge).
3. It repeats (more than twice in an hour), or does not come back within 10 seconds: tell Ari.
4. **The bridge window seems gone.** It starts minimised, so look for "TDStage bridge" on the
   taskbar first. Start a bridge only when there is no such entry **and** `doctor.bat`'s
   "Bridge file and TEMP" section lists no bridge process: then double-click
   `WebConsole\windows\bridge.bat` once. Never start a second bridge: it resets the shared file
   the running bridge writes and then cannot take the phones' port, which breaks the show's
   cloud [designed, from the code].
5. **Operator alone, when the window is there but no frames come back for 30 seconds** (TD's
   cloud and the console's Live view stay empty while the phones' cards say streaming): close
   that bridge window, double-click `WebConsole\windows\bridge.bat` once, then tell Ari.

**Who.** Operator logs and acts on steps 4 and 5; Ari investigates.
**Evidence.** 2.1-2.8 seconds from the bridge stopping to the first new frame, in 30 runs on
the development Mac with a simulated phone [simulated]. On the show PC with real phones
[unknown].

### 10.4 The console closes

**Signs and do, by case.**
- **(a) The console program stopped by itself.** Its window shows `Console exited (code N) at
  <time> - restarting in 3 s.` It restarts by itself [designed]. /track, F1 and NDI pause; TD's
  cloud is not affected. After the restart: /track performer ids start again (the client should
  treat them as new), and the console re-learns its own motion background, so /track may report
  nobody for a short time [designed; length unknown].
  1. Operator: log it. Reload the console page. The padlock and the output switches come back as
     saved [designed]; check /track shows ON in the Live view.
  2. /track still empty after a minute with someone on stage: at the next break, stage empty,
     padlock off, Stage is empty now, padlock on.
  3. Content lead: check the receivers reconnected (F1 clients must reconnect; whether the
     client's do on their own is open question C8).
- **(b) Someone closed the console window.** It does not restart. Double-click
  `WebConsole\windows\run.bat` (the console only, never `show.bat`). If it says "NOT started:
  another console is already running", one is: use that one.
- **(c) The browser page closed.** Nothing stops. Reopen http://localhost:9080.

**Who.** Operator; content lead; Ari checks remotely.

### 10.5 TouchDesigner crashes or freezes

**Signs.** TD window gone or frozen, visuals stop, Rig health says TouchDesigner is not linked;
after a while the phones' telemetry goes stale on the console (it reaches the console through
TD).

**Do.**
1. Operator: log it. The phones keep streaming; /track, F1 and NDI continue from the console
   [designed].
2. **TD frozen** (its window does not respond for 30 seconds): Ctrl+Shift+Esc opens Task
   Manager; select TouchDesigner, **End task**. TD gone or ended: reopen it in the same
   signed-in session (at the PC, or through the screen-sharing tool; never Windows Remote
   Desktop): TouchDesigner, File > Open > the show .toe from the release line (1.4). If it asks
   to save anything: **Don't Save**.
3. Check the switches of 5.2 step 6 (the show .toe has them set). TD's log pane: "TDP4 via
   tdp4_bridge".
4. The console sends TD the phone placements when TD links [designed]: the console's
   TouchDesigner line answers.
5. **Re-learn TD's background** on the empty stage (7.1 step 11) at the next break: after a
   restart the learned background is not applied until it is learned again [designed].
6. If the client's content runs in the same TouchDesigner, it stopped too: the content lead
   restarts it (open question C6).
7. TD will not come back at all: Ari decides on "Send telemetry here" (rule 7) or the standby
   (10.7).

**Who.** Operator, content lead, Ari.

### 10.6 Wi-Fi or internet lost

- **(a) Internet to Sydney lost.** The show is not affected [designed]. Ari's access is gone.
  Carry on with the cards; use the phone. If Ari needs access: the fallback path (1.3).
- **(b) A phone shows Wi-Fi instead of Ethernet** (its card's Link line; the console logs
  "stream left Ethernet"). Its wired link failed and it moved to the router's Wi-Fi [designed].
  At the next break, stand runner: re-seat the USB-C at the phone and the adapter, and the Cat6
  at both ends; check the switch port's light. Then, if the switch can, Ari or the operator
  power-cycles that switch port from the switch's own page (its address and the port map are
  on the address sheet, 4.2; it resets the adapter, not the phone) [designed]. Link back to
  Ethernet. A phone that has not joined the router's Wi-Fi just stops: card 10.1.
- **(c) The router fails.** Wired phones keep streaming [designed]; their addresses hold until
  their lease runs out. Phones on Wi-Fi stop. Restart the router (it is on the UPS).

**Who.** Operator, stand runner, Ari.

### 10.7 The show PC dies: switch to the standby

**Keep the standby ready.** The standby stays on, signed in to the show account, its cable out of
the show switch. After each refresh (11 step 5), open its show .toe (1.4) and leave
TouchDesigner running. A standby that is off would add a Windows start, the sign-in and
TouchDesigner's start to the switchover.

**Signs.** Everything stops: TD, console, visuals. The PC is black, frozen, rebooting or shows
a blue screen.

**Decide.**
1. As soon as the show PC fails, the operator prepares the standby with its cable still out:
   double-click its `WebConsole\windows\show.bat`; TouchDesigner is already open with its show
   .toe (if not: File > Open > the show .toe). With the cable out nothing reaches the phones
   [designed; Ari to confirm that a console started with no link is safe to leave running, A9].
2. If the show PC is not back with the bridge, console and TD running within 2 minutes, or
   fails a second time, the site lead decides to switch: with Ari if he answers, alone if he
   does not (1.2). Only then are the cables moved. If the show PC comes back instead, close the
   standby's console and bridge windows at the next break and leave its TouchDesigner open.

**Do** (from `Notes/Stroud-Standby-and-Restore.md` section 4; the standby refreshed at the last
end-of-day, after the alignment, or after the last change in a morning check, 5.3 step 6):
1. Pull the show PC's network cable (or switch it off). It must not hold 10.0.0.10 any more.
2. Plug the standby's cable into the show switch, in the show PC's port (4.2).
3. Standby: the console and bridge are running (Decide, step 1); if not, double-click
   `WebConsole\windows\show.bat` now.
4. TouchDesigner on the standby: check the switches of 5.2 step 6.
5. **Padlock:** the standby starts locked if the show console was locked. The button reads
   "Unlock poses" or "Locked": one click unlocks. Then Dashboard, "TouchDesigner link" panel:
   **Push poses now**.
6. The phones keep sending to 10.0.0.10 and need no change. After 30 seconds, any phone
   missing: Dashboard > Array control > **Ping all**. Still missing: relaunch its app (10.1).
   Then the padlock on.
7. Client outputs: same address as before. The content lead checks the receivers. If the
   content ran on the dead PC, it has to start on the standby (open questions C5, C6).
8. At the next break: TD background re-learned, re-check at O, `doctor.bat`.

**Switch back** (after the Tuesday drill, or once the show PC is repaired; at a break, never
during a session). The show PC is the machine of record: during the drill, change nothing on
the standby. After a real switchover, anything changed on the standby (a re-align, a placement,
a setting) is not carried back by itself: write it in the chat, and Ari redoes it on the show
PC after the switch back.
1. Show PC: on, signed in, its cable still out, its bridge, console and TD running (5.2 steps
   1-7 if it was off; after the drill they are still running).
2. Standby: close its console window, its bridge window ("TDStage bridge" on the taskbar) and
   TouchDesigner (Don't Save). This is the one time those windows are closed on purpose.
3. Pull the standby's cable out of the switch.
4. Plug the show PC's cable back into its port.
5. Show PC console: padlock off, Dashboard > Array control > **Ping all** (the phones learn the
   show PC's hardware address again), padlock on. After 30 seconds every phone streams into the
   show PC's TD; one still missing: Ping all again (padlock off, Ping all, padlock on), then
   relaunch its app (10.1).
6. The padlock reads Locked. Push poses (padlock off, Push poses now, padlock on) only if the
   Dashboard warns "Poses NOT sent to TouchDesigner" or TD's placements do not match.
7. Content lead: check the receivers. Re-check at O (7.3).
8. Snapshot on the show PC and refresh the standby (11 steps 4-5), then reopen the standby's
   show .toe and leave it ready.

Time the switch back as well, step by step.

**Who.** The site lead decides (with Ari when he answers); operator does; content lead checks
outputs.
**Time.** 3-5 minutes from the decision to phones streaming into TD, with the standby prepared
and refreshed [designed]. Never run on Windows or with phones [unknown]: the Tuesday drill
(2.2, 17:00) times it. A standby refresh from a snapshot took 0.5-1.9 s [measured on the
development Mac].
**What is lost.** Every change since the last snapshot; /track ids start again.

### 10.8 Power cut, or the switch fails

**Signs.** The UPS beeps; or every phone drops from the console at once and the switch lights
are off.
**Do.** On a power cut the UPS keeps the PC, switch and router up for a few minutes
[designed]: restore mains, or stop in order if it will not come back. A dead switch: the spare
switch, same port numbers (the port map on the address sheet, 4.2); the phones run on their
batteries but have no network until then.
**Who.** Operator, site lead.

### 10.9 A phone runs hot

**Signs.** Its card shows thermal "serious" or "critical". Serious is normal: in the one heat
run, two phones reached serious after 7-9 minutes, never critical; one held 30 fps for 31
minutes at serious, the other 25 fps [living room, plugged in, 28 Oct]. Critical (about 15 fps)
is not normal.
**Do.** Critical: shade it, aim the fan at it. At the next break, stop that phone only: padlock
off, its side panel (click its card): **Stop**, padlock on. Auto-recover leaves a phone stopped
from the console alone (its card shows AUTO-RECOVER PAUSED) until it is started again. Once it
has cooled: padlock off, its card's **Start**, padlock on. Do not use the top-bar Standby for
one phone: it stops every phone and disarms Auto-recover. Ari may set that phone to depth
without colour: its preflight "planes" and "colour" lines then FAIL as expected (5.2 step 12).
The iPhone 15 Pro has never been heat-tested with this app [unknown].
**Who.** Operator, Ari.

### 10.10 TD reads no frames from the bridge

**Signs.** The console log (Log page) shows the error **TD reads NO frames from the bridge file
while the bridge assembles N frames/s**. TD's cloud is frozen or empty while the console's Live
view still moves: the bridge is delivering and TD's reader is stuck. This is not a bridge
restart (10.3).

**Do.**
1. Operator: log it and tell Ari.
2. TouchDesigner, Point Cloud page: `Udpactive` off, then on (the console's own advice for this
   alarm). If the alarm stays for 30 seconds more: reopen TD as card 10.5 steps 2-4. [Ari to
   confirm which of the two comes first, A10.]
3. At the next break: re-learn TD's background on the empty stage (7.1 step 11).

**Who.** Operator, Ari.

---

### 10.11 People on stage, but /track or presence is empty or short

1. **Console Live view, /track panel says "waiting for background":** stage clear if possible,
   padlock off, **Stage is empty now**, 30 seconds, padlock on. A phone that started streaming
   after the console booted can leave the background unlearned until this is pressed (#59).
2. **A performer missing at the edge or at the back:** the stage cut is too tight. Show Wall
   Plane in TD and "Show cut points (dimmed)" in the console: if the performer is past the pink
   plane or under the floor cut, move the wall back or lower the cut (rule 16: a placement
   change). The console's amber message appears only when every point is cut.
3. **An inverted performer missing outside the cyr act:** expected on the default settings
   (9.1). Do not apply the preset with two people on stage.
4. **Still empty:** the person model (Rig health "YOLO worker" row: restarts and the last
   reason). Tell Ari with the clock time. If the reason is "did not answer within" the limit and
   restarts repeat, Settings > Vision > YOLO answer limit (1.5 s by default) to 3 s is the
   prepared change, padlock off and on (rule 16 does not apply: not a placement change); only
   with Ari's OK.

---

## 11. End of day: backup and handover

Every evening, and after the alignment on Tuesday. About 30 minutes.

1. **Re-check at O** (7.3): the day's drift reading.
2. **Recordings stopped:** padlock off; All phones > **Stop recording**; Live view side panel,
   "Client output (F1 contract)": **Record /track** off (while on it reads "Recording" and the row count);
   padlock on.
3. **Phones to Standby** (the top-bar Standby acts on every phone and disarms Auto-recover):
   padlock off, Standby, padlock on. Capture stops, screens go dark, the phones stay reachable
   and charging [designed]. In the morning, Start show (padlock off, Start show, padlock on)
   brings them back and arms Auto-recover again (5.3).
3a. **Restart the console** after Standby: close its window, which stops it for good, then
   start it again from `WebConsole\windows\run.bat`. The three-second restart in that script
   fires only when the console exits by itself; closing the window is how you stop it (rule 1,
   card 10.4). Under eight phones its memory grows about 0.6 MB a minute [simulated, 12 Nov
   soak], so a daily restart keeps a three-day run well clear of trouble. Three things to know
   before you press it:
   - **Do it now, not before a show.** After a console restart `/track` carries no performers
     for about 34 s while the engine relearns the empty stage [simulated, 12 Nov; #70 is open
     and holds a design for shortening it, with nothing built].
   - **Settings, the performance preset and Record /track all come back.** Since 17 November
     the console saves the Record /track switch and the next start resumes recording **into a
     new file**, saying so in its log. If the recording is meant to be off overnight, switch it
     off in step 2 and check it is off after the restart. Two log lines mean it did not come
     back on its own and the button needs pressing again: `config.json was not saved` and
     `Record /track NOT resumed`.
   - **If the start script says another console is already running,** it has tried three times,
     five seconds apart, before saying so, because Windows releases a dead console's lock a few
     seconds late. So that message can take about fifteen seconds to appear, and a window that
     sits there for that long after a crash is the retry rather than a hang.
4. **Snapshot** on the show PC, in Git Bash, USB drive in (on the show PC it is E:, `/e` in Git
   Bash):
   `./Tools/backup_state.sh /e`
   It prints `backup: /e/<date-time> (<size>)`. Write that name and size in the chat. It only
   reads the checkout [measured on the development Mac]. On GitHub's Windows test machine the
   backup, a fresh restore and a refresh pass end to end [simulated: on the project's Windows test
   runner, last green on 10 November 2026; the runner has been blocked since]. Never run on the show PC
   [unknown].
5. **Refresh the standby:** the USB drive into the standby. Check its drive letter in File
   Explorer there (it may not be E:) and use it below as `/<letter>`. On the standby, close its
   console window, its bridge window and TouchDesigner (Don't Save) if open, then in Git Bash:
   `bash /<letter>/<date-time>/restore_state.sh /c/Show`
   (the folder that holds `TDStage`, not `TDStage` itself). It refuses the show PC itself and
   a standby with a console running, and changes nothing when it refuses
   (`Notes/Stroud-Standby-and-Restore.md` 2.3). Then open the standby's show .toe in
   TouchDesigner and leave it running (10.7).
6. **Copy the logs** to the SSD, into a folder named with the date: `WebConsole\logs` (the
   console log, /track recordings, F1 dumps) and the day's readings (`C:\Show\readings`).
7. **Takes** (recordings on the phones): [open question C10: how they leave the phones at
   Stroud, and where the second copy goes]. The app keeps them in its own folder, visible in
   the iPhone's Files app [designed]; copying them to the SSD from the phone has not been
   tried. Copying off a phone needs its USB-C port, which the PoE adapter uses: copy with that
   phone's capture stopped (after Standby), then re-seat the adapter and check its Link line
   reads Ethernet. Rough size: 140-220 MB per phone per minute of recording with colour
   [measured on rig, two takes]; for example 30 minutes recorded on each of six phones is
   25-40 GB. Plan Thursday's copy time from the minutes actually recorded.
8. **Handover message** in the chat:

```
Stroud handover, <day>, <time GMT>
Snapshot: /e/<date-time> (<size>). Standby refreshed: yes / no (<time>)
Re-checks at O: <time> spot.err <m>; <time> spot.err <m>; ...
Alarms and failures: <time> <card> <what was done>
Settings or placements changed: <what, who, why>
Recordings: <sessions>; logs copied: yes / no; takes copied: yes / no (method, where)
Phones running without colour: <none, or which>
Open for tomorrow: <...>
```

Ari replies in his morning (Stroud evening or night) with anything to change before the
next morning's check.

**Thursday:** the same, then the final copies before pack-down (2.4). Keep the takes on the
phones until two copies exist (the SSD and the second drive) and Ari has checked one.

---

## 12. Open questions

Only the client (C) or Ari (A) can answer these.

**For Default Ltd**
- **C1.** Who is the tracking operator, and who is the stand runner during performer sessions?
  (This plan staffs the stands, #44.)
- **C2.** Call times for each day; whether the performance area can be empty and still on
  Tuesday from 13:15 to about 14:45 for the alignment, the background learn and the spot check,
  with screens and gauze hung before 13:15; whether Monday 23 has access.
- **C3.** The phones: model (refurbished iPhone 15 Pro?), count (six as confirmed, or eight),
  iOS version, spares.
- **C4.** The network and power kit: switch (GS316EPP?), adapters, router, UPS, Cat6 lengths;
  who orders and who brings them; a spare switch; the PoE bench test (#33) and who runs it;
  the switch's own page address (4.2).
- **C5.** The standby: is Mat Collishaw's RTX 4090 PC (the backup machine in the 20 October plan)
  available to be prepared as the tracking standby before Stroud, with a TouchDesigner licence,
  and with the client's content if the content must survive a switchover?
- **C6.** Does the real-time content run on the show PC in the same TouchDesigner as the
  tracking, or in its own? Which TouchDesigner licence is on the show PC and the standby (more
  than six phones need Commercial or Pro)?
- **C7.** Where does the client bus receive /track (127.0.0.1:7000 on the show PC?). Is F1 0.4
  used at Stroud? Is NDI needed?
- **C8.** What should the content do when /track goes quiet for a few seconds (bridge or console
  restart) or a few minutes (switchover)? Do the client's /track receiver and F1 client
  reconnect on their own?
- **C9.** Remote access: Tailscale allowed on the show PC? Which screen-sharing tool? The
  satellite connection's type and upload speed? Which video-call and chat tools?
- **C10.** Recordings: who holds the written consents; which sessions are recorded; how the
  takes come off the phones (there is no Mac on site in this plan), where they and their second
  copy go, and how long a copy takes.
- **C11.** Overnight: can the PC, switch and router stay powered, and is the venue secure?
- **C12.** The venue's 3D model (promised 23 October), the projector 2 position, and permission
  to tape the floor.
- **C13.** The markers: A3, 3D printed; their printed size measured (a photo next to a ruler).

**For Ari**
- **A1.** The release line (1.4): the code after the landing, the tox (v89 or v87), a stamped
  TestFlight build for the UK phones.
- **A2.** Version 2 of this plan after Wednesday: every **[to be filled after the 18 November session]** line.
- **A3.** Decided 10 November: ARKit on every phone at Stroud (#42). Colour from every phone fits one gigabit link (600 Mbit/s at 8 phones [designed]); the gate is the real phones through the real switch at the get-in.
- **A4.** Live hours from Sydney (1.2 is a proposal).
- **A5.** The anchor phone: phone 2 proposed (6.2).
- **A6.** The Stroud marks list and marks file for the frame check (7.2).
- **A7.** The bridge-outage behaviour (analysis, Stroud item 2): keep today's 2-3 seconds blank,
  or the other option measured.
- **A8.** Who may change TouchDesigner on site, and how a change is saved (rule 5).
- **A9.** Whether a console started on the standby with its cable out (no phones, no link) is
  safe to leave running while the switch is decided (10.7, Decide).
- **A10.** TD reading no frames from the bridge (10.10): `Udpactive` off and on first, or
  reopen TD; and whether TD's background must be re-learned after either.
- **A11.** The side-row layout has never been simulated for alignment: run the alignment
  simulations on `study_6` before this version
  (7.1 step 3).

---

## 13. Sources

`Notes/Plan-2026-10-25-Stroud-Round.md`; `Notes/Stroud-Coverage-Layout.md`;
`Notes/Stroud-Standby-and-Restore.md`; `Notes/Windows-Show-Machine-Setup.md`;
`Notes/Windows-TD-Audit-2026-11-09.md`; `Notes/Bandwidth-Decision-42.md`; `Notes/Fallbacks.md`;
`Notes/System-Analysis-2026-11-09.md` (4.4-4.5, 5.3, 6); `Notes/TASK-BOARD.md` (the re-check
cadence); `Notes/Sydney-Test-Day-2026-11-11.md` (its rules, set-up and cards W2-W7, W16);
`Notes/Meeting-2026-11-03-Mathias.md`; the 3 September contract meeting transcript;
`EmailChain.md`; the Stroud test plan of 20 October (the client's own Stroud test plan of 20 October);
issues #24 to #29, #31, #33, #42, #44, #45, #70, #71 and #74; the console and bridge sources
this plan describes (`WebConsole/server.py`, `static/app.js`, `settings.py`, `calib_check.py`,
`doctor.py`, `windows/*.bat`, `Tools/link_test.py`, `Tools/phone_session.py`,
`TD/newtox/tdp4_bridge.py`, `tdp4_receiver.py`, `tox_dats/gpu_exec.py`); and the phone app's
`ShowController.swift` and `Telemetry/ShowTelemetry.swift` (a relaunched phone's screen and
movement reference).
