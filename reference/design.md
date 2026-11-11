---
title: Why it is built this way
parent: Reference
nav_order: 3
---

# Why it is built this way

The decisions on this page are the ones that look arbitrary from outside,
get questioned by every new reader, and would be expensive to revisit. Each
one is here because it was argued out against measured numbers rather than
chosen by taste.

If you are about to propose changing one of these, this page is the argument
you are arguing against.

## The shape of the whole thing

```mermaid
flowchart LR
  A["Phone<br/>depth grid only"]
  B["Wire<br/>UDP, latest wins"]
  C["Receiver<br/>regenerates points<br/>on the GPU"]
  D["Receiver<br/>merges every view"]
  E["Receiver<br/>separates performers"]

  A --> B --> C --> D --> E
```

Every arrow points away from the phone. That is the single organising idea:
**the phone measures and sends, the receiver decides.** Each decision below
follows from it.

## 1. UDP everywhere, and no TCP option

A depth frame is useful for about 33 ms. After that the next frame has
replaced it and the old one is worthless. That one fact settles the
transport.

| | UDP, drop incomplete frames | TCP |
|---|---|---|
| Cost of one lost packet | One frame from one phone is dropped. The next frame arrives 33 ms later and replaces it. | The lost segment is resent, which takes about one round trip. |
| What happens to the frames behind it | Nothing. They arrive and are used. | They wait in the buffer until the resend completes. That is head-of-line blocking. |
| When the resent packet arrives | Not applicable. | Already stale, and it has delayed fresh data to get there. |

The TCP column is not a small inefficiency. A resent packet arrives after
the frame it belongs to is worthless, *and* it holds up every fresh frame
queued behind it. On an eight-phone rig inside a latency budget of around 120 ms
that stall is fatal, and it happens when the network is busiest, which is
during a show. Every real-time media protocol sits on UDP for this reason.

So the policy is: **no retransmission, no negative acknowledgement, drop any
frame with a missing packet, and let the next frame fix it.** The phone
splits each frame into numbered packets and the receiver reassembles them by
frame id. If any packet is missing, the receiver discards the whole frame.

A depth-and-confidence frame is around 150 KB at the 256×192 grid the rig
sends and around 230 KB at the 320×240 the parked AVFoundation app takes on a
LiDAR iPhone, and a safe datagram is 1472 bytes, so a frame is 100 to 160 packets. The app has to split frames itself
(application-layer fragmentation), which is what video-over-IP protocols do too.

**There is therefore no TCP mode and no TCP fallback.** Any TCP you find in
this system is a leftover; remove it. The phone-side TCP streamer was deleted in
September 2026.

> **A name that misleads.** A setting called `stage.tcpHost` holds the
> destination IP address. It is not a transport selector. The UDP point
> stream, the telemetry and the control replies all read it. Never infer a
> transport from a name: check which socket the code opens.

## 2. Depth crosses the wire, points do not

The obvious design has the phone work out where each point is in space and
send a list of coordinates. It is the wrong design, and the cost comes in
multiples rather than percentages: five times the bytes of the setting a show
uses, seven and a half times depth alone.

A phone's depth camera produces a grid of distances. A point's position in
space is `depth × ray direction (u,v)`, and the ray direction is fixed by the
camera's calibration. The receiver already has the calibration, because the
phone sends it in every frame header. So the coordinates are a deterministic
function of data the receiver already holds, and sending them anyway means
paying bandwidth to transmit information that was already there.

{: .warning }
**The grid decides every number below, and it depends on which app the phone is
running.** TDStage AR, the app the rig deploys, captures through ARKit, and
ARKit's scene depth is **256×192 on every LiDAR iPhone**: a 12 Pro, a 16 Pro
Max and an 18 Pro all send the same grid. The parked AVFoundation app takes the
first video format that offers depth and the smallest float grid behind it,
which **Apple gives as 320×240 on every LiDAR iPhone from the 12 Pro on**; this project has read it on one iPhone 18 Pro, 1.56 times the
cells. A
`stage.depthgrid` setting exists in both and is inert in both. So the left
column is the deployed rig and the simulator; the right column is the parked
app's path.

The table assumes 30 fps over a gigabit link with roughly 940 Mbit/s usable.
Its figures are **arithmetic from the transport spec** (cell count times bytes
times frame rate), not measurements. The measured transport numbers are at the
bottom of this page.

| What is sent | Bytes per cell | **Eight phones at 256×192, the rig's grid** | Eight at 320×240 | That column on the wire, framed | Share of a gigabit link |
|---|---:|---:|---:|---:|---:|
| Coordinates and colour, unprojected on the phone | 15 | **1,416 Mbit/s** | 2,212 Mbit/s | Not applicable | 151 per cent at 256×192. Does not fit either way |
| **Depth, confidence and colour as a grid** | 6 | **566 Mbit/s** | 885 Mbit/s | 937 Mbit/s at 320×240, about 600 at 256×192 | **60 per cent at the rig's grid**, 94 per cent at 320×240 |
| Depth and confidence as a grid | 3 | **283 Mbit/s** | 442 Mbit/s | 469 Mbit/s at 320×240 | 30 per cent at the rig's grid |
| Depth alone as a grid | 2 | **189 Mbit/s** | 295 Mbit/s | 313 Mbit/s at 320×240 | 20 per cent at the rig's grid |

