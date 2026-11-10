---
title: Getting the room out of the cloud
parent: Operations
nav_order: 10
---

# Getting the room out of the cloud

The floor, the walls, the truss and the furniture all return depth, and a
LiDAR phone has no opinion about which of them you care about. Everything
below is how the room gets removed, and the first thing to know is that there
are **two separate answers**, because there are two pipelines.

TouchDesigner and the console both read the same published frames from the
bridge, and **neither reads the other's output**
([the fork at the bridge](../index.html#the-whole-system-on-one-page)).
So cutting the floor out of TouchDesigner's cloud does nothing to what `/track`
publishes, and cutting it in the console does nothing to the picture. A rig
that looks clean on screen while the tracking output still has the back wall in
it is not a contradiction; it is one side configured and the other not.

| You want the room gone from | Set it in |
|---|---|
| The visuals, and anything built on TouchDesigner's cloud | The tox's Point Cloud and Floor pages |
| `/track`, the field stream, NDI, the Live view | The console's `segmentation` settings |

Each side offers the same two kinds of cut, and they compose in the same order:
**a geometric box first, then a learned background.**

## Geometry: the cut that works on the first frame

A geometric cut needs nothing learned and nothing empty. It is a box, applied
per point, and it is the one to reach for first because it is deterministic:
the same point is always kept or always dropped.

### In TouchDesigner

| Parameter | Default | What it cuts |
|---|---|---|
| `Cropmin`, `Cropmax` | -8, -1, -4 and 8, 9, 4 | The stage box in metres. The saved working copy is tighter: -6, -3, -5 to 6, 3, 5 |
| `Floorcut` | 0.06 m | Points below this are floor |
| `Geoceiling` | 2.4 m | Points above this are ceiling, truss and lights. The saved copy uses 4 |

{: .warning }
> **On the GPU path the crop's Y comes from `Floorcut` and `Geoceiling`, not
> from `Cropmin` and `Cropmax`.** The shader's `uMin.y` is `Floorcut` and its
> `uMax.y` is `Geoceiling`; `Cropminy` and `Cropmaxy` are read only by the CPU
> crop. Raising `Cropminy` on the GPU path and expecting the floor to go is a
> change that does nothing, and nothing says so.
>
> `Cropminy` is not inert there, though. It sets the origin of the hash grid
> that `gpu_clean` and `gpu_hyst` use, so moving it moves where clustering
> happens without moving what is cropped.

**A band 0.08 m below `Floorcut` is kept and flagged rather than dropped**, so
feet are not cut off at the ankle. It is fixed in the shader and is not a
parameter. Anything below `Floorcut` minus 0.08 m is gone.

### In the console

The engine's inclusion box is five keys in `segmentation`, and points outside
it never enter the motion engine at all:

| Key | Default | Edge |
|---|---|---|
| `stageX` | 9.0 m | Half width |
| `stageZlo`, `stageZhi` | -9.0 m, 9.0 m | Downstage and upstage |
| `stageYlo` | -0.6 m | Floor margin |
| `stageYhi` | 3.6 m | Ceiling |

The upstage edge is the one that earns its keep at a venue: a back wall past
`stageZhi` never reaches the engine, so it cannot be learned, mistaken for a
performer, or counted in the maturity ratio.

## The learned background: sharper, and it needs an empty stage

A learned background records what the room looks like with nobody in it and
subtracts it. It is sharper than a box, because it removes a chair rather than
a cuboid of air around the chair, and it costs a pass on an empty stage.

**In TouchDesigner**, set `Segmode`:

| Mode | What it does |
|---|---|
| `off` | The full cloud, for setup and inspection |
| `geometric` | Floor, ceiling and stage box, then density and clustering. Works from the first frame on a levelled cloud with nothing learned |
| `learned` | Subtracts the learned background first. The sharpest, and it needs a `Learnbg` pass over `Learnframes` frames **with the stage empty** |

**In the console**, the background learns continuously unless you stop it.
`bgThresh` (0.45) is the occupancy above which a voxel counts as scenery, and
**Stage is empty now** promotes everything currently visible in one go.
`freezeBg` then stops it absorbing anything further, which is what keeps a
performer holding still from fading into the room.

{: .warning }
> **Freezing has a trap at a get-in.** With `freezeBg` on, moving a phone
> clears the frozen background and `/track` publishes nobody until somebody
> presses Stage is empty now again. With it off, only the moved phone drops
> out, for about thirty seconds. Freeze after the rig has stopped moving, not
> before.

## Which one to reach for

1. **Set the boxes first**, on both sides. They work immediately, they cannot
   learn a performer by mistake, and they make everything after them cheaper.
2. **Then learn the background**, on an empty stage, if the geometry alone
   leaves scenery inside the box.
3. **Freeze it last**, once nothing else is going to move.

A cut you can reason about beats a cut that is sharper. The box is the one you
can explain to somebody at two in the morning when a performer's arm keeps
disappearing; the learned background is the one that quietly ate a prop nobody
moved for a minute.

## When the background will not learn

A cluster that is mostly **motion-born** gets its footprint protected, so that
a performer standing still is not absorbed. The protection has a failure mode:
if a whole view arrives after the engine has started, everything in it is
motion-born, and it can guard itself and never learn.

The console carries a mechanism for exactly that, called a scenery epoch.
Voxels born in the first three seconds after an epoch count as scenery rather
than as somebody walking in, and an epoch is raised in two ways: `ingest` marks
one when a phone's stream joins or comes back after an outage, and a tick that
brings in more than 6,000 new voxels at once raises one too, which covers a
phone that was re-aimed. A walker adds at most about 550 voxels in a tick, and
a whole body appearing at once about 3,000, so the bar sits clear of anything a
person does.

If `/track` still reports nobody with people plainly in view, the two things to
check are the maturity ratio and the settle window
([`matureFrac` in a room the stage does not fill](../console/settings.html#maturefrac-in-a-room-the-stage-does-not-fill)),
and the clearing action is the same one as everywhere else on this page:
**Stage is empty now**, on an empty stage.
