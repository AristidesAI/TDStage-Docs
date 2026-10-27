---
title: Parameters
parent: TouchDesigner
nav_order: 4
---

# Parameters

Every parameter below exists on the working tox,
`TD/TDStageConductor.tox`. The list is sourced from
`TD/newtox/tox_params_live.md`, which is generated from the running component,
and checked against the saved file.

`TD/newtox/param_manifest.py` is a larger design inventory for a component that
was never built. Most of what it lists does not exist. Do not treat it as a
parameter reference.

This page says what each parameter does. It does not say where in the pipeline
it is read, which is often the thing you actually want to know:
[How the pipeline is built](pipeline.html) has the stage order, the two merge
paths side by side, and where each parameter bites.

One caveat on the generated list: `tox_params_live.md` was generated at v63 and
the working copy is v78. A multi-component parameter is printed there as its X
component alone. The operator or shader that **reads** a parameter is the real
contract, and that is what the tables below were checked against.

## Reading this page

The **When** column says when an operator touches a parameter.

| When | Meaning |
|---|---|
| **Get-in** | Set once while rigging, then left alone |
| **Show** | Reasonable to touch with an audience in |
| **Build** | Changed while developing the hub, not on a rig |

Most of this component is get-in. During a show the operator should be
watching, not adjusting.

The **Path** column says which merge path reads the parameter. `Mergegpu`
chooses the path, and the two paths read different parameters. A parameter
marked CPU does nothing while `Mergegpu` is on.

## Point Cloud

Ingest, and the legacy whole-cloud controls.

| Parameter | Label | Type | Default | When | Path | What it does |
|---|---|---|---|---|---|---|
| `Udpactive` | UDP Active (TDP4) | Toggle | True | Get-in | both | Arms the TDP4 ingest. Off means nothing arrives. The saved working copy ships with it off. |
| `Udpport` | UDP Port | Int | 9003 | Get-in | both | The port TouchDesigner receives on, or the port name the bridge publishes its memory-mapped file under. See [Running the hub](running.html). |
| `Stalesecs` | Stale After (s) | Float | 0.5 | Get-in | both | A device silent for longer drops out of the merge and reads STALE. Saved working copy: 0.28. |
| `Maxpoints` | Max Output Points | Int | 400000 | Get-in | CPU | Output budget. The emit strides evenly over the merged cloud to stay under it. |
| `Colormode` | Colour Mode | Menu `rgb` / `tint` | `rgb` | Show | both | `rgb` uses the phone's own colour plane. `tint` gives each device a flat colour, which is how you tell whose cloud is whose while aiming. |
| `Cropon` | Stage Crop | Toggle | False | Get-in | CPU | Enables the axis-aligned crop on the CPU path. The GPU path always crops. |
| `Cropmin` | Crop Min | XYZ | -8, -1, -4 | Get-in | both | Minimum corner of the stage box, in metres. The defaults differ per component: X -8, Y -1, Z -4. Saved working copy: -6, -3, -5. |
| `Cropmax` | Crop Max | XYZ | 8, 9, 4 | Get-in | both | Maximum corner. Per component: X 8, Y 9, Z 4. Saved working copy: 6, 3, 5. |
| `Voxelsize` | Voxel Dedup (m, 0=off) | Float | 0.0 | Build | CPU | Drops duplicate points where views overlap, on the legacy unsegmented path only. Zero is off. |
| `Cleardevices` | Forget All Devices | Pulse | - | Show | both | Wipes every learned device and its buffered cloud, and clears the `devices` table. Use it when a phone has gone and its frozen cloud is still in the view. |

### Which parameter the crop box actually reads

`Cropmin` and `Cropmax` are three-component parameters, and the generated
parameter list prints only the X component, so a reader who trusts it sees one
number for a box with six faces. Read the file, or read the component.

The GPU crop does not use the Y components at all. Its uniforms, on the GLSL
POP `gpu_gl`, are:

| Uniform | Reads |
|---|---|
| `uMin.x`, `uMin.z` | `Cropminx`, `Cropminz` |
| `uMin.y` | `Floorcut` |
| `uMax.x`, `uMax.z` | `Cropmaxx`, `Cropmaxz` |
| `uMax.y` | `Geoceiling` |
| `uMin.w` | A fixed 0.08 m floor band, not a parameter |

So on the GPU path the vertical extent is set on the Level page, not on the
Point Cloud page. `Cropminy` and `Cropmaxy` are read by the CPU crop.

