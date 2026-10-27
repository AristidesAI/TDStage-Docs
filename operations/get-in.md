---
title: Rig get-in
parent: Operations
nav_order: 4
---

# Rig get-in

Building the rig in a venue, in the order that avoids rework. Assumes the
phones were prepared beforehand. If they were not, stop and do
[Preparing a phone](phone-preparation.html) first, because several of those
steps need internet the venue will not have.

## Order of work

The order is not a preference. Each step is the thing that lets the next one
be checked, so doing them out of order means doing them twice.

```mermaid
flowchart TD
  N["Step 1 Network<br/>addressing settled"]
  P["Step 2 Phones on the network<br/>visible in the console"]
  S["Step 3 Stands and aiming"]
  M["Step 4 Markers and calibration"]
  V["Step 5 Verification"]

  N -- "a phone cannot be seen<br/>until it has an address" --> P
  P -- "aiming needs the live view,<br/>which needs the phone visible" --> S
  S -- "calibration solves the pose<br/>a phone is actually in" --> M
  M -- "nothing can be verified<br/>before it is calibrated" --> V
```

Read each arrow as the reason, not as a sequence number.

- **Network before phones**, because an unaddressed phone cannot appear in
  the console, and a phone you cannot see is a phone you cannot check.
- **Phones before stands**, because aiming is done from the live view. Doing
  stands first means climbing to every stand twice: once to mount, once
  again when you find out what it sees.
- **Stands before calibration**, because calibration solves for where a
  phone actually is. Move a stand afterwards and the solve is stale and
  silently wrong.
- **Calibration before verification**, because every check at the end is a
  check of the calibrated rig.

## 1. Network

Phones reach the receiving machine over Ethernet. Wi-Fi works and is the
fallback, but it costs latency and drops frames under load, so it is not what
a show runs on.

The gap is not marginal. A phone on a cable measured **0.55 ms** to the
receiving machine against roughly **8 ms** over Wi-Fi (measured, real phone,
one phone). An iPhone on a USB-C cable presents a real network link, so the
stream crosses the cable with nothing special done to it.

That matters more than the raw numbers suggest, because of what the depth
stream is. One frame from one phone is about a hundred packets, and a frame
missing any one of them is discarded whole rather than resent. Eight phones
with colour offer around 49,000 packets per second (measured, simulation).
Wi-Fi under load drops packets in bursts, and a burst that costs single
packets across many frames costs those whole frames. See
[Why it is built this way](../reference/design.html).

### Addressing, and the trap in it

**Check this before you need it.** A plain unmanaged switch does not hand out
addresses. If the rig has no router and no DHCP server on it, nothing on that
network gets an address automatically and every phone needs a static one.

Work out which case you are in before the get-in, not during it.

```mermaid
flowchart TD
  Q{"Is anything on this network<br/>handing out addresses?"}
  Q -- "a router" --> AUTO["Automatic.<br/>Phones appear on their own"]
  Q -- "a machine sharing<br/>its connection" --> AUTO
  Q -- "switches only,<br/>nothing else" --> MAN["Nothing gets an address.<br/>Every phone needs a static one,<br/>and so does the receiving machine"]
  Q -- "not sure" --> CHK["Run the doctor check<br/>on the receiving machine"]

  CHK -- "reports a LAN address" --> AUTO
  CHK -- "reports no LAN address" --> MAN
  MAN --> PLAN["Write the address plan<br/>on the case, before travel"]
```

| Rig has | Addressing | What to do |
|---|---|---|
| A router, or a machine sharing its connection | Automatic | Nothing. Phones appear on their own. |
| Switches only | **None** | Set a static address on every phone and on the receiving machine. |

People expect a switch to sort this out because almost every switch they have
plugged into before had a router somewhere behind it. This one may not.

Decide the address plan in advance and write it on the case. A rig discovered
to need static addressing at 9am on a show day costs an hour.

The receiving machine can answer this for you. Run:

```
python3 WebConsole/doctor.py
```

On a switches-only rig with no static plan it fails with `no LAN address:
every interface is link-local, virtual or Tailscale`. With a single phone on
a cable it warns `USB link only, no LAN address`, which is fine on a desk and
wrong at a venue.

### Confirming the link

A phone should reach the console without anyone typing its address. If you
have to type an address to see a phone, the network is wrong and typing the
address only hides it.

## 2. Phones on the network

Per phone:

1. Power it from mains, not battery.
2. Confirm it appears in the console's device list by itself.
3. Confirm its device id is unique. Two phones sharing an id overwrite each
   other's frames, and the symptom looks like a dropout rather than a clash.
4. Confirm it reports charging and a nominal thermal state.

### The firewall trap

The console learns a phone's address from the health messages the phone
sends, and those arrive on a port TouchDesigner owns on the show machine. If
the firewall has no rule for TouchDesigner, the result is a specific and
confusing state: **phones show as online from their point data, but with no
battery, no temperature and no frame rate**, and control messages cannot
reach a phone whose address was never typed in.

The Windows setup script adds the rule. The doctor check confirms it. Run
both before deciding the network is fine.

## 3. Stands and aiming

Each phone goes where the coverage plan puts it. Coverage is the whole reason
there is more than one phone: a performer hidden from one camera has to be
visible to another, and that only happens if the angles were planned.

Aim with the console's live view rather than by eye. What matters is what the
phone sees, not where the phone points.

