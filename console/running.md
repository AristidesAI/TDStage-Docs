---
title: Running the console
parent: Console
nav_order: 2
---

# Running the console

## What it needs

The core console boots on plain Python 3.9 or newer. The Live view, YOLO person
segmentation and MCAP export need the packages in `WebConsole/requirements.txt`.
One virtual environment serves both the console and the YOLO worker.

`torch` and `torchvision` are deliberately not in `requirements.txt`. They are
installed first, from the right index, so that `ultralytics` finds them already
satisfied instead of pulling a CPU build from PyPI.

On Windows the installer targets Python 3.12, falling back to 3.11. Those are
the versions CUDA torch wheels exist for. `doctor.py` fails below 3.9 and warns
on Windows for anything outside 3.11 and 3.12.

## Install on macOS or Linux

```bash
cd /Users/ari/Documents/XcodeProjects/TDStage/WebConsole
python3 -m venv .venv && . .venv/bin/activate
pip install torch torchvision
pip install -r requirements.txt
python3 doctor.py                 # environment check, read only
```

Keep the `TD/newtox` folder next to `WebConsole`. The console imports
`tdp4_receiver`, `tdp3_receiver` and `rgb_orient` from there, and will not serve
the Live view without them.

## Install on Windows (the show machine)

1. **Get the repo.** `git clone`, or download the ZIP and unzip. Keep
   `TD\newtox` beside `WebConsole`.
2. **Install Python 3.12 x64** from python.org with "Add to PATH" ticked, or
   `winget install -e --id Python.Python.3.12`.
3. **Run `WebConsole\windows\install.bat`.** It creates `WebConsole\.venv`,
   installs torch from the CUDA 12.6 index when `nvidia-smi` is found and from
   the CPU index otherwise, then `requirements.txt`, then runs `doctor.py`.
   Safe to re run. Override the torch index with
   `set TORCH_INDEX_URL=https://download.pytorch.org/whl/cu130` beforehand, or
   the Python version with `set TDSTAGE_PY=3.11`.
4. **Run `WebConsole\windows\firewall.bat` once.** It asks for Administrator and
   adds four inbound rules:

   | Rule | Protocol and ports | Scope |
   |---|---|---|
   | TDStage Console UDP | UDP 9001, 9003, 9013 | any |
   | TDStage TouchDesigner UDP | UDP 9000, 9004 | any |
   | TDStage Console HTTP | TCP 9080 | LocalSubnet and 100.64.0.0/10 |
   | TDStage F1 WebSocket | TCP 9001 | LocalSubnet and 100.64.0.0/10 |

5. **Check with `WebConsole\windows\doctor.bat`.** Every line should read OK,
   and the compute section must say `yoloDevice=auto resolves to cuda`. If it
   says cpu, the CUDA torch wheel did not install: set `TORCH_INDEX_URL` and run
   `install.bat` again.

YOLO weights (`yolo26n-seg.pt`, `yolo26n-pose.pt`) ship in `WebConsole/models/`,
so the install works offline once pip has run.

Run Python with `PYTHONUTF8=1`. The `.bat` files set it. Without it, logs and
`config.json` hit the cp1252 codepage.

## Start commands

### The show machine, everything at once

```
WebConsole\windows\show.bat
```

It starts the TDP4 bridge in its own window, waits two seconds, then the console
with a watchdog, and opens the browser. Both restart themselves if they exit.
Closing a window stops that process.

The bridge command it runs is:

```
TD\newtox\tdp4_bridge.py --port 9003 --shm-port 9004
```

The bridge receives the phones on UDP 9003 in its own process and publishes
whole frames through a memory mapped file named for port 9004, which is what the
tox's `Udpport` expects. TouchDesigner and the console both read that one file,
each keeping its own place in it.

**There is no fan out relay in front of it, and there should not be.**
`udp_fanout.py` is legacy. It lost packets above about 30,000 per second, and
eight phones with colour are 49,000; the bridge alone took 61,000 per second with
no loss. `windows\fanout.bat` and the console's Start fan-out button remain for
the no bridge CPU path only. The architecture diagram in `CLAUDE.md` still shows
the relay as the show path and is stale; its port table is correct.

### The show machine, console only

```
WebConsole\windows\run.bat
```

which runs, in a restart loop:

```
python server.py --http 9080 --listen 9001 --tdp4-port 0
```

Extra arguments to `run.bat` pass straight through to `server.py`.

### A Mac, everything at once

```bash
./Tools/show_mac.sh
```

Same two processes, same ports, each restarted two seconds after it exits.
Ctrl-C stops both.

### A Mac, console only

```bash
cd WebConsole && . .venv/bin/activate
python3 server.py --http 9080 --listen 9001 --tdp4-port 0
```

Use `--listen 9001` whenever TouchDesigner is on the same machine. TD binds UDP
9000 for phone telemetry, and the console cannot have it as well.