`Cropminy` is not dead on the GPU path, though: `gpu_clean` and `gpu_hyst`
take the **origin** of their spatial hash grid from
`Cropminx - 0.5`, `Cropminy - 0.1`, `Cropminz - 0.5`, and the grid's extent in
X and Z from `Cropmax - Cropmin`. Change `Cropminy` on the GPU path and you
move the cleanup and hysteresis grid without moving the crop. That is a
deliberate split, not an oversight: the crop decides what is in the room, and
the hash grid only has to cover it.

## View

The preview render. None of this touches the output cloud.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Pointsize` | Point Size | Float | 3.0 | Show | Point sprite size in the preview render. Saved working copy: 8. |
| `Floorviz` | Show Floor Plane | Toggle | False | Get-in | Draws the floor plane in the preview, which is how you see whether the level solve landed. |
| `Flooroffset` | Floor Offset (m) | Float | 0.0 | Get-in | Subtracted from Y on every landed frame, on **both** merge paths, so it moves the whole cloud vertically. The saved v78 tox ships **-0.782028 m**, which is not a small correction: it is most of a metre. On the CPU path `udp_pc_exec._land` passes it to `level_ops.unproject_level`; on the GPU path `gpu_atlas_callbacks` bakes it into each phone's pose row. It is applied at landing, before any merging. |
| `Autofloor` | Set Floor To Origin (auto) | Pulse | - | Get-in | Takes the fifth percentile of Y across live devices and adds it to `Flooroffset`, putting the floor at y = 0. Robust to people standing in frame. It is cumulative, so it refines rather than replaces. |
| `Autoframe` | Auto-Frame Preview Cam | Toggle | True | Get-in | Keeps the preview camera framed on the cloud. Saved working copy: off. |

## Log

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Maxlog` | Max Log Rows | Int | 500 | Build | Row cap on `logtable`. |
| `Clearlog` | Clear Log | Pulse | - | Show | Empties `logtable`. Useful before a test so the next fault is the only thing in it. |

## Human

Learned-background segmentation, and the shared cleanup thresholds.

| Parameter | Label | Type | Default | When | Path | What it does |
|---|---|---|---|---|---|---|
| `Learnbg` | Learn Background (empty stage!) | Pulse | - | Get-in | both | Starts a background learn over `Learnframes` frames. **The stage must be empty.** The learned grid is what `Segmode` = `learned` subtracts. |
| `Learnframes` | Learn Frames | Int | 300 | Get-in | both | Frames to average into the learned background. Saved working copy: 450. |
| `Fusevox` | Fine Voxel (m) | Float | 0.025 | Get-in | both | Fusion voxel size. Read by the CPU fusion and by the GPU fusion shader. The GPU hysteresis cell is four times this value. |
| `Floormargin` | Floor Margin (m) | Float | 0.03 | Get-in | CPU | Tolerance on the learned floor height map. Saved working copy: 0.033. |
| `Densitymin` | Min Pts / 10cm Cell | Int | 4 | Get-in | both | A 10 cm cell with fewer points than this is noise. Read by the CPU cleanup and by the GPU cleanup shader. |
| `Minclusterpts` | Min Person Points | Int | 150 | Get-in | both | A cluster with fewer points than this is not a person. Read by both cleanup paths. |
| `Autoalign` | Measure Alignment | Pulse | - | Get-in | CPU | Collects 30 frames, then solves a four-degree-of-freedom alignment per device against a reference, on a worker thread. It only measures. |
| `Alignref` | Reference Device | Int | 1 | Get-in | CPU | The device the alignment solve measures the others against. |
| `Applyalign` | Apply To Registration | Pulse | - | Get-in | CPU | Writes the measured alignment into the `registration` table. Check `align_report` first: it carries an accept or reject verdict, residual and inlier count per device. |
| `Halign` | Auto-Align (ICP vs static bg) | Toggle | False | - | - | **Inert.** The parameter exists on the page and nothing in the repository reads it. It is also absent from the generated parameter list. Treat it as dead until something claims it. |

## Level

The largest page. It holds the stage level solve, the lens unwarp, the manual
trim, and the merge path controls.

### Level solve

