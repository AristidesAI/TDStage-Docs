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
| saved settings ignored | config.json has a bad 'settings' block: fix or delete it, then restart the console. Defaults are in use meanwhile. |
| Telemetry listener failed | Another process holds the port. Find it with: lsof -nP -iUDP:9001 (Windows: netstat -ano -p udp), stop it, or start the console with --listen <free port> and use Retarget telemetry. |
| battery low / stopped charging | Reseat the phone's USB-C / PoE power. A show phone must run on mains; check the hub port is powered. |
| thermal / frame-rate ceiling lowered / capture age | Phone is hot: Blackout its screen, drop the RGB plane (depth+conf), shade it or add airflow. Serious/critical lowers fps and adds capture latency. |
| depth grid is | The phone's format picker fell back. Stop and Start streaming; if it repeats, switch the capture path (Device > Capture) and back. |
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
| vision restart failed | The service could not be restarted from here. Restart the console (Ctrl-C and run it again; run.bat / show_mac.sh restart it on their own); the full traceback is in logs/console.log. |
| config backup failed | The console could not copy config.json into backups/ (disk full, or the folder is not writable). Saving still works; free some space or fix the folder's permissions and the next save backs up again. |
| /track recorder | Writing the /track recording failed (disk full, or logs/ not writable). Turn Record /track off and on again; the console still holds the last 60 s in memory (/api/track/trace). |
| direct pong from | A phone's clock-sync reply reached the /ctl socket but could not be read. Clock sync still runs on TD's copy of the reply; an older app build is the usual cause: install the current one. |
| config.json did not parse | The console started from the newest backup (backups/ beside config.json); the broken file is kept beside it. Check the roster and markers; if the backup is older than wanted, stop the console, copy another backups/config-*.json over config.json and start it. |
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
| YOLO backend failed | pip install ultralytics in the console's Python, then restart. Apple Vision is used meanwhile. |
| person observer not started / settings: .*hook / settings apply failed / standby rate | Restart the console; if it repeats, the full traceback is in logs/console.log. |
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

## When none of these match

Check the console log first: it names the device and the time, which usually
narrows a vague fault to one phone. Then confirm the stream is actually
arriving before changing anything else, because a dead link produces symptoms
that look like a dozen different faults.
