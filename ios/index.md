---
title: iOS app
nav_order: 4
has_children: true
---

# iOS app

{: .warning }
> **Two apps exist, and these pages describe the one that is parked.** The
> phones on the rig run **TDStage AR**, which captures through ARKit. These
> pages were written for **TDStage**, the AVFoundation app, which the project
> parked on 6 November 2026 when the show was set to run TDStage AR on the
> ARKit path only (issue 31). Almost everything here holds for both, because
> they share the wire format, the recorder, the 57 settings keys the parked app
> has, and most of the interface: the shell and the RECORD and PLAYBACK pages
> are the same code within a few lines. TDStage AR's LIVE page adds Capture
> path, Edge bleed and Person only, and 22 settings keys the parked app does
> not have. The differences below are the ones that change a number or an
> answer.

TDStage AR carries **both** capture paths, behind `stage.capture` (default
`arkit`, switchable on its LIVE page). Every AVFoundation figure below was
measured on that path inside TDStage AR; the parked app has not been measured
since it was parked.

| | TDStage AR, on the rig | The AVFoundation path |
|---|---|---|
| Capture | ARKit scene depth | AVFoundation raw depth |
| **Depth grid** | **256×192 on the iPhone 18 Pros this project has read** (issue 18, 25 October). Apple gives 256×192 as ARKit's streaming grid, so a 12 Pro should send the same one, which nobody here has read. The grid follows the app's 4:3 video format pick: before that fix one phone reported 256×144 on hardware | The native float grid of the first video format that offers depth; the app does not ask for the largest, and `stage.depthgrid` is stored and ignored. Apple gives AVFoundation streaming depth as up to 320×240; this project has read 320×240 on one iPhone 18 Pro, never on a 12 Pro Max or a 16 Pro Max |
| Confidence plane | A real per-cell confidence from the sensor | A validity mask: **2** (high) where depth is finite and positive, 0 where it is not. With no confidence map every kept cell reads as high, so a receiver's confidence threshold separates nothing |
| Person matte | ARKit's own, produced in the same frame as the depth, nothing to align. **Off by default** (`stage.persononly` false); the session does not even request it unless an operator turns it on | A Vision matte on a separate clock, which can disagree at the silhouette on a fast performer. **The parked app has none at all** - this is TDStage AR's own AVFoundation path |
| Capture to send | 62 to 78 ms on phone 1, two phones streaming, 28 October | 37 ms the same day on phone 2, after it was switched to the AVFoundation path mid run. Two different phones, one switched halfway, so the gap is not a clean comparison |
| `stage.stabilization` | Read | Ignored |

[What TDStage AR adds](arkit.html) documents the depth conditioning pass and
the twenty-odd settings that steer it, which exist only in that app. Why the
project chose the slower, lower-resolution path is on
[Why it is built this way](../reference/design.html): the ARKit path is the one
with measured evidence, and its per-cell confidence is what the edge cull
reads, while the AVFoundation path's edges and limbs were never measured. The
same-phone A/B between the two paths has no recorded result.

The phones are pure streamers. They capture raw LiDAR depth and send it. By
default no rendering, no cleanup and no tracking happens on a phone: Raw
Streamer Mode is on, and the optional on-phone stages behind it (lens
rectification, QR marker detection, person and pose detection) are off. They
exist for measurements and for calibration, and the pose detector's results
never reach the wire. See [The LIVE page](live.html) and the
[Settings reference](settings.html).
