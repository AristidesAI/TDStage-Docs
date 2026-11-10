---
title: What TDStage AR adds
parent: iOS app
nav_order: 8
---

# What TDStage AR adds

The app on the rig is **TDStage AR**. It shares the settings, the wire format,
the recorder, the `/ctl` surface and the whole interface with the app the rest
of this section describes. What it adds is a **depth conditioning pass that
runs on the phone**, and about twenty settings that steer it. None of them
appear in the other app.

The pass exists for one reason. Depth at the silhouette of a body smears onto
whatever is behind it, and those smeared points survive into the fused cloud as
a halo no receiver-side cleanup removes reliably. Conditioning each cell on the
phone, where the raw sensor samples and the confidence still exist, removes
most of it before it reaches the wire.

{: .note }
Every default below is what a fresh install uses. The show is expected to run
on the defaults, and each key exists mainly so one effect can be switched off
for a measurement.

## The switch that decides everything else

| Key | Default | What it does |
|---|---|---|
| `stage.capture` | `arkit` | `arkit` runs the ARKit renderer: frame-aligned confidence and person matte, a 256×192 ceiling. `avfoundation` runs the parent project's raw renderer: no confidence, no matte, up to 320×240. Changing it needs a capture restart, which the controller performs |
| `stage.confidenceGate` | `false` | Drop every cell ARKit rates low |
| `stage.rec.imu` | `true` | Write the 100 Hz `.imu` sidecar beside each take |

`stage.capture` is the one setting on this page that changes what every other
number means, because it changes the grid, the confidence plane and whether a
person matte exists at all. It is a string, so it is set with the `/ctl` string
form rather than a number.

{: .note }
> **The confidence gate is off for a measured reason, not an unexamined one.**
> It drops every ARKit "low" cell, and low is where thin, fast-moving limbs
> sit. Measured with `Tools/limb_test.py` on a moving person: with the gate on,
> limbs kept 0.44 with 96 per cent of frames below 0.6; with it off, 0.80 with
> 9 per cent. Body coverage went 0.77 to 0.89 and bleed 0.019 to 0.032, and
> TouchDesigner's cleanup absorbs that extra bleed. Turning it on trades limbs
> for tidiness at the silhouette, which is the wrong way round for this show.

The IMU sidecar is on by default and worth leaving on: it is the only record
of what the phone itself was doing during a take, at 100 Hz on the same clock
as the frames, and `ar_phone_check.py` reports a phone that has it switched off
as a recorder setting that loses data.

## Edge cull, which removes the halo

A per-pixel test that reads a cell's neighbours, decides whether the 3×3 window
straddles a real discontinuity, and drops the cell if it is sitting in the gap
between two surfaces rather than on either of them. A surviving cell always
keeps its own depth: nothing is averaged, invented or moved.

| Key | Default | What it does |
|---|---|---|
| `stage.edgecull` | `1.0` | Strength. **0 turns the cull off**, and leaves the rest of the pass running, so 0 alone does not give you the grid as the sensor produced it |
| `stage.edgeslope` | `66.0` | Steepest surface believed to be real, in degrees from head-on. Above it a depth step reads as a discontinuity rather than a slope |
| `stage.edgeband` | `0.30` | How much of the gap at each end still belongs to its surface. Larger keeps more genuine edge pixels and culls only the dead centre |
| `stage.edgefloor` | `0.02` | Threshold floor in metres. Below it the cull is chasing sensor noise |
| `stage.edge8` | `true` | Include diagonals, which catches silhouettes running at 45° to the raster |
| `stage.edgekeephigh` | `true` | Never drop a cell ARKit rated high confidence. Those land on a real surface, so a high-confidence cell inside a gap is a thin limb rather than a blend |

`edgeslope` is the one with an open question on it. **70 kept 0.010 more limb
cells** than 66 on a replayed take, and what grows at 70 is real floor around
the feet rather than points floating above it. It is not the default yet
because that result came from a take replay and wants a live A/B on the rig.

## Temporal median, which stops the boil

A median of each cell's own last three samples, taken per cell, never across
neighbours.