The grid columns and the framed column are two **bases**, and saying which one
a figure uses avoids an argument later. A grid column is payload at the IP
layer: cells × bytes × frame rate, compared against the roughly 940 Mbit/s a
gigabit link carries once its own overhead is taken out. The framed column adds
what Ethernet charges per packet (38 bytes of preamble, header, checksum and
inter-frame gap, plus the UDP, IP and TDP4 headers) and compares against the
full 1,000 Mbit/s line rate.

They agree to within half a percentage point, which is the useful part: the
conclusion does not depend on which basis you pick. For a claim about whether
something fits on a cable, the framed number is the honest one, because that is
what the cable carries.

The first row does not fit on a gigabit network at all, which is the argument
for sending a grid. The chosen row fits twice over.

The second row is the one that changes character with the grid, and the grid
changed twice. At 320×240 it is 937 Mbit/s of framed traffic on a 1,000 Mbit/s
line, which is not a load to carry into a show, and that is the figure the
2.5 GbE decision was taken on. At the 256×192 the rig now sends it is about
600 Mbit/s, a 60 per cent load, and **colour from all eight phones fits a
gigabit link**. Stroud runs ARKit on every phone, decided 10 November.

Two ceilings could bind, the receiving software or the link, and it is now
settled that the link does. A load test on 2026-10-27 took the receiving
bridge to 114,500 packets per second (twelve phones of 320×240 with colour)
with no incomplete frames and every phone still at 30.0 fps, at 55 per cent of
one core. Eight colour phones offer 76,300, so the bridge has about half as
much again in hand. The 61,000 figure in older notes was the highest load
tested, not a limit.

So at that grid the constraint is 937 Mbit/s of framed traffic on a
1,000 Mbit/s line, with nothing left for a burst. That is a cabling decision rather than a software
one, and on 2026-10-30 it was taken.

### The decision of 30 October, and where it stands

