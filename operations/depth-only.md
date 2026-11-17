---
title: The depth-only run
parent: Operations
nav_order: 12
---

# The depth-only run

{: .no_toc }

One performer, upside down, tracked without the person model. This is the
configuration to use when the body on stage is in a cyr wheel, inverted, or
otherwise not something a keypoint model recognises as a person.

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## Why it exists

The person model wants an upright body. The client's own rotation test on
6 November 2026 found about **22 per cent of the upright detection rate at
180 degrees** and about 4 per cent at 90 or 270. A performer hanging in a wheel
is therefore invisible to the model for most of a routine, and everything that
depends on the model - the person masks, `/track` performers, F1 presence - goes
with it.

Depth does not care which way up a body is. So the whole model path comes out of
the loop and the performer is found geometrically: a cluster of points of roughly
the right size, in the stage volume, moving.

{: .warning }
**It is for one performer.** With the mask gate off and detection on geometry,
two people who touch cannot be separated at all - there is nothing to tell them
apart with. The preset sets `maxPerformers` to 1 for that reason, and there is
now a measured figure for what happens if a second body is in view anyway: in
side-by-side simulated runs on 17 November, with the cap at 1 and two walkers on
stage, the single id switched between the two bodies **about 90 times in 150
seconds** (87 to 97 across runs) [simulated]. So the instruction is not
cautious: keep one person and nothing else body-sized in the stage area while
this preset is on. Use it for one body in a wheel and for nothing else.

## Applying it

The console has it as a preset. In the Live view's **People only** panel it is
the **Cyr wheel (arm B)** button, and over the API:

```bash
curl -X POST http://localhost:9080/api/preset -d '{"name":"cyr","action":"apply"}'
```

`{"action": "reverse"}` with the same name puts back **the values that were
there before the apply**, not the shipped defaults, and that holds across a
console restart. So an operator who applies it at 11pm to test something can
undo it exactly the next morning without knowing what the rig was set to.

Seven settings move and nothing else does:

| Setting | Value | Why |
|---|---|---|
| `latency.personMode` | `motion` | The person observers stop feeding the engine; foreground comes from motion against the learned background |
| `tracking.detSource` | `geometry` | Performers are clusters of points, not model instances |
| `tracking.maskGate` | off | Points are no longer intersected with a person mask before merging |
| `tracking.footMax` | 2.4 m | A cyr wheel side-on is about 2 m across, so the footprint gate has to open or the whole wheel is rejected as too wide for a person |
| `tracking.spanMin` | 0.3 m | A body in a wheel can present a short vertical extent |
| `tracking.maxPerformers` | 1 | One body on stage |
| `f1.presenceSource` | `depth` | The field stream's presence comes from depth too, rather than from a model answer that will not arrive |

## Three conditions, and they are not optional

**Press Stage is empty now first, on an empty stage.** Geometric detection is
motion against a learned background. If the background was learned with the
performer or the wheel standing in the volume, that shape is scenery for the
rest of the session and the performer inside it is invisible. Skipping this step
costs the run.

**One performer.** See the warning above. If a second person walks on to adjust
something, expect one performer, the wrong one, or a merge - all three are the
configuration working as specified.

**Rotate and retry off, with one thing to know about what that costs.**
`vision.rotateRetry` makes the model look again at a picture turned 180, 90 or
270 degrees when it finds nobody upright but the depth holds a body-sized blob.
On turned stand-ins of an upright walker it moved detection from **0 per cent at
180 degrees to 100 per cent**, with no false people on empty frames - so it
works, and it is the reason the setting exists.

In this configuration it does not feed the performers: detection is geometric
and the masks are not consulted. What it would still feed is **hands**, which
come from wrists the model finds, matched to a performer the geometry produced.
So switching it off is the right call for a depth-only run - it saves an extra
inference pass per frame on every phone that triggers it, about 10 ms on a Mac
and 30 with keypoints on - and the thing it takes with it is any chance of hands
from an inverted body. If the session wants hands from the wheel, that is the
setting to turn back on, and the cost is measurable in the load line.

## Putting the defaults back

Three ways, and they are not equivalent:

| | What it does |
|---|---|
| `{"action": "reverse"}`, or the panel's own button | The seven settings go back to what they were immediately before the apply. The right answer in almost every case |
| Setting each key by hand | Works, and you have to know what seven values to type. The settings page lists the defaults, not what your rig had |
| A console restart | Changes nothing. The preset is in the saved configuration, and so is the record of what preceded it |

After reversing, **learn the background again** if the stage has changed since
the geometric run. Nothing forces it, and a background learned for one
configuration is not wrong for the other, but a wheel left on stage is scenery
either way.

## What is known about it

{: .note }
**Level: simulated. No inverted body has been measured through this
configuration.** The preset's seven values are verified against the code and
its reverse is covered by self-tests. What has not happened is a performer in a
wheel in front of real phones, which is what the 18 November session is for.
The 22 and 4 per cent detection figures are the **client's** measurements of
their own rotated frames, not ours.

Two things nobody can tell you yet: how well a geometric cluster tracks a
rotating body through a routine, and whether 2.4 m is the right footprint for
the wheel that will actually be on stage. Both want the session, and both are
cheap to adjust once somebody has watched it.

## See also

- [Settings reference](../console/settings.html#the-cyr-preset) for the preset
  row by row, and for what each of the seven settings does elsewhere
- [Getting the room out of the cloud](background.html) for learning a
  background and for the stage cut, which helps a geometric run more than a
  model one
- [The tracking output](../reference/track.html) for what a receiver gets while
  this is on: performers and no hands, since hands come from wrists the model
  finds