| Key | Default | What it does |
|---|---|---|
| `stage.temporalmedian` | `true` | Run the median at all |
| `stage.motionthresh` | `0.01` | **Makes the median motion-adaptive.** A cell counts as moving only when its present sample differs from both of its last two by more than `max(edgefloor, this × range)` |
| `stage.motionhold` | `false` | At a motion onset, hold the previous sample one frame so a single-frame spike never reaches the wire. Costs 33 ms at every onset |
| `stage.motionflipguard` | `true` | A cell in motion does not count towards the flip hysteresis, because a sweeping edge is not boil |
| `stage.fliplimit` | `0.0` | Flips before a cell is muted. **Off**, because muting cost a moving limb's edge for good |
| `stage.arsmoothed` | `false` | Use ARKit's own smoothed depth instead of raw scene depth. **Off for a show**: Apple's smoothing lags moving surfaces. It exists so the difference can be seen in an A/B |

Read the motion threshold before changing anything here. A plain median-3
returns the previous sample for *any* steady motion: one frame late, every
frame, which is what made arms stretch on this path. With the threshold at its default, a
cell is treated as still unless it moves more than `max(2 cm, 1 % of range)`
between frames. At 4.5 m that is 4.5 cm a frame, so radial motion under about
1.35 m/s at 30 fps counts as still and is sent one frame late. An edge crossing
a cell jumps by far more than that and goes out on time.

## The person gate, and what it does to an inverted performer

| Key | Default | What it does |
|---|---|---|
| `stage.persononly` | `false` | Stream only cells the person matte covers |
| `stage.persondilate` | `true` | Grow the matte one texel, which restores fingers and hair |
| `stage.personinvert` | `false` | Keep the background instead. A calibration aid |
| `stage.personquality` | `1` | Matte quality on the AVFoundation path only. ARKit ignores it, because its matte comes from the frame |

{: .warning }
> **With `persononly` on, a performer the model does not recognise is not
> streamed at all.** The gate culls every cell the matte does not cover, so
> when the matte comes back empty the phone sends an empty frame, and no
> receiver can recover a body that never left the phone. It fails **closed**.
>
> The one exception is a missing matte. If no matte buffer arrives, the gate is
> skipped entirely and the full grid goes out, so a segmentation that fails to
> produce anything fails **open**. A matte that produces nothing does not.
>
> This is the opposite of the console's policy, which fails open: a device with
> no fresh mask contributes all of its points, so a model miss there can never
> blank the stage.

**The model wants an upright person.** That is a property of Apple's
segmentation, not of this app, and it is why `persononly` is off by default.
For an act with an inverted or sideways performer, a cyr wheel among them,
leave it off and let the receiver do the isolation from geometry, where being
upside down costs nothing.

Feeding the segmenter a rotated frame is possible on the AVFoundation path,
which carries the rotation explicitly, but only two rotations exist there:
none, and the 90° the rear camera needs. **There is no 180° option in either
path today.** On the ARKit path there is no knob at all, because Apple
produces the matte inside the frame.

## Range gate, thermal ladder and format

| Key | Default | What it does |
|---|---|---|
| `stage.znear` | `0.15` | Hard near gate in metres |
| `stage.zfar` | `12.0` | Hard far gate in metres |
| `stage.minconf` | `0` | 0 off, 1 medium and above, 2 high only |
| `stage.arFormatMatch` | `true` | Run ARKit at the slowest 4:3 format that still reaches the target frame rate, rather than the fastest |
| `stage.thermalLadder` | `true` | Lower the frame-rate ceiling as the phone heats. 0 holds the set rate whatever happens |
| `stage.thermalSeriousFPS` | `30` | The ladder's rung for a serious thermal state, in absolute fps. At 30 it acts only at critical |
| `stage.thermalColourAt` | `0` | Shed the colour plane from fair (1) or serious (2). **0 never**, because colour is wanted |

The thermal defaults come from a measured run: 31 minutes at 30 fps while the
phone reported serious, never reaching critical, and dropping to 25 fps bought
nothing.

## What none of this changes

The frame on the wire, the recorder, the profile document and the `/ctl`
surface are identical to the other app's. A take recorded on either replays
through either, and a receiver cannot tell which app produced a frame, except
that the confidence plane means something real here.

`stage.depthgrid` is inert in both. This app sends **256×192 on every LiDAR
iPhone**, because that is ARKit's scene-depth grid.