### Why aiming is a coverage decision, not a framing one

Occlusion has exactly one answer: another viewpoint. A performer behind
another performer cannot be recovered by any amount of processing of the view
that cannot see them, and is recovered trivially by a camera that can. That
is the entire reason there is more than one phone.

So the test of a phone position is not whether the picture looks good. It is
whether that phone sees something the others do not.

```mermaid
flowchart TD
  Q{"Does this phone see part of<br/>the playing area that the<br/>others see poorly?"}
  Q -- "yes" --> K["Keep the position"]
  Q -- "no, it mostly<br/>duplicates another" --> M["Move it.<br/>Duplicate angles add density,<br/>not information"]
  Q -- "it sees a gap<br/>nothing else covers" --> P["Priority position.<br/>Note it before you leave"]
```

A rig where every phone looks from roughly the same side has redundancy and
little extra information. Two phones looking across the playing area from
opposite sides see more of a body standing between them than four phones
ranged along one side.

## 4. Markers and calibration

Calibration puts every phone into one shared stage coordinate space by
showing them printed markers at known positions.

### The marker size trap

**The size in the console must match the size you actually printed**, and the
thing you measure is not the obvious one.

{: .warning }
Measure the **whole marker image**, white margin included, between the centres
of the four crop marks. Not the black square: that is about 89 % of the image,
so ruling it and typing what you read sets every phone 11 % small.

| Printed on | Between the crop marks | The black square alone |
|---|---|---|
| A4 at true size | **195 mm** | about 174 mm |
| A3 at true size | **280 mm** | about 249 mm |

A fresh roster defaults to **195 mm**, which is A4 printed at true size. So
printing A4 and leaving it alone is correct. **Printing A3 and leaving it alone
is not**, and nothing warns you, because a wrong size solves perfectly well. It
just solves to the wrong answer.

What that wrong answer looks like is worth knowing, because the obvious guess
is wrong twice over. Depth is metric LiDAR, so nothing is rescaled and the
floor does not tilt. The phone simply believes it stands nearer its marker than
it does, and slides its **whole cloud** away from itself along that sight line
by that fraction of its distance to the marker — about 0.66 m for a phone 6 m
out at 11 % small. Each phone slides its own way, so the rig stops agreeing
with itself. The full working is in
[the console walkthrough](../console/guide.html#markers-and-the-mistake-that-does-not-announce-itself).

**A loaded stage layout does not reach the phones.** The plan import reads each
marker's sheet size and applies one rig-wide size to the console's **roster**,
and sends nothing. Until you press **Apply to all phones**, every phone still
holds whatever it was last told — so the console can read `every phone 280 mm`
while the phones calibrate on 195. Press it after every layout load, and
confirm the number against the paper that came out of your printer rather than
the paper the plan assumed.

### Placing markers

1. Put markers at positions you have measured, not estimated.
2. Tape them flat. A curled marker reads as a tilted one.
3. Keep them out of the path of anyone who will be moving around the stage.
4. Leave them up until calibration is verified, not until it is run.

## 5. Verification before you release the rig

Do not call a rig built until all of these pass:

- [ ] Every phone appears in the console without a typed address.
- [ ] Every phone has a unique device id.
- [ ] Every phone is charging and nominal thermally.
- [ ] The marker size in the console matches the printed markers.
- [ ] Calibration has solved for every phone.
- [ ] **One person stands in the middle and the rig sees one person.**
- [ ] A person walking the playing area stays tracked as they cross between
      the areas each phone covers.
- [ ] The output reaches whatever is consuming it.

### The one-person test

Put somebody in the centre of the stage, where two phones on opposite sides
can both see them, and have calibrated on **different** markers. Then look at
the cloud.

| What you see | What it means |
|---|---|
| One body, in the right place | Those two phones agree. Move on. |
| **Two bodies**, separated along the line between the two stands | A marker size is wrong. The gap is roughly 11 % of the two phones' distances to their markers added together, so about 1.3 m for two phones 6 m out. |
| One body, in the wrong place | Both phones are off the same way. Check the size, then check the marker positions in the plan. |

What it does not catch, which matters as much as what it does:

- **Shifts that happen to cancel.** If every phone's marker lies in roughly the
  same direction from it, every cloud slides the same way: they still agree
  with each other, and the whole stage is simply in the wrong place. Two bodies
  prove an error; one body does not prove correctness.
- **Small errors.** A 1 % size error at 6 m is 6 cm, which you will not see by
  eye.

So run it a second time with a pair of phones at ninety degrees to the first,
which covers the other axis and breaks the cancelling case.

A console-side version of both halves is proposed in
[#41](https://github.com/AristidesAI/TDStage/issues/41): a passive check that
compares what each phone thinks the centroid of one person is, and a separate
button that compares the agreed position against a marked spot whose stage
coordinates you know. The second is the one that can prove correctness rather
than agreement. Until that exists, the eye is the instrument.

The walking test is still the one that catches coverage problems. A rig can
pass every other check and still have a gap that only shows when someone walks
through it.

## What to record before you leave

Write down what the rig actually is, not what it was planned to be:

- Which phone id is on which stand.
- The addressing scheme used.
- The printed marker size.
- Anything that differs from the plan, and why.

The next person at this venue is possibly you, six weeks later, with no
memory of any of it.
