---
title: iOS app
nav_order: 4
has_children: true
---

# iOS app

The phones are pure streamers. They capture raw LiDAR depth and send it. By
default no rendering, no cleanup and no tracking happens on a phone: Raw
Streamer Mode is on, and the optional on-phone stages behind it (lens
rectification, QR marker detection, person and pose detection) are off. They
exist for measurements and for calibration, and the pose detector's results
never reach the wire. See [The LIVE page](live.html) and the
[Settings reference](settings.html).
