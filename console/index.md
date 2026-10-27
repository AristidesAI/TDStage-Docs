---
title: Console
nav_order: 3
has_children: true
---

# The WebConsole

The WebConsole is the browser application the technician and the operator use to
run the phone rig. It is a single Python process (`WebConsole/server.py`) plus a
web page served from `WebConsole/static/`. Open it at
**http://localhost:9080**.

It replaced the old macOS Stage Coordinator app. There is nothing to install on
the operator's machine beyond a browser. To reach it from a tablet side stage,
browse to `http://<show-machine-ip>:9080`.

## What it is for

Four jobs, in the order you meet them at a get in.

1. **Manage the phones.** The roster, each phone's name, IP, colour, stage pose
   and field of view, its AR marker assignment, and every phone setting that can
   be changed remotely. Start, stop, blackout, ping, calibrate, heal.
2. **Place the rig.** The 3D stage plan, the marker plan at true printed size,
   and the live point cloud from the phones so you can see what each one
   actually sees.
3. **Carry the client outputs.** The `/track` OSC stream of performer positions
   and hands, the F1 WebSocket field, the NDI image of the cloud, and the person
   consensus behind them.
4. **Tell you why something is broken.** The Rig health panel, the Log page, and
   `GET /healthz` for a watchdog.

## What it owns

| Thing | Where it lives |
|---|---|
| The phone roster, poses, marker plan, person figures | `WebConsole/config.json`, with rotating copies in `WebConsole/backups/` |
| Each phone's last known good profile | `WebConsole/profiles/phone-<id>.json` |
| Every runtime tunable | the `settings` section of `config.json`, schema in `settings.py` |
| The log | the Log page and `WebConsole/logs/console.log` (rotating, 5 files of 5 MB) |
| Phone telemetry in | UDP, the port on the Dashboard (`--listen`) |
| `/ctl` control out to each phone | UDP to each phone's own control port, 9010 by default |
| The TouchDesigner conductor bus | UDP OSC out to `tdHost:9006`, replies to the console's telemetry port |
| `/track` out | UDP OSC to the client bus, 127.0.0.1:7000 by default |
| The F1 field | TCP WebSocket, port 9001 by default |
| The NDI source | `TDStage Point Cloud`, 960x540 at 30 fps by default |

## What it does NOT own

This is the part that matters during a show.

**The console never feeds TouchDesigner's point cloud.** The phones stream TDP4
to the TDP4 bridge (or to a fan out). The bridge hands whole frames to
TouchDesigner and to the console through one memory mapped file, and each reader
keeps its own place in that file. The console is a second reader, not a relay.
Nothing the console does, including quitting, removes a frame from
TouchDesigner's input.

**Closing the console mid show has zero effect on TD's cloud.** What stops is:

- phone telemetry and health (so no battery, thermal, fps or pong readings)
- `/ctl` control (so no start, stop, blackout or calibrate from the browser)
- auto recover
- the client outputs: `/track`, the F1 WebSocket and NDI
- person consensus, the Live view and hand tracking

TouchDesigner keeps ingesting, merging, cleaning, fusing and driving the
visuals exactly as before.

**Cleanup and fusion for TD's own cloud stay in TouchDesigner.** The console
runs its own segmentation, but only to feed the client outputs. It never writes
back into TD's cloud.

**The console does not start anything by itself.** No background loop launches a
process or reaches for a phone. Every repair, fan out start, profile push and
heal is something an operator pressed. Auto recover is the one supervised
exception, it is off by default, and `Start show` is what arms it.

## How the phones reach both readers

This is the current path, since 2026-10-27:

```
phones ──UDP :9003──▶ tdp4_bridge.py ──┬──▶ TouchDesigner  (reads the mmap file, "9004")
                                       └──▶ WebConsole     (reads the same file)
```

`tdp4_bridge.py` binds the phone facing port itself and hands whole assembled
frames to both readers through one memory mapped file, published under the name
`9004` so the tox's `Udpport` needs no change. Each reader keeps its own place in
the file. Nothing copies packets.

**`udp_fanout.py` is legacy, and optional.** It still exists and still works,
and the console can start and stop it, but it is not the show path. It copied
every datagram with three syscalls and lost packets above about 30,000 per
second, and eight phones with colour are 49,000. The bridge alone received
61,000 per second with no loss. Keep the relay only for a no bridge CPU path.

The architecture **diagram** in the repo's `CLAUDE.md` still shows the relay as
the show path. That diagram is stale. Its **port table** is still correct and
authoritative.

## The two machines

On the show machine (Windows, RTX 4090) the tracking side is one PC: the TDP4
bridge, the console, and TouchDesigner with the tox. Phones arrive over PoE
Ethernet, one cable each. See [Running the console](running.html).

On a Mac, `Tools/show_mac.sh` starts the same two processes.

## Operating it from off site

The UI works over Tailscale, but the Live view is capped for any client that is
not on the LAN: **5 frames per second and 20,000 points shared across all
phones**. A `100.64/10` Tailscale address counts as off LAN, because it is a
tunnel. `WebConsole/README.md` describes remote operation without that caveat.
Everything else in the UI behaves the same remotely. Details in
[Running the console](running.html).

## Where to go next

- [Running the console](running.html) for install, start commands and every CLI flag.
- [The browser UI](ui.html) for a walkthrough of each page and control.
- [HTTP API](api.html) for every endpoint, and which are POST only.
- [Settings reference](settings.html) for the tunables, their defaults and ranges.
- [Troubleshooting](troubleshooting.html) for symptom first fixes.