## Every CLI flag

| Flag | Default | What it does | When to change it |
|---|---|---|---|
| `--http PORT` | `9080` | TCP port for the browser UI and the whole HTTP API. | Only if something else holds 9080, or you are running a second instance. |
| `--listen PORT` | not set, falls back to the saved value in `config.json`, else `9000` | UDP port the console binds for phone telemetry (`/tdlidar/<id>/device/*`) and for TouchDesigner's health and pong replies. | Set `9001` whenever TouchDesigner runs on the same machine, because the tox binds 9000. The phones must then be pointed at it, which the Dashboard's telemetry retarget button does. |
| `--no-autostart` | off | Do not bind the telemetry listener at boot. | For a bring up where you want the port left free. Start it later from the toolbar. |
| `--tdp4-port PORT` | `9003` | A direct TDP4 UDP listener on the phone facing port. It is bound only while nothing else claims it, and the console hands it straight back when the tox mirror is alive. `0` disables it. | `0` on the show machine, where TouchDesigner must be able to bind 9003 the instant it launches and the console reads the bridge file instead. Another number to run a measurement instance beside TD. |
| `--sim-port PORT` | `9013` | A second TDP4 listener the console always owns. The built in simulator is aimed at it. A real phone can be pointed here when TD is not in the loop. | Rarely. Change it only to avoid a clash, and then set the fan out's second target to match. |
| `--f1-port PORT` | `9001` | The F1 0.4 draft WebSocket (SMSF, SMSP, SMSS). **TCP**, so it coexists with a UDP `--listen 9001`. `0` turns it off. | `0` when no client machine is consuming it. |
| `--f1-hz RATE` | `15.0` | Rate of the F1 field. | Only if the client asks for a different rate. |
| `--config PATH` | `config.json` beside `server.py` | The config file to load and save. Phone profiles move with it, into a `profiles` folder beside it. | Always, when you run a second instance for a test or a measurement. |

### What `--config` does to a fresh instance

If the file named by `--config` does not exist yet, the console starts with the
TouchDesigner link **off**. A new test instance would otherwise seed TD's
registration table with its own default poses and move the real phones in TD.
Turn the link on from the Dashboard if that instance is meant to own TD.

## Verifying it came up

The console prints two lines on a successful boot:

```
TDStage Web Console → http://localhost:9080
telemetry in UDP :9001   ·   /ctl out UDP → phone :9010   ·   Ctrl-C to quit
```

Then check, in order:

1. **The web UI.** Open `http://localhost:9080`. The top bar should show a
   listen indicator reading `listening :9001`. If it reads `bind failed`,
   something else holds the port, usually TouchDesigner.

2. **The health endpoint.** This is the one command for a watchdog or a remote
   check:

   ```bash
   curl -s http://localhost:9080/healthz
   ```

   It answers `200` with `ok`, uptime, the ids of online and streaming phones,
   phones that have moved since their pose lock, the TD link state, a `degraded`
   list of phones that are hot, slow or late, and an `offWired` list of phones
   that have a wired link up but are streaming over Wi-Fi. `degraded` and
   `offWired` empty is the state you want.

3. **Frames reaching the console.** `GET /api/live` reports both ingest paths.
   `bridge.running` true with a rising `frames` count means the memory mapped
   path is working. `tdp4.held` true means TouchDesigner holds the phone port
   and the console has correctly stood aside.

4. **The Rig health panel** on the Dashboard. It re checks every ten seconds and
   names a cause and a fix for each problem it finds, with a button for the ones
   the server can repair itself.

5. **`doctor.py`** for the environment rather than the running console. It is
   read only.

   ```bash
   python3 doctor.py              # full check, waits 5 s for phone telemetry
   python3 doctor.py --wait 0     # skip the telemetry wait
   ```

   Flags: `--listen` (default `9001`), `--http` (default `9080`), `--wait`
   (default `5.0`). It checks the Python version, every import the console and
   the YOLO worker need, the torch compute device, the bundled model files,
   whether UDP 9001, 9003 and 9013 and TCP 9080 are free, the Windows Firewall
   rules with the exact `netsh` lines to add them, this machine's LAN addresses,
   and whether any phone telemetry arrives. Exit code 0 means no FAIL lines,
   1 means at least one.

## Network, PoE rig

- One gigabit 802.3at PoE+ switch with enough budget for eight 25 W phones. The
  PC on a switch port, a router or the switch's DHCP on the same LAN.
- Give the PC a fixed address, for example 10.0.0.10, and reserve one address
  per phone.
- Each phone gets a PoE adapter into USB-C. In the app, "Prefer Ethernet (PoE /
  cable)" is on by default, and the Link line must read **Ethernet**. Set the
  destination to the PC's wired address, or push it from the console.