Fits the ground plane so the cloud sits level with the floor at y = 0.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Levelsolve` | Solve Level (gather frames) | Pulse | - | Get-in | Gathers `Levelframes` frames, then solves. The normal way to level. |
| `Levelnow` | Solve Level (single frame) | Pulse | - | Get-in | Solves from one frame. Faster and noisier. |
| `Levelframes` | Level Gather Frames | Int | 60 | Get-in | Frames to gather. Saved working copy: 56. |
| `Levelrecentre` | Recentre Origin On Floor | Toggle | True | Get-in | Moves the origin onto the solved floor as well as levelling. Saved working copy: off. |
| `Levelclear` | Clear Level | Pulse | - | Get-in | Back to identity. |
| `Levelstatus` | Level Status | Str | - | - | Read-only result string. On failure it reports what it measured, not just the threshold it wanted, for example the best floor patch it found in cells and square metres. |
| `Levelcell` | Level Cell (m) | Float | 0.15 | Build | Cell size of the floor-candidate grid. |
| `Levelthresh` | Level Inlier (m) | Float | 0.03 | Build | Inlier distance for the plane fit. |
| `Levelmincells` | Level Min Cells | Int | 40 | Build | Minimum floor cells for the solve to accept. 40 cells is about 0.9 square metres at the default cell size. The solve used to hardcode 150 cells, about 3.4 square metres, which is more floor than one phone reliably sees, so it failed whenever anyone stood on the floor. Fixed 2026-09-04. |
| `Levelmaxtilt` | Level Max Tilt (deg) | Float | 40.0 | Build | Reject a solved plane tilted more than this. Saved working copy: 53.1. |
| `Levelmaxrms` | Level Max RMS (m) | Float | 0.05 | Build | Reject a solved plane with a worse residual. |

All five of `Levelcell`, `Levelthresh`, `Levelmincells`, `Levelmaxtilt` and
`Levelmaxrms` are read by the solve. Before 2026-09-04 they did not exist and
the solve used fixed values.

### Lens unwarp

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Unwarpsolve` | Solve Lens Unwarp (flatten warp) | Pulse | - | Get-in | Solves a correction for the residual curvature in a device's depth grid, per device, from the frames it has. |
| `Unwarpclear` | Clear Lens Unwarp | Pulse | - | Get-in | Back to none. |
| `Unwarpstatus` | Unwarp Status | Str | - | - | Read-only result string. |

### Manual trim

Applied to the whole merged cloud, after registration. This is the nudge you
reach for when the cloud is right but sitting slightly wrong.

| Parameter | Label | Type | Default | When |
|---|---|---|---|---|
| `Trimx`, `Trimy`, `Trimz` | Cloud Offset X/Y/Z (m) | Float | 0.0 | Get-in |
| `Trimrx`, `Trimry`, `Trimrz` | Cloud Rotate X/Y/Z (deg) | Float | 0.0 | Get-in |
| `Trimreset` | Reset Cloud Offset/Rotate | Pulse | - | Get-in |

Saved working copy: `Trimy` 0.25, the rest zero.

### Stage volume and segmentation

| Parameter | Label | Type | Default | When | Path | What it does |
|---|---|---|---|---|---|---|
| `Floorcut` | Ground Cutoff Height (m) | Float | 0.06 | Get-in | both | Points below this height are floor. On the GPU path this is the Y minimum of the crop, and a band just under it is kept flagged so feet are not lost. Saved working copy: 0. |
| `Geoceiling` | Ceiling Cutoff (m) | Float | 2.4 | Get-in | both | Points above this are ceiling, trussing and lights. On the GPU path this is the Y maximum of the crop. Saved working copy: 4. |
| `Segmode` | Segmentation Mode | Menu `off` / `geometric` / `learned` | `off` | Get-in | both | `off` passes the full cloud, for setup and inspection. `geometric` cuts floor, ceiling and stage box, then density and clustering, and works from the first frame on a levelled cloud with nothing learned. `learned` subtracts the learned background first and is the sharpest, but needs a `Learnbg` pass on an empty stage. Saved working copy: `geometric`. |

### Merge path

| Parameter | Label | Type | Default | When | Path | What it does |
|---|---|---|---|---|---|---|
| `Mergegpu` | GPU Merge Path | Toggle | False | Get-in | - | Builds the cloud on the GPU: the depth grids go up as one texture and a chain of GLSL POPs unprojects, transforms, crops, cleans and fuses every cell each frame. The **CPU merge stands down**; background removal, cleanup and fusion continue as GPU stages. `out_merged` goes empty. Needs the bridge running. Saved working copy: on. |
| `Fusionmode` | Fusion Mode | Menu `points` / `grid` / `merged` | `points` | Build | CPU | `grid` runs the angle-aware weighted merge on the full grid rather than on decimated points. |
| `Mergevoxel` | Merge Voxel (m) | Float | 0.025 | Build | CPU | Voxel size for the grid merge. |
| `Mergealign` | Pre-align Devices | Toggle | False | Build | CPU | Runs the alignment solve before merging. |
| `Fuserate` | Fusion Rate (Hz) | Float | 30.0 | Build | CPU | Caps real fusions per second. Below the interval, the last result is re-emitted rather than recomputed. |
| `Mergeprecut` | Cut Before Fusing | Toggle | True | Build | CPU | Applies the geometric cut before fusion rather than after. Saved working copy: off. |
| `Mergethread` | Segment Off Main Thread | Toggle | True | Get-in | CPU | Runs segmentation on a latest-wins worker thread, so TouchDesigner's frame rate stops following the phone count. Costs about one merge of extra latency. Off is synchronous. |

