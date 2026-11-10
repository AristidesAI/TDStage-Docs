---
title: Questions we get asked
nav_order: 7
---

# Questions we get asked

These are the questions that come up when somebody is sizing this system for a
venue. Each answer says what it rests on, because several of them rest on
arithmetic rather than on a stage.

{: .warning }
> Read [how far each part is proven](reference/status.html) first. The system is
> in pre-production: nothing has run on a stage, and the most phones placed and
> aligned together so far is two, in a living room. Where an answer below is
> computed rather than measured, it says so.

## How many phones for a stage 14 m wide by 4 m deep?

**Start from coverage, not from a headcount.** The number that matters is how
much of the playing area is seen by **two** phones, because one view is a
position a performer can hide from, and a second view from a different angle is
the only thing that recovers them.

A phone's footprint comes from its lens and its range:

| Distance from the phone | Width it sees | Height it sees |
|---|---|---|
| 3.0 m | 4.28 m | 3.20 m |
| 4.0 m | 5.71 m | 4.27 m |
| 4.5 m | 6.42 m | 4.81 m |

*Arithmetic from a lens of 71.0 × 56.2 degrees, **measured** on a real recorded
frame from an iPhone 18 Pro.*

So on a stage only 4 m deep, a phone looking across it covers **roughly 5.7 m
of width**. Three phones along one side cover 14 m once. Two-view coverage of
the whole width means phones from both sides, which is **about six**. That is
also the number the Stroud plan settles on for its 8 × 6 m playing area, which
is smaller but deeper, so the two shapes need a similar count for different
reasons. At three phones, the same plan leaves most of that area seen by one
phone or by none.

Every one of those footprints rests on a range of 4.5 m that the project plans
on and **has not measured on a person**. The range walk is the scenario that
measures it, and if the real figure comes in shorter, the footprints shrink and
the count goes up.