On 2026-10-30 the answer was **a faster link rather than less colour**: a
switch with a 2.5G uplink and a 2.5G card in the show machine, with every
phone sending colour ([#42](https://github.com/AristidesAI/TDStage/issues/42)).

{: .warning }
> **The rig is gigabit, and is expected to stay gigabit.** The switch named for
> Stroud, a Netgear GS316EPP, has gigabit ports and **no 2.5G port at all**, so
> the show machine's link is 1 GbE whatever card is in it, and no 2.5G hardware
> has been bought. Two things make that workable rather than a compromise: the
> rig runs ARKit, where eight colour phones are about 600 Mbit/s, and the
> figures below that make 2.5G look necessary are the parked app's grid.

Eight colour phones on a 2.5 Gbit/s link is 937 of 2,500 Mbit/s: **37 per
cent**, which is headroom rather than a tightrope. Every alternative bought the
same relief by giving something up: colour from most of the rig, colour detail,
colour frame rate, or days of protocol work. This one costs a switch and a
network card.

### Recomputing any of this: `bw_matrix.py`

Every figure in this section comes from one tool, so a different configuration
does not need arguing about.

```bash
python3 Tools/bw_matrix.py --table       # the whole matrix, no sockets
python3 Tools/bw_matrix.py --selftest    # the packet maths against the spec
```

It computes from the TDP4 spec's packet arithmetic and checks itself against
the transport spec, issue 42's own table and `link_test.py`, 30 checks in all.
`--measure` sends the real simulator into the real receive bench on loopback
and verifies the bench counted exactly the bytes the maths predicted. It
refuses the show's ports, so it cannot land on a running bridge or console.

At the rig's grid, with framing, the options it prices are:

| Option | 6 phones | 7 phones | 8 phones |
|---|---:|---:|---:|
| Colour on every phone | 450 (45 %) | 525 (53 %) | **600 (60 %)** |
| Colour on three, depth and confidence on the rest | 338 (34 %) | 375 (38 %) | 413 (41 %) |
| Colour at 10 Hz on every phone | 300 (30 %) | 350 (35 %) | 400 (40 %) |
| Depth and confidence, no colour | 225 (23 %) | 263 (26 %) | 300 (30 %) |
| Depth only | 150 (15 %) | 175 (18 %) | 200 (20 %) |

*Mbit/s and the share of a gigabit line, ARKit at 256×192 and 30 fps.*

The middle two rows are the levers if a venue's link ever does bind: colour on
a subset of the rig, or colour at a lower rate than depth. Neither is needed at
a gigabit link on this grid, and both exist priced rather than as something to
work out under pressure.

### What the move to ARKit does to that decision

Every figure above is the **AVFoundation** capture grid, 320 × 240, which is
what the decision had in front of it on 30 October. The app the rig actually
deploys now captures through ARKit, at 256 × 192, and that is 44 per cent fewer
cells:

| Colour from every phone | 6 phones | 7 phones | 8 phones |
|---|---:|---:|---:|
| ARKit, 256 × 192 | 450 Mbit/s (45 %) | 525 (53 %) | 600 (60 %) |
| AVFoundation, 320 × 240 | 703 Mbit/s (70 %) | 820 (82 %) | 937 (94 %) |

*Per cent of one gigabit line, with framing. Arithmetic, confirmed against the
simulator's byte counts exactly.*

**So on ARKit, colour from all eight phones fits one gigabit** at 60 per cent,
inside the 70 per cent guideline, and the 2.5 GbE hardware is not needed for
bandwidth. It is still needed if the show runs AVFoundation, or ARKit at 60 fps,
or more than about nine colour phones.

That matters for Stroud, because the switch discussed for it has gigabit ports
and no 2.5 G port at all, so with that switch the link is 1 GbE whatever card
the machine has. As of 9 November no 2.5 G switch or card has been bought.

{: .warning }
> **Bandwidth is not the only question the link has to answer**, and the other
> one is open on both grids: what the switch does when several phones' frames
> arrive at once on separate ports. The buffer arithmetic says two colour frames
> starting within about a millisecond of each other overflow the switch named
> for Stroud. [Where the lost-packet rule stops
> holding](ports.html#where-that-rule-stops-holding-the-switchs-buffer) has the
> figures. It is settled by real phones through the real switch at the get-in,
> with colour on fewer phones as the fallback on site.

The same choice will come again, so the principle is worth stating:
**the cheapest thing in this system is usually the hardware.** A protocol
change costs days of work across the phone, TouchDesigner, the console, the
simulators, the take format and the spec, and it costs them again every time
somebody reads the wire. A faster link costs a purchase order.

{: .note }
Still to be measured: the receive path through a real network card and the
venue's switch, rather than loopback (sender and receiver on the same machine,
no card involved). The bridge is proven to 114,500 packets a second on
loopback, and eight colour phones offer about 76,300, but loopback skips the
card's own receive path, which is where a real rig would struggle. That test is
part of [#42](https://github.com/AristidesAI/TDStage/issues/42).

### What a show without colour gives up

This, rather than the megabits, is what decides it, and it is easy to miss
because "colour" sounds like appearance.

The console's person vision reads the phones' colour plane. Without it there
are **no person masks**, so performers are separated by geometry alone, and
**no hands**, because the wrist detector works on a colour image. The system
keeps tracking and keeps publishing positions (the mask stage fails open, so a
phone with no mask contributes all of its points rather than none), but two of
the things that make the tracking good are absent.

So depth-and-confidence is not "the same thing, smaller". It is a different
product: positions without appearance, and bodies separated by shape instead of
by who they look like. Know that before the link budget decides it for you.

### The fact that makes the trade cheaper than it looks

The person model has a **total** budget of inferences per second shared across
every phone, 70 by default. Each phone therefore runs at the budget divided by
the phone count, so **at eight phones the model already looks at each one about
nine times a second**, not thirty.

Two consequences follow, and they turn an apparently brutal choice into a mild
one:

- **Colour at a reduced frame rate costs the person model nothing**, because it
  was only sampling at about that rate anyway. What it costs is colour in the
  point cloud lagging a fast-moving arm.
- **Colour on a subset of phones** costs masks and hands from the phones that
  do not send it, and nothing from the ones that do.

The options, with their link loads and what each gives up, are in
[#42](https://github.com/AristidesAI/TDStage/issues/42). The decision is
Ari's; this page exists so that whoever takes it knows the model's appetite for
colour is smaller than the wire's.

Two things make reduced-rate colour work rather than merely cost less, and both
exist because sending colour intermittently used to break something:

- **In the console, a frame without colour keeps the colours it had.** Each point
  borrows the phone's last real image, up to a second old and on the same grid.
  Without that, every point of a colourless frame was **black**, so the coloured
  cloud, the video output and the appearance colours the tracker uses would have
  blinked black on every such frame, which is what sending colour less often
  was supposed to protect. TouchDesigner does not hold colour: its atlas marks a
  colourless frame as having none.
- **A phone that is moving gets slightly stale colours** for up to that second,
  because the held image is pinned to the grid rather than to the scene. On a
  phone on a stand this is invisible; know it before anybody hand-holds one.

**A hot phone can do this by itself, and currently does not.** The thermal
ladder (the ordered list of things a phone sheds as it heats up) can drop the
colour plane before it cuts frame rate, which would halve that phone's
bandwidth while keeping its rate. It is switched off by default because the
heat run of 2026-10-28 found that taking colour off the wire did not visibly
change a phone's thermal state, so it cost the person masks and the hands from
that phone and bought nothing measurable.

{: .note }
Those bridge figures were measured over loopback. That is the right way to find
the software's own ceiling, and it skips a real network card's receive path and
the switch, so the end-to-end path at this load has still not been measured.

The work does not disappear, it moves. The receiver regenerates the points
from the grid on the GPU: the 2026-07-18 architecture note put unprojecting the
393,000 cells of eight 256×192 grids at under a millisecond, and the GPU merge
path holds TouchDesigner at 60 fps with eight simulated phones. The phone's CPU
is spared and the network carries less than half the traffic.

Two consequences:

- Compression was considered and rejected. On a dedicated gigabit LAN there
  is bandwidth to spare, and compression costs latency and CPU to save
  something that is not scarce.
- The frame is **planar**, not interleaved: all the depth, then all the
  confidence, then all the colour. Planes can be omitted independently, and
  a planar depth buffer uploads to a GPU texture with no repacking.

## 3. The grid is kept, and that is what gives continuity

The grid is more than a convenient container: keeping it is what makes the
point cloud stable.

Cell `(u,v)` is **the same camera ray every frame**. So the point that cell
produces does not appear and disappear between frames; it moves along that
ray as the measured distance changes.

```mermaid
flowchart TD
  G{"Is the grid preserved<br/>on the wire?"}
  G -- "yes" --> Y["Cell (u,v) is the same ray<br/>every frame"]
  Y --> Y1["Points move<br/>rather than flickering"]
  Y --> Y2["Velocity per point<br/>comes for free"]
  Y --> Y3["Background subtraction is<br/>a 2D per-cell compare"]
  G -- "no" --> N["An unordered list of points<br/>with no frame-to-frame identity"]
  N --> N1["Only way to stabilise it<br/>is to smooth positions"]
  N1 --> N2["Smoothing adds lag<br/>and invents geometry"]
```

The whole trick is **coherent identity, raw positions.** The system keeps
identity per cell, and it does *not* low-pass (smooth over time) the position.
Each frame shows the raw current depth. You get a point cloud that does not
strobe into the generative visuals, without the lag of positional smoothing.

Three things fall out of it:

- **Background subtraction becomes trivial.** A cell whose depth sits at the
  learned background distance is background, so dropping it is a 2D compare
  rather than a 3D lookup on the hot path.
- **Per-point velocity is free**, as change in position over change in time
  per cell.
- **A dropped frame costs nothing positionally.** Since each cell is the
  same ray next frame too, losing a frame loses 33 ms of update, not
  continuity. This is what makes the drop-incomplete-frames policy in
  section 1 safe.

**The caveat, stated because it is easy to overclaim.** This is *ray*
identity, not *surface* identity. A static surface's point slides along its
ray as the distance changes, which is correct. But a performer moving
sideways sweeps *across* cells, so the surface under a given cell changes at
a silhouette edge. The grid gives stable ids, per-point velocity, flicker
reduction and near-free background subtraction. It does not give true
per-material-point tracking, which would need per-point scene flow layered
on top. Do not describe it as tracking the same piece of a body over time.

## 4. Performer separation happens on the receiving side

Separating performers is the hard requirement, and no part of it can happen
on a phone. The research came before the decision.

```mermaid
flowchart TD
  Q{"Where can performers<br/>be separated?"}
  Q --> P["On the phone"]
  Q --> R["On the receiver"]
  P --> P1["One body per device<br/>in the body-tracking API"]
  P --> P2["The multi-person API caps low<br/>and its own docs warn it<br/>merges people who cluster"]
  P --> P3["All of it is 2D, and one phone<br/>cannot associate with another"]
  R --> R1["Every phone's view is already<br/>in one stage coordinate space"]
  R --> R2["A performer hidden from one phone<br/>is seen by another"]
  R1 --> R3["Separate in 3D,<br/>hold identity over time"]
  R2 --> R3
```

The on-device route fails on the APIs' own definitions, so no tuning rescues
it. ARKit's body anchor tracks a single person per device. Vision's 3D body
pose returns only the most prominent person. The one multi-person API caps at
a handful of people, is two-dimensional, and Apple's own documentation warns
it may miss people or combine them when they cluster, which is the case that
has to work. And no phone can associate what it sees with what another phone
sees, because it does not know the other phone exists.

**Occlusion has one answer: more viewpoints.** No amount of processing
recovers a body behind another body from the view that cannot see it. A
second camera that can see it recovers it at once. This is why the rig has
six to eight phones rather than one good one,
and it is why the aiming step at a get-in is a coverage decision and not a
framing decision.

![Concept drawing: a plan view of six phones around a stage with overlapping view cones and one performer seen by three of them, and a side elevation with truss-rigged phones within 4 to 5 m of an aerial performer and a floor phone out of range.](../assets/img/multi-view-concept.webp)

*The original brief's concept drawing. Its 14 m stage and truss rig are superseded by Stroud's 8 x 6 m area with phones on stands; the idea it shows, one performer covered by several angles, is unchanged.*

That makes the camera positions a design input, not a convenience. Angles
planned on paper are what make separation possible later; a rig where every
phone looks from roughly the same side has redundancy but no additional
information.

### Sparse body points: 17 joints per performer, from several phones, with the depth as referee

{: .note }
> **Off by default, and proposed rather than agreed.** `tracking.bodyPoints`
> adds one message per performer, `/track/performer/body`, carrying 17 joints as
> stage points with a confidence each. It is inside the client contract's
> "skeletons stay shallow" line: points, no bones, no rotations. The message
> is to be agreed with Default Ltd on 17 November. **It is not good enough to
> switch on for a show yet** (#66, 11 November): through the real keypoint
> model on rendered people the fused limb error is about 7 to 10 cm median
> with tails of 40 to 70 cm, and a red-team review the same day found two
> high findings (below). The verdict: it lands **off** with no behaviour
> change; it may be switched on at the 18 November dry run only as a labelled
> experiment, and only after the client confirms their bus accepts a bundle
> holding only a body message; **not for Stroud** until the two high findings
> are fixed. Its cost is **measured on synthetic scenes**, and it has **not run
> on a multi-phone rig**. Off, it sends nothing and costs one attribute read.

The same reasoning that puts performer separation on the receiver puts body
points there. One phone sees a body from one side, in two dimensions, and
cannot tell which of its joints belong to which performer when two overlap.
Several phones, each already in stage coordinates with its own intrinsics and
extrinsic in every frame, can.

```mermaid
flowchart LR
  A["Each phone's frame:<br/>RGB + depth on one grid,<br/>K and E in the header"] --> B["Keypoint model on the colour:<br/>17 COCO keypoints per person<br/>(u, v, confidence)"]
  B --> C["Lift each keypoint through<br/>THAT frame's depth<br/>(the wrists' own lift)"]
  C --> D["Match each phone's person<br/>to a performer<br/>(plan distance 0.8 m)"]
  D --> E["Per joint, across phones:<br/>triangulate the rays,<br/>8 px reprojection gate"]
  E --> F["Depth check: a view whose lifted<br/>point sits more than 0.25 m<br/>in front is an occluder, dropped"]
  F --> G["Position: the depth points<br/>within 0.12 m of the<br/>triangulated joint, weighted median"]
  G --> H["/track/performer/body<br/>17 x (x y z confidence views)<br/>own bundle, after the frame's"]
```

**Per phone**, every keypoint with a confidence at or above
`vision.minJointConf` is lifted through its own frame's depth, with the same
function the hand tracking uses for the wrists. That gives a 3D point per joint
per phone, but a poor one on its own: a keypoint model guesses through
occluders, and a guessed pixel lifts to the depth of whatever is in front.

**Across phones**, each phone's person is assigned to the nearest eligible
performer in plan within 0.8 m, one person per phone per performer. Then, joint
by joint, the rays from every phone that reported it are triangulated: a search
over view pairs picks the pair whose midpoint the most confidence agrees with
within 8 pixels of reprojection, then a confidence-weighted least-squares
intersection over every view inside that gate, re-gated and solved once more.
That 8 px is the gate at a 256-wide grid and scales with each view's own width,
so a phone sending 320 is gated at 10 px rather than held to a tighter angle
than its neighbour.
Two rays closer than 5 degrees apart cannot be the pair that seeds the solve,
because depth along nearly parallel rays is unconstrained. Two phones at a
decent angle to each other triangulate perfectly well, which the two-phone row
of the table below is; two phones looking from almost the same direction do
not, and neither does a joint only one phone reported. Both of those fall back
to the depth points.

**The depth is the referee, and then the measurer.** A view whose lifted point
lies more than 0.25 m in front of the triangulated joint is an occluder: the
keypoint was placed on something standing between the phone and the performer.
That view is dropped and the joint re-solved. In the default `hybrid` mode the
triangulation then mainly chooses which views to trust; the position reported is
the confidence-weighted median of the surviving views' depth-lifted points
within 0.12 m of the triangulated joint. That 0.12 m is a fixed radius in the
code, not a setting, and it is distinct from the 0.25 m occluder gate: 0.25 m
decides which views are lying, 0.12 m decides which depth points become the
published position. If none confirms, the depth consensus of the surviving
views is used when it lies within 0.25 m of the triangulation, otherwise the
triangulated point itself. At 256 x 192, one pixel of keypoint
noise is about 2 cm at 4 m, and the LiDAR is better than that, so the
triangulation referees and the depth measures.

Three other modes exist for comparison and diagnosis: `combined` reports the
triangulated position after the same occluder check, `triangulate` skips the depth checks, so a triangulated joint comes from the
rays alone while a joint only one phone sees still gets that phone's
depth-lifted point, `depth` has the phones vote with no triangulation: the view whose lifted
point has the most confidence within 0.25 m of it wins, and its group's
confidence-weighted median is the position.

**What a joint's numbers mean.** `confidence` is the mean keypoint confidence
of the views used, scaled by their share of the confidence of every view that
reported the joint: agreement keeps it, rejected views cost it. `views` is the
number of phones consistent with the joint. A joint no phone supplies is sent
as `0 0 0 0 0`, never NaN, because a NaN would poison the bus's One Euro
filter; confidence 0 means ignore the position. Positions are raw unless
`tracking.bodySmooth` is above zero (the bus smooths positions itself).

**Which performers get one.** Confirmed performers that are neither coasting
nor clustered, the same rule the hands use: a clustered blob would hand the
fuser the wrong body's limbs. Each body message rides in its own OSC bundle,
one per performer, sent right after the frame's bundle. At about 470 bytes a
body, three of them inside the frame's own bundle would push it past one
1500-byte packet and fragment it; keeping them separate keeps the bodies from
pushing the frame's bundle past one packet.

#### Why triangulation plus depth, and not a multi-view network

Two families of method turn several camera views into one 3D body. Learned
end-to-end multi-view networks (VoxelPose, Faster VoxelPose, MvP, TEMPO,
MVGFormer) take every view into one network that outputs 3D joints. Geometric
fusion (mvpose, VoxelKeypointFusion, RapidPoseTriangulation) runs a 2D
keypoint model per camera and triangulates across the calibrated cameras.

The deciding evidence is a published study of exactly this rig's situation, a
camera layout the models were never trained on (Bermuth et al.,
VoxelKeypointFusion, 2024, arXiv 2410.18723; averaged over four unseen
datasets):

| Method | Correct parts (PCP) on unseen rigs | FPS |
|---|---|---|
| MvP (learned) | 1.8 | 3.2 |
| VoxelPose (learned) | 37.6 | 13.9 |
| VoxelPose, retrained on synthetic data for the rig | 73.3 | 10.9 |
| Faster VoxelPose (learned) | 72.1 | 60.9 |
| TEMPO (learned, temporal) | 59.1 | 29.7 |
| mvpose (geometric) | 77.6 | 28.1 |
| VoxelKeypointFusion (geometric) | 85.3 | 27.2 |

Learned models transfer poorly to a new camera layout and need retraining per
rig. This rig changes with every venue, so per-rig retraining is not an
option. The same group's RapidPoseTriangulation (arXiv 2503.21692) is the
fastest of the geometric family, about 0.1 ms per frame for the triangulation
itself, which is why the fusion here is written to its shape: in numpy, from
the paper, not copied (the repository shows no licence). Depth is what this
rig has that those RGB rigs lack, and it is used for the two things RGB-only
triangulation cannot do: give a joint seen by one phone a position at all, and
drop a view that is looking at an occluder.

The 2D source is whichever observer already reports keypoints: YOLO pose in
the worker, or Apple Vision's body pose on a Mac. No new dependency, and
YOLO's cost was already measured. Turning body points on
also turns on the YOLO keypoint pass when YOLO is the primary observer and
`/track` hands are off, at about 10 to 15 ms per YOLO frame (a figure from a
comment in the code, not re-measured for this feature). RTMPose or RTMW would be the upgrade if YOLO's keypoints on
256 x 192 colour prove too coarse; they would plug in behind the same
17-name interface and are not added.

Not taken: the learned volumetric networks (retraining per venue), TEMPO (adds
latency by design, being temporal), MVGFormer (speed on a show PC not
published), and any commercial multi-iPhone mocap, which needs its own app on
the phone and would stop the LiDAR stream.

#### The numbers, and what kind each one is

**Accuracy, simulated** (`python3 WebConsole/body_points.py --compare`: 150
poses per rig, joints rendered as spheres of 5 cm radius so the lift reads skin, 2 px of
2D noise, 10 % of views with an occluder in front, 5 % of keypoints 10 to 40 px
off, phones at 4 m). Median / 95th percentile joint error in mm, and the share
of joints more than 10 cm off:

| Rig | `hybrid` (default) | `triangulate` only | `depth` only |
|---|---|---|---|
| 2 phones, 90 degrees apart | 40 / 148, 8.7 % | 63 / 199, 18 % | 41 / 825, 21 % |
| 3 phones, ring | 29 / 102, 5.4 % | 54 / 125, 9.8 % | 29 / 238, 9.2 % |
| 8 phones, ring | 21 / 49, 0.1 % | 32 / 59, 0.1 % | 23 / 58, 0.7 % |

The medians are mostly the lift's skin offset, which no fusion removes. The
tails are where the modes differ: depth alone has no way to reject an
occluder, triangulation alone keeps an occluded view in the solve and reports
the ray intersection rather than the depth.
None of these figures has been checked against a real body on a real rig.

**Cost, measured on synthetic scenes** (`--bench`, one Mac): fusion 0.38 ms
per `/track` tick at 3 phones and 3 performers (95th percentile 0.46 ms),
0.65 ms at 8 phones and 3 performers, one vectorised call per tick. The depth
lift is 0.35 ms per person per phone frame and runs on the observer thread,
not the tick. Off: one attribute read per `/track` tick and one per person per observer
frame, nothing else.

**End to end, one real phone, once:** take T1 replayed into a sandboxed scratch
console produced 1,625 body messages against 1,762 performer messages, every
argument well formed (id plus 17 x 5), `views` = 1 throughout (a one-phone take),
largest bundle 740 bytes (bodies were still inside the frame's bundle in that
run), no errors. The 137 performer messages with no body were not broken down: coasting and
clustered performers get none by rule, and a performer with no phone frame
younger than 0.15 s carrying a person within 0.8 m of it gets none either. That run predates the
own-bundle change, which has since been covered by self-tests only. There has
been no multi-phone run.

#### What the red-team review found (11 November)

A review against the code and the real-model harness, summarised in #66 (the
full report is kept outside the repository). Two findings are high, and they
are why the feature is not for Stroud as it stands:

- **Wrong-side and ghost joints.** With every tripod at one height, almost any
  two views agree inside the 8 px reprojection gate. So a single view in which
  the keypoint model has swapped left and right (a back or side view does
  this), if it is slightly more confident, wins the pair search, and `hybrid`
  emits a triangulated point that no depth confirms. Synthetic, one swapped
  view: the left wrist more than 15 cm off in 23 of 30 poses at 3 phones
  (median 503 mm), 28 of 30 with 2 phones at 90 degrees, none at 6 to 8 phones
  unless three adjacent views swap. On the real-model harness most errors over
  30 cm are swapped views: 41 of 49 on a 3-phone ring; 137 of 191 at 8 phones
  with three people, plus 44 from the wrong person. `hybrid` was the best mode
  in none of these rigs.
- **Lag and jitter from unsynchronised phones.** Views up to 0.15 s apart are
  fused as if simultaneous. Walking at 1.5 m/s with a wrist moving at 3 m/s:
  hip median 98 mm, wrist 95th percentile 270 to 504 mm, wrist tick-to-tick
  jumps 156 to 500 mm at the 95th percentile, and the body trails its own
  `/track/performer`. The receiver rule that follows: do not derive a
  performer's position from a joint while the performer's own position is in
  the same bundle, because during movement they disagree and the body is the
  one behind. The scope that makes it useful rather than only prohibitive:
  until time alignment lands, take where the performer is from
  `/track/performer` and use the body only for the layout of the limbs relative
  to it. A gesture keyed to an arm's direction is
  reasonable; a cue keyed to where that arm is in the room is not.

Three medium findings belong here too. As it behaves today, the fusion runs on
the `/track` thread before the frame is sent, 0.3 to 2.3 ms on the bench and 12 to 18 ms on a bad
tick under contention, so switching body points on delays the existing
performers and hands as well. Views from the wrong person are taken when
performers are close, and a clustered pair (a duet) gets no body at all. And
the one-bundle-per-body wire shape has never been through the client's bus,
which is known to drop a hand it cannot match to a performer in the same
frame; that is on the 17 November agenda and is the thing most likely to
change the format.

Two passes worth having when robustness is the question: garbage or NaN
keypoints, bad cameras and a dead or slow worker raise no exception and put
nothing non-finite on the wire, with performers and hands continuing; and a
25-minute soak (one take replayed as two identical phones, depth path only)
held memory flat, `/track` at 30 Hz, no errors, no restarts, 61,281 body
messages, none non-finite.

A fix pass for the two high findings and three of the others (swap hypothesis
and ranking by agreeing views, a two-sided depth gate, no unconfirmed
triangulation, time alignment as the hands do it, frame sent first) was
running when this was written, measured before and after on the real-model
harness. If it lands before the integ-c merge these figures move; if not, the
page carries them as the published limits.

**Known gaps** (#66): no half-pixel correction between YOLO pixel coordinates
and cell centres (at most 0.5 px of bias); no time alignment between
unsynchronised phones: views up to 0.15 s apart are fused as they are, so a
limb that moved between them reprojects outside the 8 px gate and is dropped
rather than averaged, and older observations are not views at all; the lift is not yet vectorised; inverted performers are
expected to be missed by COCO keypoint models as they are by the person model
(not measured for keypoints), so #62's rotate-and-retry would apply. The toggle is in the generated Tuning panel, not in
the hand-written Live view, and body points reach neither TD's consensus view
nor F1.

**Known gaps** (#66): no half-pixel correction between YOLO pixel coordinates
and cell centres (at most 0.5 px of bias); no time alignment between
unsynchronised phones: views up to 0.15 s apart are fused as they are, so a
limb that moved between them reprojects outside the 8 px gate and is dropped
rather than averaged, and older observations are not views at all; the lift is not yet vectorised; inverted performers are
expected to be missed by COCO keypoint models as they are by the person model
(not measured for keypoints), so #62's rotate-and-retry would apply. The toggle is in the generated Tuning panel, not in
the hand-written Live view, and body points reach neither TD's consensus view
nor F1.

## 5. The phones are deliberately dumb

A phone captures depth and sends it. It does not render, clean, cluster,
track or decide. This is a choice, and these are the reasons.

| Reason | Detail |
|---|---|
| A phone cannot see the problem | Separation is a multi-view problem. A single phone lacks the information to solve it, however much compute it has. |
| Processing on a phone cannot be inspected | Eight phones each making their own decisions is eight black boxes. One receiver making all of them is one place to look when the answer is wrong. |
| Thermal headroom is the scarce resource | A phone on a stand under stage lighting, streaming for hours on mains, is thermally constrained. Capture is what it must never drop. |
| Raw data can be reprocessed | A recording of what the phone sent can be replayed through a changed receiver. A recording of what a phone concluded cannot. |
| One streamer, one lifecycle | There is a single streaming path on the phone and a single place that owns the connection. Fewer states means fewer states that can be wrong at a venue. |

The capture itself is raw on purpose: invalid cells stay invalid rather than
being filled in. Smoothed, hole-filled depth looks better on one phone and is
worse for fusing several, because it invents geometry the other phones will
contradict.

### Which capture API, and why that changed

{: .note }
> **Since 2026-11-06 the project ships one phone app, TDStage AR, and it
> captures with ARKit scene depth.** The original app captured with
> AVFoundation's LiDAR depth camera with filtering turned off, and used ARKit
> only for marker calibration. That app is parked, not deleted. Anything you
> read elsewhere describing AVFoundation as *the* capture path, including
> older notes in the repository, predates this.

The original comparison is still the reason the first app was built the way it
was, and it is still true about the two APIs:

| | AVFoundation, unfiltered | ARKit scene depth |
|---|---|---|
| The sensor | The same LiDAR, through the same densification | The same LiDAR, through the same densification |
| Streaming resolution | Higher | Lower |
| Filtering | Can be turned off | Cannot |
| Body tracking | Not used | One body per device, and needs camera motion a tripod will never give it |

What changed is not that table. It is that **edge bleed turned out to cost more
than resolution**. Depth at the silhouette of a body smears onto whatever is
behind it, and those smeared points survive into the fused cloud as a halo that
no receiver-side cleanup removes reliably. The ARKit fork went after that
directly: a per-pixel bimodal edge cull, a temporal median, flip hysteresis,
and ARKit's own person matte. On 6 November the project kept the fork and
parked the other app rather than maintain two.

Two things about that decision should be said plainly, because they are the
questions a reviewer asks:

- **The A/B was never run.** Comparing the two paths on resolution against
  confidence on a real performer is still open (#10). The choice was made on
  the edge-bleed work, not on a measured comparison of the two capture paths.
- **ARKit costs latency, and the measurement is not a clean comparison.**
  Capture to send on 28 October: ARKit **62 to 78 ms with two phones**,
  AVFoundation **37 ms with one phone**. Different phone counts, so the gap is
  not all attributable to the API. It has not been re-measured at equal
  configuration.

Both APIs are the same sensor underneath, so neither buys better raw depth.

## 6. The limit that must never be claimed away

**Identity through sustained physical contact is not measurable, by this
system or by any markerless system, at any number of cameras.**

When two bodies are physically together there is no low-density gap for
clustering to find and no seam in the fused surface. The information is not
there to be processed. This is the explicit motivating problem of the
state-of-the-art research in the field, whose solution needs per-subject
learned priors and optimisation over a whole recorded sequence, and is
offline.

So the live behaviour is this, and it is the honest behaviour rather than a
shortfall:

- Do not attempt to re-derive the boundary from the current frame.
- Carry identity through by prediction.
- Reacquire on separation.
- **Flag the identity as uncertain**, so whatever consumes the output can
  decide for itself whether to trust it.

That flag is the feature. A downstream designer can use a system that says
"I am guessing", and cannot use one that guesses silently.

More phones do not fix this. More phones fix occlusion, which is a different
problem: occlusion means the information exists but this camera cannot see
it, and contact means the information does not exist. Adding viewpoints
helps the first and does nothing for the second.

Say it plainly and early, to anyone deciding what the system will do. It is a
property of the physics, not a defect in the implementation, and it does not
improve with budget.

## What this all costs, measured

These figures show whether the decisions paid off. Every one is from
synthetic streams, not from phones.

| Figure | Value | Label |
|---|---|---|
| GPU merge path, frame rate held | 60 fps at 8, 12 and 16 streams, on a development Mac with the person model idle and no content rendering | Measured 2026-10-26, simulation at 256×192, depth and confidence |
| Transport loss up to 16 streams | 0 incomplete frames, at 573 Mbit/s | Measured 2026-10-26, simulation at 256×192, depth and confidence |
| Bridge to TouchDesigner delay | 9.5 ms median, 15.3 ms at the 95th percentile | Measured 2026-10-26, simulation at 256×192, depth and confidence |
| Bridge receive capacity | 114,500 packets per second with no drops, 55 % of one core (twelve phones of 320×240 with colour). An earlier 61,000 was the highest load then tried, not a limit | Measured 2026-10-27, loopback |
| Eight phones with colour, offered load | 49,000 packets per second at the rig's 256×192; about 76,000 at the parked app's 320×240 | Arithmetic from the frame size |

Real-phone evidence is **two phones in one room**, measured together since
2026-10-28. Nothing in this table was produced by eight real phones, and
simulated phones do not get hot, fight for a switch or stand in front of each
other. See
[Evidence and claims](../operations/evidence.html).
