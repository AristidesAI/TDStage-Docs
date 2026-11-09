---
title: How far each part is proven
parent: Reference
nav_order: 7
---

# How far each part is proven

Every component, what state it is in, the evidence for that, and the level that
evidence supports. **A claim on this page without evidence beside it is a
defect in this page**, not a thing you may assume.

This page is generated from the system repository's own README, which is the
copy the people writing the code maintain. Do not edit it by hand. Regenerate
it with:

```
python3 tools/gen_status.py
```

**Status on 2026-11-09 (written against main `29e742f`; code unchanged since `81f7f31`, 7 Nov):
pre-production. Nothing has run on a stage yet.** The most phones placed and aligned together
so far is two, in a living room. The three-phone stage test planned for 7 Nov did not run. This page says what
exists, how far each part is proven, and what is still open. Each claim names its evidence. A
claim here without evidence is a defect in this page.

## The levels

- **Rig**: measured on real iPhones streaming into this stack, at home. Used only for things that do not depend on the room.
- **Living room**: real phones placed around one furnished room at home. A room, not a stage, so it says little about stage distances.
- **Simulated**: synthetic phones, replayed takes or CI runners. No live phone in the loop.
- **Designed**: the code and its self-tests exist. Never run on the thing it is for.

## Every component

| Component | State on 2026-11-09 | Evidence | Level |
|---|---|---|---|
| Phone app TDStage AR (separate repo `TDStageARKit`) | 1.2 (5), a Debug build of `f7fc7b4` plus the uncommitted 1.2 version bump. Installed directly on all three phones at 00:10 on 7 Nov, not through TestFlight. Not yet run in a session: the only use recorded after the install is the fake-phone rehearsal. Build number 5 was set on the build command line. The TDStageARKit project says 1.1 (4) in git and 1.2 (4) in its working tree, so git cannot rebuild this exact build | `Notes/Sydney-Test-Day-2026-11-11.md` 0.2 (`devicectl` read 1.2 / 5 on each phone); `TDStageARKit` working tree; TASK-BOARD, Distribution state | Rig (earlier builds); 1.2 (5) installed only |
| Phone app TDStage (`TDStage/` in this repo) | Out of scope since 6 Nov. Version 1.0 is installed on phone 1 but not used. It listens for /ctl on UDP 9010, the same port as TDStage AR, so force-quit it before a session | day plan header and 0.2; `Notes/AR-Audit-2026-11-06.md` finding 5 | none |
| TDP4 wire | Spec, phone packer, receiver, simulator. Two real iPhone frames pass the shipped receiver, but they come from the non-AR TDStage 1.0. TDStage AR's packer also sets frameFlags bits 1-4, and no TDStage AR frame is committed as a fixture. The phone's 20-byte packet header has no cross-language check (#50) | `TD/newtox/wire_fixture_test.py` (23 checks; it prints "iPhone18,2, TDStage 1.0"); repo `TDStageARKit`, `TDStageARKit/Net/PointCloudUDPStreamer.swift:810` | Rig (non-AR app) |
| Bridge | Real phones through it since 26 Oct. The packet rate of 12 colour phones (114.5k pkt/s) with 0 lost, on loopback only. No real 2.5 GbE card tested (#42) | `Tools/link_test.py`; PROGRESS 2026-11-03 | Rig, Simulated at 8-12 phones |
| TD GPU merge (`Mergegpu`; the tox is v87 today) | The show path. 60 fps at 8, 12 and 16 simulated streams on the dev Mac, measured on tox v69 on 26 Oct: depth+conf sims with no colour, through the old fan-out and the bridge, person model idle, no content. Not re-run on v87 or with colour. Atlas write about 1.7 ms of a 16.7 ms frame (8 colour phones' shape, synthetic, 3 Nov). TD cloud age with 3 real phones not measured (#11) | #11 comments 26 Oct 04:12Z, 27 Oct and 3 Nov | Simulated |
| TD CPU merge (fallback) | The fused person id is a rounded mean of track ids (#51, fix in progress) | `TD/newtox/hlib_grid.py:1175` | Simulated |
| Alignment | Two phones agreed to a 12.4 mm median gap on 28 Oct. That was before the floor-cell refinement (`dfbeb4c`) and has not been re-measured. Never tested at stage distances (#1, #24) | CHANGELOG 2026-10-28, corrected 2026-11-03 | Living room |
| Marker calibration | Never run end to end on a phone (#35) | `Tools/marker_pdf.py` (`8934b43`) | Designed |
| Calibration check (`/api/rig/calib`) | Never run on real phones (#41) | `WebConsole/calib_check.py`, CI | Designed |
| Person segmentation and /track | All simulated. Self-test 19-20 of 20 per scenario. Replays of recorded sims (27 Oct, round 3, swapped of crossings kept): walkers in their own costumes swap 0-3 times (1 of 56, 3 of 110, 0 of 22); walkers in one costume swap in 19-40 % of crossings (18 of 97, 4 of 18, 6 of 15, and 49 of 137 with 4 walkers and a sitter). Ring sim: 11 crossings, 0 swaps, and the live run re-acquired one track as a new id. Not checked on real bodies (#17) or with a plan-placed phone (#43). Clustering thresholds untested on bodies (#32) | `WebConsole/track_emit.py --selftest`; CHANGELOG 2026-10-27 (the round 3 replay table); TASK-BOARD snapshot 2026-10-27 (session A) | Simulated |
| Hands on /track | On the Mac's live config /track carries no hands: 0 in 2,328 performer frames of a take T1 replay. Keypoints switch on by themselves only where Apple Vision is absent (Windows), untested with phones | `49b2ae0`; `WebConsole/yolo_seg.py:157-163` | Simulated |
| Consensus view in TD (`consensus_view`) | The console's /track performers and hands drawn in TD, from a copy of each bundle (`TDSTAGE_TRACK_COPY`, sent even when the client bus is unreachable). Code, DAT callbacks and wiring steps exist; not yet built into the tox. Markers get TD's Flooroffset and trim; they sit on TD's cloud only while TD's stage level solve is off (with it on, Consensusstatus warns and gives the size). Tested on recorded bundles from a sim-fed console and a scratch console (zero performers: its stage was not learned) | `TD/newtox/consensus_view.py --selftest`; `Notes/Windows-TD-Audit-2026-11-09.md` section 3 | Simulated |
| F1 0.4 producer | Requirements check against the F1 0.4 draft and the Stroud plan. On the dev Mac on 27 Oct, with Default Ltd's decoder `sms_td.py` read from `~/Downloads`: 14 PASS, 4 BUILT, 0 FAIL, 7 NEEDS-RIG. That decoder is not in the repo, so a clone cannot reproduce those 14. The same tool in Windows CI at `81f7f31`: 7 PASS, 3 BUILT, 0 FAIL, 15 NEEDS-RIG (run 42259150264). Some PASS rows check plan geometry, not a measurement (ST-01). Multi-phone density and latency not measured (#29) | `Notes/Requirements-Conformance.md`; `Tools/requirements_check.py` | Simulated |
| Windows show machine | Installer, doctor and `show.bat` green on GitHub's GPU-less Windows runner at `81f7f31` (run 42259150264). 4 of the 13 completed runs after `1bdb822` (3 Nov) failed on one of two intermittent checks: the fan-out relay throughput check twice (`a2f159f`, `43ac618`) and the config-lock self-test twice (`b0b750c`, `b2147f6`). Each passed on the next push with no change to `udp_fanout.py`, `xplat.py` or the workflow. Not diagnosed. Not yet run on a real PC: CUDA, a phone over USB-C, NDI, TD reading the bridge file (#26, due 19 Nov) | `.github/workflows/windows-console.yml`; failed runs 41583622403, 41605399856, 42151112009, 42220963137 | Simulated |
| Heat | Two phones, 1.5 h each, plugged in, ambient not measured. Thermal serious after 7-9 min, never critical. Phone 1 held 30 fps at serious for 31 min, phone 2 held 25 (#31) | `Notes/Heat-Run-2026-10-28.md` | Living room |
| Latency | Capture to send: ARKit 62-78 ms (two phones), AVFoundation 37 ms (one phone), 28 Oct. Capture to TD output with one real phone (phone 2 on Wi-Fi, through the fan-out and the bridge, GPU path, 26 Oct): p50 about 123 ms, a sum of three stages: capture to fan-out output 95.7 ms (measured, phone hot), bridge to TD 10.4 ms (measured) and about 16.7 ms for one 60 fps output frame (assumed, not measured). A cooler phone would lower the first stage; that was not measured end to end. Capture to /track emit p50 35 / p95 54 ms with 2 simulated phones (3 Sep), before the consensus and YOLO path, not re-measured. TD cloud age with 3 real phones: not measured (#11) | heat-run note; #11 comment 26 Oct 01:48Z; PROGRESS 2026-09-03 | Rig (one phone), Simulated |
| Takes (record, replay) | Format v2, Swift and Python cross-checked. Three copies of take T1 replayed 2,748 of 2,748 frames byte-identical. The only real movement take on record is T1 (7 Sep, one phone, handheld, no IMU, not in git). `taketest` compiles this repo's `TDStage/Recording`: TakeFormat, TakeWriter and TakePlayer are byte-identical to TDStage AR `f7fc7b4`, TakeStore is not | CHANGELOG 2026-11-06; `Tools/taketest/` | Rig (one take) |
| iOS CI | Red in both apps (#48). TDStage AR at `f7fc7b4` (run 42220967993): 16 failing tests, which are 15 assertion failures and one crash in TelemetryHostClearTests (malloc "pointer being freed was not allocated"). The crash restarted the test host. The same suite passed 118 of 118 locally on iOS 26.5 on 6 Nov | #48; CHANGELOG 2026-11-06 | none |
| Distribution | TestFlight TDStage AR 1.1 (4), uploaded 3 Nov 08:35Z from an Xcode Organizer archive with empty build stamps. Its dSYM shows it contains the #49 fix's code (`83fb5ca`). Stops launching about 1 Feb 2027. The console's expiry warning cannot fire for it | archive record and dSYM (TASK-BOARD, Distribution state); `WebConsole/server.py:1954-1960` | none |

*Generated from the system repository's README (committed ecda386). 19 components.*

## Reading a level

Several rows carry a compound level — "Rig (one phone), Simulated", "Rig
(earlier builds)". That is not hedging. It means one part of the claim was
measured on real hardware and another was not, and the row names which is
which. Read the evidence column before quoting the row.

**Levels do not transfer.** A thing proven on one phone is not proven on eight;
a thing proven in a living room is not proven at stage distances, because the
room never tested the distance. A simulated result says the code does what it
was written to do, which is worth knowing and is not the same as the rig
working.

The strongest single caveat on the whole project sits in the status line above:
the most phones placed and aligned together so far is two, in a living room.
Anything that depends on more phones, or on a stage, is designed or simulated
until the stage test produces its own evidence.

See [Evidence and claims](../operations/evidence.html) for how a number earns
its way onto this table in the first place, and what not to claim.