### GPU merge path controls

These are read only while `Mergegpu` is on. They are the GPU equivalents of
the CPU path's stages, not extras: background removal, cleanup and fusion all
happen on this path, on the GPU. See [How the pipeline is built](pipeline.html)
for the stage order and for which parameter each shader reads.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Gpufuse` | GPU Voxel Fusion | Toggle | True | Get-in | Fuses overlapping views into one voxel on the GPU. |
| `Gpufusemin` | GPU Fusion Min Points | Int | 1 | Build | A voxel needs this many points to survive fusion. |
| `Gpuclean` | GPU Density + Cluster Cleanup | Toggle | True | Get-in | Density and cluster cleanup on the GPU, using `Densitymin` and `Minclusterpts`. |
| `Gpuhyst` | GPU Temporal Hysteresis | Toggle | True | Get-in | GPU path with `Segmode` = `learned` only. A cell four times `Fusevox` across must hold points for three consecutive merges before it appears, and inherits that streak from any of its 27 neighbours, so a limb moving into a fresh cell keeps showing. It holds for twelve merges after it empties. Counts scale with the frame rate. |
| `Gpusmooth` | GPU Fuse Plane Smooth | Toggle | False | Build | Prototype. Moves each fused voxel along the normal of a plane fitted to its 3x3x3 neighbourhood. Off by default until real takes decide whether it helps. |
| `Gputemporal` | GPU Temporal Depth (still) | Toggle | False | Build | Prototype. Averages each depth cell over up to sixteen frames while it holds still, with a three-frame hold, and resets the moment it moves. Off by default. |
| `Gputempsigma` | Temporal Noise Scale | Float | 1.0 | Build | Scale on the depth-noise model the temporal filter gates with. Lower is a stricter stillness test: less lag, less averaging. |

Both prototypes are built, not verified on a rig. `Gputemporal` has an offline
check, `TD/newtox/temporal_test.py`, which scores it against the merge
simulator.

## Console

The link to the web console. The console carries the device roster, the
calibration markers and the client-facing outputs; the hub carries the cloud.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Consoleactive` | Console Link Active | Toggle | True | Get-in | Enables the link. |
| `Consoleport` | Console Link Port (rx) | Int | 9006 | Get-in | The port the hub receives on, from the console. |
| `Consolehost` | Console Host (blank = learn from ping) | Str | blank | Get-in | Leave blank and the hub learns the console's address from its ping. |
| `Consolereply` | Console Listen Port (tx) | Int | 9001 | Get-in | The port the hub sends to. |
| `Healthhz` | Health Rate (Hz) | Float | 1.0 | Build | How often the hub reports its health to the console. |
| `Oscinport` | Phone Telemetry Port (relay in) | Int | 9000 | Get-in | Phone OSC telemetry arrives here and is relayed to the console. The hub no longer interprets it. |
| `Consolestatus` | Link Status | Str | - | - | Read-only. Address, time since the last ping, and transmit, receive, relay, ignored and error counts. |

## RGB

Each phone's own camera image, as a TOP. The camera image is the image: there
is no reprojection and no holes. When a phone streams depth only, the slot is
drawn from the same per-point colours the merge uses, so it stays live.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Rgbactive` | RGB Views Active | Toggle | True | Get-in | Enables the views. |
| `Rgbmap` | Slot Mapping | Menu `auto` / `byid` | `auto` | Get-in | `auto`: slot N is the Nth live device in sorted order, which is what the desk wants. `byid`: slot N is device id N. |
| `Rgbselect` | Output Select | Menu `grid` / `1` to `8` | `grid` | Show | What `out_rgb` carries: the four by two grid of all eight, or one phone full size. This is a genuine show-time control for looking down a single camera. |
| `Rgbw` | View Width (px) | Int | 320 | Get-in | Per-slot width. |
| `Rgbh` | View Height (px) | Int | 240 | Get-in | Per-slot height. |

## Hands

Hand markers. The detection runs in the console; the hub polls it over HTTP
and turns each hit back into the exact stage point the merge already produced.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Handsactive` | Hand Tracking Active | Toggle | True | Get-in | Enables the poll. Saved working copy: off. |
| `Handsurl` | Detector URL (console /api/hands) | Str | `http://127.0.0.1:9080/api/hands` | Get-in | The console endpoint. Use a loopback address when the console runs on the same machine. |
| `Handsrate` | Poll Rate (Hz) | Float | 15.0 | Build | Poll rate. Saved working copy: 30. |
| `Handsdepthwin` | Depth Window (px) | Int | 7 | Build | Window around the detected pixel used to read a depth. |
| `Handssmooth` | Position Smoothing | Float | 0.4 | Build | Smoothing on the marker position. |
| `Handssize` | Marker Radius (m) | Float | 0.06 | Get-in | Drawn marker radius. |
| `Handsshow3d` | Markers In 3D View | Toggle | True | Show | Draw markers in the preview render. |
| `Handsshowrgb` | Rings On RGB Views | Toggle | True | Show | Draw rings on the RGB views. |
| `Handsstatus` | Hands Status | Str | - | - | Read-only. Endpoint, poll time, last success, hand and phone counts, misses and errors. |

