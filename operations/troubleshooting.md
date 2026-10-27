---
title: Troubleshooting
parent: Operations
nav_order: 9
---

# Troubleshooting

Symptoms the console can report, and what to do about each one.

This page is generated from the console's own fix hints, so it cannot drift
from the software. Do not edit it by hand. Regenerate it with:

```
python3 tools/gen_troubleshooting.py
```

Every row is a message the console raises, with the fix it offers. The console
shows the same text in its log and on the Rig health page, so what you read
here is what an operator sees at the desk.

| Symptom | What to do |
|---|---|
| TouchDesigner link off; start it with --td-link | Expected for a test or measurement console: a --config instance never drives TouchDesigner unless asked, because on link-up it pushes its own poses into TD's registration (2026-10-27: a scratch console moved phones 1-6 in the live tox). If this instance SHOULD own TD, stop it and start it again with --td-link (the dashboard's TD switch also turns it on, for this run only). The show console runs without --config and is never affected. |
| client outputs (/track, NDI) off; start it with --client-out | Expected for a test or measurement console: a --config instance never sends /track or publishes NDI unless asked, whatever its file says, so a copy of the show's config cannot drive the client bus (the same rule as --td-link). If this instance SHOULD send them, stop it and start it again with --client-out, or switch /track and NDI on from Live > Client output for this run. The show console runs without --config and restores both as it last saved them. |
| /track NOT restored | The saved /track target does not resolve on this machine (the line names it), so /track stays off rather than send to the default address. Fix the host on Live > Client output (or the network / DNS) and switch /track on: the save that follows keeps it on across restarts. |
| NDI NOT restored | NDI is not available on this machine (the line names the import error): cyndilib or the NDI runtime is missing, so NDI stays off; /track is unaffected. Install the NDI runtime and cyndilib (WebConsole/requirements.txt) and restart the console. |
| roster is a fresh seed: poses NOT sent to TouchDesigner | Check the roster, then press Push poses (the TouchDesigner panel). A seeded roster (a first boot, or a config.json that nothing in backups/ could replace) never pushes poses to TouchDesigner on its own, so TD keeps the registration it has. If the roster on the All phones page is the show's, Push poses sends it and ends this state (so does saving a pose edit). If it is not, stop the console, copy the right backups/config-*.json over config.json and start it again. |
| could not be applied .*trying the next backup | That backup holds a value of the wrong type (the line names it) and is skipped, left as it is in backups/; the console tries the next older one and a later line says which file it started from. Nothing to do unless that line says a new session was seeded. |
| saved settings ignored | config.json has a bad 'settings' block (the line names it): defaults are in use for what it held. Set the values you need in Settings; the next save writes a valid block and files the old config.json in backups/. No restart needed. |
| Telemetry listener failed | Another process holds the port. Find it with: lsof -nP -iUDP:9001 (Windows: netstat -ano -p udp) and stop it, or type a free port in the Dashboard's Telemetry port field and press Start in the top bar (it rebinds without a console restart), then use Retarget telemetry. |
| battery low / stopped charging | Reseat the phone's USB-C / PoE power. A show phone must run on mains; check the hub port is powered. |
| thermal / frame-rate ceiling lowered / capture age | Phone is hot: Blackout its screen, drop the RGB plane (depth+conf), shade it or add airflow. Serious/critical lowers fps and adds capture latency. |
| depth grid is .*not 4:3 | The phone picked a video format that is not 4:3 (the 16:9 case crops rows off the stage). Stop and Start streaming; if it repeats, switch the capture path (Device > Capture) and back. |
| stream left Ethernet | Check the PoE adapter and Ethernet cable. Wi-Fi adds ~8 ms and drops frames under load. |
| GB free | Export or delete old takes on the phone (Playback page) before recording again. |
| take list unreadable | Restart the app on the phone. If it repeats, export the takes and reinstall. |
| CRASH RECOVERED | Pull the crash log (Xcode > Devices > View Device Logs) and note the last failure cause line. One crash is survivable; a second one means a root cause. |
| watchdog healed | One heal is fine. Repeats point at network or thermal trouble on this phone: check its link and temperature. |
| SAFE MODE | The phone runs factory defaults. Fix the cause, push a profile (Device > Recovery > Push profile), then Restart app. |
| phone id collisions / sending as the same id | Two phones (or a phone and a replay or sim) use one Device ID, so their frames overwrite each other. Give each phone its own id: device page > Device ID, or the All phones page; stop any sim or take replay that reuses the id. |
| is not where this phone reports from | The typed host on the device page wins over the address the phone actually uses. Clear the host field (Device > Config) to follow the phone, or set it to the new address; if the phone moved between the cable and Wi-Fi, use the Cable / Wi-Fi host buttons. |
| commit(s) behind this checkout | Install the current build on this phone (Xcode Run on the cable, or a fresh TestFlight upload with ./Support/testflight.sh --upload after a bump) so it has the fixes this console expects. |
| state marker sizes | Phones hold different printed-marker sizes, so a calibration scales the stage wrongly on some. Set one size for the rig on the Markers page (Apply to all phones) and print at that size. |
| vision restart failed | The restart raised (the line names the error, logs/console.log has the traceback). Press Restart again: the YOLO worker respawns in its own process and the Apple Vision services start a fresh thread. If it fails the same way it is a code fault: report it with the log. |
| config backup failed | The console could not copy config.json into backups/ (disk full, or the folder is not writable). Saving still works; free some space or fix the folder's permissions and the next save backs up again. |
| /track recorder | Writing the /track recording failed (disk full, or logs/ not writable). Turn Record /track off and on again; the console still holds the last 60 s in memory (/api/track/trace). |
| direct pong from | A phone's clock-sync reply reached the /ctl socket but could not be read. Clock sync still runs on TD's copy of the reply; an older app build is the usual cause: install the current one. |
| could not be kept aside | The config folder is not writable or the disk is full (the error is in the line), so the broken file could not be copied aside and is still config.json itself; nothing can be saved until that is fixed. Fix the folder's permissions or free space: the next save then writes the state in use over config.json, no restart needed. (To run from another backup instead: stop the console, copy that backups/config-*.json over config.json, start it.) |
| could not be rewritten at boot | The config folder is not writable or the disk is full (the error is in the line): config.json still holds the file the console could not use. Fix the folder's permissions or free space; the next save writes the state in use over it, no restart needed (a broken file that lands in backups/ is skipped by every restore). |
| retuned defaults could not be saved | The config folder is not writable or the disk is full (the error is in the line). The retuned values are in use now; fix the folder and the next save writes them (until then every boot migrates them again). No restart needed. |
| no Python with ultralytics | Either install the vision requirements into the Python that runs server.py (the line names it; pip install torch torchvision, then pip install -r WebConsole/requirements.txt) or set TDSTAGE_YOLO_PYTHON to a Python that has ultralytics: on a Mac, Tools/show_mac.sh reads it from Tools/show_mac.local. The worker's interpreter is chosen when the console starts, so restart it after either fix (this one does need a restart). Apple Vision carries the person masks on a Mac meanwhile; doctor.py says which interpreter the worker resolved to. |
| worker venv python missing | TDSTAGE_YOLO_PYTHON names a file that is not an executable Python: fix the path, or unset it so the console's own interpreter is used, then restart the console (the interpreter is chosen at start). doctor.py says which interpreter the worker resolved to. |
| telemetry handler failed | The console's handler for that message raised (the line names the address and the error); the listener keeps running and every other message is still routed, but what that message drives (TD poses, a phone's row) was not updated. A wrong-typed value in config.json or an app build this console does not know are the usual causes; the traceback is in the console's own output (server.out / the terminal). |
| Telemetry listener stopped | The listener's socket itself failed (the line has the error: an interface going away is the usual cause). Click Listen in Settings to start it again; if it repeats, the full error is in logs/console.log. |
| config.json .*no backup to restore | No backup in backups/ both parses and loads (the line names any it had to skip), so a new 6-device session was seeded and written to config.json; the broken file is kept beside it as config.json.corrupt-<time>. TouchDesigner gets no poses from the seed until Push poses. Stop the console, fix that file (or copy a snapshot's console/config.json) over config.json and start it again. |
| config.json .*restored from backups/ | The console started from the newest backup that parses AND loads (the line names it, and any it skipped); the broken config.json is kept beside it as named. Check the roster and markers: a backup is taken at most once a minute, so the latest edits may be missing. If they are not the show's, stop the console, fix the kept file or pick another backups/config-*.json, copy it over config.json and start it again. |
| could not be applied .*a new session is seeded | A value in the saved config has the wrong type (the line names it) and no backup in backups/ loads either, so a new 6-device session was seeded and written to config.json; the file is kept as named. TouchDesigner gets no poses from the seed until Push poses. Stop the console, fix the value in the kept file and copy it over config.json, then start it again. |
| every frame arrives twice | Stop the fan-out relay (udp_fanout.py / windows\fanout.bat): with the bridge running, phones send to the bridge on :9003 and the console reads its file. Tools/show_mac.sh and windows\show.bat start the right pair. |
| TD reads NO frames from the bridge file | The bridge runs and TD's reader gets nothing from its file: TD reads a different file name (Udpport must equal the bridge's --port), or TD's tdp4_receiver text is older than the bridge's layout. Cycle Udpactive; if it persists, reload the tox's tdp4_receiver DAT from TD/newtox/tdp4_receiver.py. |
| TDP4 receiver is NOT running | In TouchDesigner: Point Cloud page, check Udpactive is on and Udpport is free (9004 behind the bridge, 9003 direct). The tox's log names the bind error; another process on that port (a second TD, the bridge on the same port) is the usual cause. |
| PHONE MOVED | Someone bumped the tripod. Calibrate this phone again; if the move was deliberate, re-lock its pose. |
| profile too large | One /ctl datagram holds ~9 KB. Drop unused keys from the profile. |
| simulator (failed / exited) | Check that python3 runs and TD/newtox/tdp4_sim.py exists; the full error is in logs/console.log. |
| AUTO-RECOVERY | The console restarted this phone's stream. Repeats mean a root cause: watch thermal, link type and capture age on its device page. |
| no telemetry and no point data | Open TDStage on the phone (it may be asleep or closed), then check its destination IP points at this machine: Retarget telemetry. |
| TouchDesigner link lost | Open TD with TDStageConductor.tox, then check Settings > TouchDesigner host/port (default 9006). Ping on the Stage page confirms it. |
| TD send failed | TD host unreachable from this machine: check the TD host/port in Settings, and the firewall. |
| REJECTING the stream | Receiver wedge (#20): in TD toggle Udpactive off and on, or restart the bridge process (tdp4_bridge.py). |
| WITHOUT the TDP4 bridge | Start the bridge: python3 TD/newtox/tdp4_bridge.py --port 9004 (show.bat and Tools/show_mac.sh start it). TD switches to it within 2 s. |
| no IP known | Set the phone's host on its device page, or wait for its first telemetry packet (the console learns the address from it). |
| send failed | Phone unreachable: check it is on the network and its IP has not changed (device page shows the last seen address). Ping it. |
| fan-out stopped | Start the fan-out again (Live > Ingest) or run Tools/show_mac.sh; until then TD receives nothing on 9004. |
| Coordinator stopped listening | Click Listen in Settings to resume receiving telemetry. |
| rig align | The two phones need overlapping floor in view. Move the anchor phone or calibrate both on markers. |
| F1 producer | Check the F1 settings (Live > Client output); the WebSocket port (9001/tcp) must be free. |
| YOLO backend failed | A fault while starting the YOLO observer (the line names it, logs/console.log has the traceback): Apple Vision carries the person masks for this session. The backend is wired in when the console starts, so a console restart is what tries YOLO again; report the error if it repeats. |
| person observer not started | Press Restart on 'Person observer (Apple Vision)' in Rig health: it starts a fresh thread, no console restart. The traceback is in logs/console.log. |
| settings: .*hook | A code fault (the line names the module): that module keeps its own defaults and does not follow Settings. A console restart runs the same code and fails the same way: report it with logs/console.log. |
| settings apply failed / standby rate | Settings did not reach every module at boot (the line names the error). Change any value in that Settings group: each edit pushes the whole group again, no restart needed. The traceback is in logs/console.log. |
| retarget .* sent to 0 | No phone took the retarget: they need a known IP first (telemetry or a host set on the device page). |
| HEAL STORM | Something keeps killing this phone's stream: check its link (Wi-Fi drops, cable), thermal state and the app log; heals cannot fix a cause outside the app. |
| last failure cause | The phone's own account of why it last failed; the heal and crash lines around it say what it did about it. |
| cable address moved | Click Autofix on the phone (device page): it re-teaches the phone the Mac's new cable address. |
| cable_watch | The USB cable check itself failed (ifconfig / arp); the cable path may still work. Full error in logs/console.log. |
| sim loop / simulator stopped | Expected when a timed run ends. Tick Loop on the Simulator panel to keep it running; start it again from there or the Live view. |
| placement not applied / orientation not applied | The setting was saved but not applied to this view; reload the page. Full error in logs/console.log. |
| F1 note | Run the F1 bus on a different port from TD's telemetry (9000), or on another machine. |
| -> 4\d\d | The UI sent a request the server refused; the reply above says why. Reload the page if the UI is out of date. |
| -> 5\d\d | Server-side exception: the traceback is in logs/console.log. Report it with the request line above. |
## Where capture latency is going

When the console reports a phone's frames arriving late, it names
the stage of the capture path that is slowest. Each stage has its own
fix, because the cause is different in each case.

| Slowest stage | What it means and what to do |
|---|---|
| `delivery` | The capture framework itself is late (ARKit or AVFoundation): a hot phone delivers late. Blackout the screen and cool the phone; on TDStage AR the AVFoundation capture path delivers sooner (no ARKit confidence). |
| `prep` | Depth and colour preparation on the phone is slow: drop the rgb plane (depth+conf); on TDStage AR also person gating. Under thermal pressure the GPU and CPU clock down. |
| `hop` | The main thread is busy when a frame is ready: blackout the screen (SwiftUI stops redrawing) and close any on-phone page with live stats. |
| `main` | Main-actor work per frame (marker detection, skeleton) is high: turn markers/skeleton off outside calibration. |
| `queue` | The previous frame is still being sent: the link is slow or saturated. Check Wi-Fi vs Ethernet, and the planes (rgb doubles the bytes). |
| `pack` | Packing the frame is slow: drop the rgb plane; under thermal pressure the CPU clocks down. |
| `socket` | The socket takes the datagrams late: Wi-Fi contention, or the wired adapter is saturated or on the wrong VLAN. Check /device/link on the phone's page and the switch port. |

## When none of these match

Check the console log first: it names the device and the time, which usually
narrows a vague fault to one phone. Then confirm the stream is actually
arriving before changing anything else, because a dead link produces symptoms
that look like a dozen different faults.