- Bandwidth: eight phones at depth+conf is about 280 Mbit/s; with colour on
  every phone about 570 Mbit/s. Both fit one gigabit uplink. Wi-Fi is the
  fallback only.
- The console logs "stream left Ethernet" when a phone drops to Wi-Fi, and
  `GET /healthz` lists it under `offWired`.

## Operating it remotely

Install Tailscale on the show machine and on the operator's laptop, sign both
into the same tailnet, then browse to
`http://<show-machine>.<tailnet>.ts.net:9080` or its `100.x` address. The
firewall rule already admits `100.64.0.0/10`.

Never forward port 9080 to the public internet. **The console has no login.**

### The off LAN cap

`WebConsole/README.md` says the console can be operated from Sydney. True, with
one caveat it does not state: **the Live view is capped for any client that is
not on the LAN, to 5 frames per second and 20,000 points shared across all
phones.** At eight phones that is 2,500 points each. The console logs the cap the
first time it applies, and every capped response carries an
`X-Cloud-Remote: 5 Hz, 20000 points` header.

A Tailscale `100.64/10` address counts as off LAN, because it is a tunnel. Only
private, loopback and link local addresses count as on LAN.

Everything else in the UI is uncapped remotely: the roster, telemetry, `/ctl`,
the Log, Stage 3D, Markers and the settings. It is the point cloud, and only the
point cloud, that is thinned. Judging merge quality or cloud density needs a
browser on the venue LAN, or a remote desktop session on the show machine.

Use RDP or another remote desktop over Tailscale for TouchDesigner and for
running the `.bat` files. Phones stay on the venue LAN. Only the browser crosses
Tailscale.

## Ports, as the code binds them

| Port | Protocol | Direction | Carried by |
|---|---|---|---|
| 9080 | TCP | browser to console | The UI, the whole HTTP API, the SSE event stream |
| 9000 | UDP | phone to TouchDesigner | OSC telemetry. The tox binds this, which is why the console uses 9001 |
| 9001 | UDP | phone and tox to console | OSC telemetry in, when started with `--listen 9001` |
| 9001 | TCP | console to client machine | The F1 0.4 draft WebSocket. A different protocol on the same number, deliberately |
| 9003 | UDP | phone to bridge | TDP4 depth grid plus the TDPH hello. The bridge binds it; the console binds it only with `--tdp4-port 9003` and nothing else holding it |
| 9004 | UDP | bridge or fan out to TouchDesigner | TDP4. Also the name of the bridge's memory mapped file |
| 9013 | UDP | simulator or fan out to console | TDP4 on the console's own always bound port |
| 9006 | UDP | console to TouchDesigner | OSC: `/tdstage/pose`, `/tdstage/pose/clear`, `/tdstage/ping` |
| 9010 | UDP | console to phone | OSC `/tdlidar/ctl/*`. Per phone, settable as its Ctl port |
| 7000 | UDP | console to client bus | OSC `/track` performers and hands |

Every stream here is UDP except the browser's HTTP and the F1 WebSocket. There
is no TCP transport for depth anywhere in this system.

## Files the console writes

| Path | What |
|---|---|
| `WebConsole/config.json` | Roster, poses, marker plan, person figures, listen port, TD link, client output targets, recovery policy, every setting |
| `WebConsole/backups/config-*.json` | Rotating copies. The console loads the newest if `config.json` ever fails to parse |
| `WebConsole/profiles/phone-<id>.json` | Each phone's last known good profile, with a revision number |
| `WebConsole/logs/console.log` | Rotating, 5 files of 5 MB |
| `WebConsole/logs/track-<stamp>.jsonl` | Written only while `/track` recording is on |

### Backups, and what is not proven

`./Tools/backup_state.sh` takes a **snapshot** before risky work: both repos as
git bundles, uncommitted work as patches, the console config and its rotating
backups, the profiles, the tox, TD's learned state, and a manifest with sha256
sums. Run it before anything you might want to undo.

Treat it as a snapshot, not as a tested restore. **Restoring a configuration is
not proven.** Two specific gaps:

- The console keeps `backups/config-*.json` and falls back to the newest file
  that **parses** if `config.json` fails to parse. Parsing is the only test it
  applies. A file that parses cleanly but holds the wrong values is accepted
  without complaint, and you will not be told.
- The backup path has open review findings, and no restore has been exercised
  end to end.

So: keep the snapshots, and if you ever need one, check the restored roster,
poses, marker plan and listen port by eye against what you expected before
trusting them. Do not plan a show around an unattended restore.

### Restarting to pick up a code change

The Rig health panel's Restart buttons clear state and revive dead threads. They
do **not** reimport any Python module. An edit to the console's code needs the
console process restarted: Ctrl-C and run it again, or close the `run.bat` or
`show.bat` window. Both watchdogs restart the process on their own if it exits,
so on the show machine the process comes straight back.