## Align

Per-device registration: where each phone is, so its cloud lands in the right
place.

| Parameter | Label | Type | Default | When | What it does |
|---|---|---|---|---|---|
| `Posesource` | Pose Source | Menu `console` / `manual` | `console` | Get-in | `console` takes poses from the console roster. `manual` uses the knobs below. Saved working copy: `manual`. |
| `Regdevice` | Edit Device Id | Int | 1 | Get-in | Which device the knobs below edit. Saved working copy: 2. |
| `Regyaw` | Yaw (deg) | Float | 0.0 | Get-in | That device's yaw. Note that the registration yaw is not the same number as the roster's plan heading; see the console documentation before typing a figure in by hand. |
| `Regtx`, `Regty`, `Regtz` | Move X/Y/Z (m) | Float | 0.0 | Get-in | That device's translation. |
| `Regreload` | Reload From Table | Pulse | - | Get-in | Loads the selected device's stored values onto the knobs. |
| `Regzero` | Zero This Device | Pulse | - | Get-in | Zeroes the selected device. |
| `Regcopyref` | Copy From Reference | Pulse | - | Get-in | Copies the reference device's values onto the selected one. |

The `registration` table holds the stored values, one row per device. Rows
appear automatically as devices come online, so the table is never edited to
add a phone.

## What the saved file ships with

These are the values stored in `TDStageConductor.tox` as of 2026-10-27, where
they differ from the parameter default. A later save may differ; read the file
rather than trusting this table.

| Parameter | Saved value |
|---|---|
| `Udpactive` | off |
| `Udpport` | 9004 |
| `Mergegpu` | on |
| `Segmode` | geometric |
| `Stalesecs` | 0.28 |
| `Floorcut` | 0 |
| `Geoceiling` | 4 |
| `Learnframes` | 450 |
| `Mergeprecut` | off |
| `Posesource` | manual |
| `Autoframe` | off |
| `Handsactive` | off |
| `Floorviz` | on |
| `Pointsize` | 8 |
| `Cropmin` | -6, -3, -5 |
| `Cropmax` | 6, 3, 5 |
| `Flooroffset` | -0.782028 |
| `Floormargin` | 0.033 |
| `Levelframes` | 56 |
| `Levelrecentre` | off |
| `Levelmaxtilt` | 53.1 |
| `Trimy` | 0.25 |
| `Handsrate` | 30 |
| `Regdevice` | 2 |
| `Regyaw` | 21 |
| `Regtx` | 0.3 |
| `Regty` | -0.09 |
| `Regtz` | -1.9 |

`Cropmin` and `Cropmax` together are the live stage box: about six metres
either side in X and five either side in Z, three metres down and three up.
The X and Z figures are read directly by the GPU crop; the Y figures are read
by the CPU crop and by the cleanup grid's origin.

The `Align` knobs are the pose of whichever device `Regdevice` selects, so the
saved values are device 2's. The saved `registration` table carries non-zero
poses for devices 1, 2 and 3:

| id | yaw (deg) | tx | ty | tz |
|---|---|---|---|---|
| 1 | 46.0 | -2.7 | 0.53 | -0.9 |
| 2 | 21.0 | 0.3 | -0.09 | -1.9 |
| 3 | 90.0 | 0.0 | 1.67 | 0.599 |
| 50 | 0 | 0 | 0 | 0 |

Those are a bench rig, not a venue. They are in the file because the component
was last saved with them, and they will land somebody's phone in the wrong
place if they are left there. With `Posesource` on `manual`, as saved, the
console cannot correct them.
