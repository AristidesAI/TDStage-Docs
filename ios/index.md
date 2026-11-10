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
> parked on 6 November 2026 rather than maintain two. Almost everything here
> holds for both, because they share the settings, the wire format, the
> recorder and the whole user interface. The differences below are the ones
> that change a number or an answer.

| | TDStage AR, on the rig | TDStage, parked |
|---|---|---|
| Capture | ARKit scene depth | AVFoundation raw depth |
| **Depth grid** | **256×192 on every LiDAR iPhone.** It is ARKit's grid, so a 12 Pro and an 18 Pro send the same one | The largest float depth grid AVFoundation offers, which is 320×240 on every LiDAR iPhone from the 12 Pro on |
| Confidence plane | A real per-cell confidence from the sensor | A validity mask: 255 where depth is finite and positive, 0 where it is not |
| Person matte | ARKit's own, produced in the same frame as the depth, nothing to align | Vision, a separate inference on a separate clock, which can disagree at the silhouette on a fast performer |
| Capture to send | 62 to 78 ms, measured with two phones on 28 October | 37 ms, measured with one phone the same day. Different phone counts, so the gap is not a clean comparison |
| `stage.stabilization` | Read | Ignored |

[What TDStage AR adds](arkit.html) documents the depth conditioning pass and
the twenty-odd settings that steer it, which exist only in that app. Why the
project chose the slower, lower-resolution path is on
[Why it is built this way](../reference/design.html): edge bleed at a
silhouette turned out to cost more than resolution, and the A/B between the two
capture paths was never run.

The phones are pure streamers. They capture raw LiDAR depth and send it. By
default no rendering, no cleanup and no tracking happens on a phone: Raw
Streamer Mode is on, and the optional on-phone stages behind it (lens
rectification, QR marker detection, person and pose detection) are off. They
exist for measurements and for calibration, and the pose detector's results
never reach the wire. See [The LIVE page](live.html) and the
[Settings reference](settings.html).
