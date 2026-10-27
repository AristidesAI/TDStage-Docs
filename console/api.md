---
title: HTTP API
parent: Console
nav_order: 5
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

Routes found in the source: 22 GET, 34 POST.

| Path | Verb | What it is for |
|---|---|---|
| `/` | GET | The console's web interface. |
| `/api/align/rig` | POST | Solve the rig alignment. |
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
| `/api/hands/diag` | GET | Why hand detection is or is not producing results. |
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
| `/api/rig` | GET | Rig health: one row per problem, each with its fix. |
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
| `/api/venue/layout` | POST | Load a stage layout. Copies positions and labels only; it does NOT set the marker size. |
| `/api/vision` | GET | State of the vision services. |
| `/api/vision/restart` | POST | Restart a vision service. Clears counters; it does NOT reload code. |
| `/healthz` | GET | Liveness check. Returns without touching any device. |

## Cautions

**Restarting a vision service does not reload code.** The restart controls
clear counters and bring a service back up. A code change needs the console
itself restarted.

**Configuration restore is not yet proven.** The console keeps rotating
backups and falls back to the newest one that parses. Treat the snapshot
tooling as a snapshot: restoring from one is being verified, not demonstrated.
A configuration file that parses but holds the wrong values is still accepted.
