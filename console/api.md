---
title: HTTP API
parent: Console
nav_order: 6
---

# HTTP API

Every route the console serves, and which verb it answers.

This page is generated from the console's routing code, so it cannot drift
from the software. Do not edit it by hand. Regenerate it with:

```
python3 tools/gen_api.py
```

## Read this before you call anything

**Check the verb.** Several routes that read like queries are POST only. A
GET to one of those returns 404, which looks exactly like a route that does
not exist. This has already wasted time at least once.

**Three paths answer both verbs**, with different meanings: GET reads,
POST changes. They are `/api/settings`, `/api/hands` and `/api/profile`.

**There is no PUT and no DELETE.** Every POST takes a JSON body and answers
with JSON.

**Two surfaces are not HTTP at all.** The client field stream is a WebSocket
on its own port, 9001 by default. The tracking output is OSC over UDP on port
7000, configured through `POST /api/track`.

Routes found in the source: 24 GET, 33 POST.

| Path | Verb | What it is for |
|---|---|---|
| `/` | GET | The console's web interface. |
| `/api/align/check` | GET | _Not described yet._ |
| `/api/align/job` | GET | State, progress and result of the running (or last) alignment solve. Read only. One solve runs at a time, so starting another while one is running is refused rather than queued. |
| `/api/align/rig` | POST | Solve where every phone is relative to an anchor phone, from the clouds alone, with no markers. Pass `job: true` to run it in the background and poll `/api/align/job`; eight phones is twenty-eight pairs and takes tens of seconds. Each answer is graded: a FAIL is refused and that phone is left where it was, a WARN is applied with its reason. |
| `/api/align/walk` | POST | Walk calibration, which places phones from one person walking rather than from shared scenery, so it works for phones that face each other. `action`: `start`, then `stop` after about 20 seconds of walking where every phone sees you, then `solve`. A forgotten `start` stops itself after two minutes. `only` lists the phones to place, so a walk solve can finish what a cloud solve refused: every other checked phone stays where it is and is reported `FIXED`. |
| `/api/autofix` | POST | Run the automatic fixer against a device. |
| `/api/cloud` | GET | The point cloud, as binary, long-polled. Query: `seq`, `max`, `labels=1`, `fmt=i16`. Off the local network this is capped to 5 Hz and 20,000 points. |
| `/api/count` | POST | Set how many devices the roster holds. |
| `/api/ctl` | POST | Send a control message to one phone or all of them. |
| `/api/dev/shot` | POST | Development screenshot helper. |
| `/api/device` | POST | Change a device's roster entry. |
| `/api/diag/age` | GET | Frame ages per device. |
| `/api/diag/limbs` | GET | Limb diagnostics. |
| `/api/diag/person` | GET | Person diagnostics. |
| `/api/diag/profile` | GET | Profile diagnostics. |
| `/api/edit` | POST | Edit roster fields in bulk. |
| `/api/events` | GET | Server-sent event stream the interface subscribes to. |
| `/api/fanout` | POST | The legacy relay. Not the show path. |
| `/api/hands` | GET and POST | Read hand detections (GET) or change the detector's settings (POST). |
| `/api/hands/diag` | GET | Why hand detection is or is not producing results, as checks rather than counters. This is the per-problem list. Read-only. |
| `/api/listen` | POST | Change the telemetry listening port. |
| `/api/live` | GET | Live summary: which ingest paths are receiving and at what rate. |
| `/api/markers` | POST | Marker definitions. |
| `/api/markers/size` | POST | Set the printed marker size. Must match the markers you actually printed. |
| `/api/ndi` | POST | Video output settings. |
| `/api/person` | POST | Person segmentation mode. |
| `/api/person/debug` | GET | Segmentation internals. |
| `/api/profile` | GET and POST | A phone's stored settings. The phone fetches this itself at boot. |
| `/api/profile/` | GET | Same, addressed per device as `/api/profile/<id>`. |
| `/api/profile/key` | POST | Change one key in a stored profile. |
| `/api/profile/push` | POST | Push a stored profile to a phone. |
| `/api/range` | POST | Working range. |
| `/api/recover` | POST | Run a recovery step on a phone. |
| `/api/recovery` | POST | Recovery policy. |
| `/api/redo` | POST | Redo it. |
| `/api/rgb` | GET | Which devices have a camera image, and how old each one is. |
| `/api/rig` | GET | The facts that span phone, console, relay and TouchDesigner in one place: relay status, cable link, this machine's address, the listener and hands. A facts dump, not a problem list. |
| `/api/rig/calib` | GET | The one-person calibration check: with a single person on stage, do the phones agree where they are? Read only. Pass `x` and `z` to compare the agreed position against a spot whose stage coordinates you know, which is the half that can show the whole rig is offset rather than merely self-consistent. |
| `/api/scene` | POST | Scene settings. |
| `/api/settings` | GET and POST | Read the tunables (GET) or change them (POST). |
| `/api/sim` | POST | Start or stop simulated phones. |
| `/api/stalls` | GET | Recorded stalls, for diagnosing a stuttering stream. |
| `/api/state` | GET | The whole console state: roster, markers, scene, link status. |
| `/api/td` | POST | Link to TouchDesigner. |
| `/api/telemetry/retarget` | POST | Tell phones to send health here instead of to TouchDesigner. |
| `/api/track` | POST | Read or configure the tracking output. Body: `enabled`, `host`, `port`. |
| `/api/track/record` | POST | Start or stop recording the tracking output. Body: `{"on": true}`. Writes `logs/track-<timestamp>.jsonl`. |
| `/api/track/trace` | GET | Per-frame trace of the tracking output, for offline analysis. |
| `/api/undo` | POST | Undo the last roster change. |
| `/api/usb/link` | POST | Find a phone attached by cable. POST only. |
| `/api/venue/layout` | POST | Load a stage layout. Sets positions, labels, and one rig-wide marker size derived from the smallest sheet in the layout. It writes the roster; it does NOT push the size to the phones, so Apply to all phones is still needed. |
| `/api/vision` | GET | State of the vision services. |
| `/api/vision/restart` | POST | Restart a vision service. Clears counters; it does NOT reload code. |
| `/healthz` | GET | Liveness check. Returns without touching any device. |

## Cautions

**Restarting a vision service does not reload code.** The restart controls
clear counters and bring a service back up. A code change needs the console
itself restarted.

**Configuration restore is not yet proven.** The console keeps rotating
backups and falls back to the newest one that both parses and passes its
shape check. Treat the snapshot
tooling as a snapshot: restoring from one is being verified, not demonstrated.
A configuration file that parses but holds the wrong values is still accepted.