The honest way to answer this for a real venue is to run the search on its
actual plan. `Tools/room_plan.py` looks for the positions, heights, pitch and
yaw that give the most two-view coverage of a named area, and writes the tape
marks with it. [Where a plan like that comes
from](operations/get-in.html#where-a-plan-like-that-comes-from) describes it.

### Does a mixed rig of phone generations work?

**For the merge, yes.** ARKit gives 256×192 on every LiDAR iPhone and every
frame carries its own intrinsics, so a 12 Pro and an 18 Pro fuse without
anything special.

**For range and noise, nobody knows.** The LiDAR hardware changed with the
15 Pro, so whether an older phone sees as far or as cleanly is **unmeasured**,
and it is the kind of difference that shows up as one phone's corner of the
stage being worse than the others.

`Tools/model_check.py` answers it from one recorded take per phone, offline,
with no console and no phone attached. Per model it reports valid cells, the
high-confidence share, temporal depth noise in millimetres and edge share by
half-metre band, and the farthest band that is still at least half
high-confidence.

```bash
python3 Tools/model_check.py take-a.tdp4rec take-b.tdp4rec
```

The one take measured so far, an iPhone 18 Pro, gave **2 to 3 mm of temporal
noise from 1.5 to 4.5 m, all of it high confidence**, through the phone's own
smoothing. Record every phone with the same app settings, or the comparison
measures the settings rather than the hardware.

## What about aerial performers working up to 7 or 8 m?

**A floor-level rig does not reach them.** A phone on a 2.25 m stand, pitched
30 degrees up, sees to about 6.1 m above the floor at the 4.5 m range limit,
and the top of its view at that range is the furthest thing it can measure at
all. A performer at 7 to 8 m is outside it.

| Phone pitched up | Top of its view, at the 4.5 m range limit |
|---|---|
| Level | 4.4 m |
| 15 degrees | 5.3 m |
| 30 degrees | 6.1 m |
| 45 degrees | 6.6 m |

*Arithmetic, from the same measured lens and the same assumed 4.5 m range, for
a lens at 2.25 m.*

**The answer is where the phones are mounted, not what the software does.**
Aerial work at 7 to 8 m needs phones rigged **within 4 to 5 m of the action**,
on the truss or on towers, looking across or down at the aerial zone. A view
from straight above stacks limbs onto bodies, so a high phone wants an angle
rather than a plan view.

That is a coverage study against the venue's truss plan, with its own
placement rules, and it is separate from the floor rig. The floor system is
what has been built and tested so far; a test day records height data but
builds nothing on it.

{: .note }
> **Two range figures appear in our material and they measure different
> things, and neither is ours.** **Apple's figure for the sensor is "up to
> 5 metres"**, from the iPad Pro launch in March 2020. The 5 to 6 m sometimes
> quoted is **the client's own measurement** of depth holding on a person in a
> studio on 6 November 2026, not a specification. The 4.5 m used above is the
> *usable body* figure this project's coverage model plans on, the strictest of
> the three and the one to place phones by. **We have measured none of them
> ourselves at distance.**

## Can the array cope when performers cluster?

Partly, and the figure is measurable. Two standing performers were placed a
known distance apart in simulation and the shipping pipeline was run end to end
against exact ground truth:

| Separation | 1 phone | 2 phones | 6 phones |
|---|---|---|---|
| 0.25 m | one performer | one performer | starting to split |
| 0.30 m | one performer | one performer | **two, 87 % pure** |
| 0.50 m | unreliable | unreliable | two, 97 % |
| 0.60 m | two | two | two |

*Simulated. [The separation
envelope](td/testing.html#how-close-is-too-close-separation_testpy) has the
method and the full sweep.*

**Six views split two bodies from 0.30 m, where one or two views need 0.50 to
0.60 m.** That is the whole argument for more phones in one table: angles, not
processing, are what separate people.

{: .warning }
> **Two bodies in sustained physical contact cannot be separated**, by this
> system or by any markerless system at any number of cameras. While they are
> together, identity is carried by prediction and the output raises a flag so
> the receiving side can decide what to do with it. That limit is in the
> physics, so it does not improve with more phones and should never be promised
> away.

## We have a one-day get-in. How fast is registration?

The design assumes that constraint rather than fighting it. There are three
ways to place a phone, and they can be mixed on one rig.

| Method | What it needs | Good for |
|---|---|---|
| **Printed markers** | A marker taped flat at a measured position, 0.8 to 3.5 m from the lens and at least 20 degrees below horizontal | A phone that can see a floor marker |
| **Rig align** | Two phones seeing the **same surfaces** | Neighbouring phones with overlapping views |
| **Walk align** | One person walking the stage, seen by everybody | Phones that face each other across the stage and share no scenery at all |

Markers first, because they tie the rig to the room's own measurements rather
than to itself. [Markers and calibration](operations/get-in.html#4-markers-and-calibration)
is the procedure.

{: .warning }
> **One marker per A4 sheet, not two.** The marker is the whole printed image,
> and the console's default of 195 mm is A4 at true size, measured between the
> centres of the four crop marks, not the black square, which is about 89 per
> cent of that. Measuring the square instead sets every phone **11 per cent
> too near its marker**, which solves perfectly and solves to the wrong answer:
> each phone's cloud slides away from its marker, and one performer appears as
> two. [The marker size trap](operations/get-in.html#the-marker-size-trap).

What a get-in actually costs in minutes has **not been measured**, because no
get-in has happened yet. What exists is the written procedure, the tape
layout generated with the coverage plan, and a verification list to run before
the rig is called built.

## Which phones, and how old can they be?

**An iPhone Pro with LiDAR, 12 Pro or later.** The app streams the rear LiDAR
depth and there is nothing to capture without it.

Everything the project has measured was measured on **iPhone 17 Pro and 18
Pro**. Older LiDAR models should work and have not been tried, so a rig built
on them is a risk nobody here has priced. If a phone count has to be fixed
before testing, the safe reading is: the models that have been run are 17 Pro
and 18 Pro.

{: .note }
An earlier email of ours said "iPhone 15 Pro and newer". The requirement is the
LiDAR sensor, which arrived with the 12 Pro, so that line was tighter than it
needed to be.

## What is built already, and what is the effort from here?

The [proof-level page](reference/status.html) is the component-by-component
answer, and it is generated from the engineering record rather than written for
a reader. That is deliberate.

In short: the phone app, the wire protocol, the TouchDesigner hub, the console,
the client outputs and the recording format exist and run. What has **not**
happened is a rig on a stage. Simulated and living-room results do not transfer
to a venue, and the page says so per component rather than in general.

Effort and cost for a specific venue are quoted separately. Nothing in this
documentation carries prices.

## Where does a side-by-side comparison test fit?

Directly, and the tooling for it is the part that is already built. A scored
session walks a runbook step by step and **reads the numbers out of the console
rather than asking anyone to write them down**: telemetry, clock offsets,
capture age, frame rates, per scenario. It writes a machine-readable file and a
summary, and a second tool turns that file into the evidence pack, with the
build facts read off disk rather than remembered.

After the day, one command collects the takes off every phone, the console's
recordings and the screen video into a single delivery folder, checks every
take, and names in capital letters anything that is missing.

[Evidence and claims](operations/evidence.html) is how a number earns its way
into that pack, and [the delivery
folder](operations/evidence.html#the-delivery-folder) is what comes out of the
day.
