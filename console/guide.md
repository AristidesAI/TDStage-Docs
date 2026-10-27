---
title: Guided walkthrough
parent: Console
nav_order: 2
---

# Guided walkthrough

Three screens, with the controls that matter numbered on the picture. Read
this once before a get-in and you will know where everything is.

The numbers are drawn on the images so the pairing survives being printed,
pasted into a call sheet, or read on a phone where the caption has wrapped
somewhere else.

{: .note }
Screens were captured at a narrow browser width so nothing is cut off. The
console reflows, so a wide window puts the same controls on fewer rows. The
labels do not change.

## Starting the array

![The Dashboard's Array control panel, with six controls numbered](../assets/screens/console-dashboard.webp)

**Start show and Start all are not the same button**, and that is the thing
worth learning first.

**Start show** (1) is a staggered start. It brings phones up one at a time and
checks each one came up before moving to the next, so a phone that fails to
start is named rather than lost in a crowd of six.

**Start all** (5) sends start to everything at once. It is faster and it tells
you less. Use it when you already know the rig is healthy and you just want
pictures.

**Blackout all** (6) is not a stop. It turns the phones' screens off while they
keep streaming, which is what a phone on a stand should look like during a
performance: dark, and working. A lit phone screen is visible from the
audience and it also costs frame rate, because the phone is drawing an
interface it does not need.

**Ping all** (3) reaches every phone without changing anything. It is the
cheapest way to answer "is this thing on the network".

**Finish all** (4) ends calibration on every phone at once, which is the step
people forget after walking the markers.

**Telemetry port** (2) is where the phones send health. If this is wrong, the
phones stream perfectly and read as dead. See
[Troubleshooting](troubleshooting.html).

## Finding the phone somebody changed

![The All phones page showing the parity panel, with five controls numbered](../assets/screens/console-all-phones.webp)

A rig drifts. Someone changes a setting on one phone to test something at
11pm and nobody writes it down. This page exists to find that phone.

**Parity** compares every setting across every enabled phone and lists the
ones that disagree.

The panel is honest about when it cannot help (2): it states how many phones
are actually reporting, and names the ones that are offline rather than
quietly leaving them out of the comparison. **Parity needs two reporting
phones.** A green page with five phones offline means nothing was compared.

**Only differences** (3) hides every setting the phones already agree on. On a
healthy rig that leaves an empty list, which is the fastest possible answer.

To fix a drifted rig: pick the phone you trust as the reference (4), then
**Match every phone to this one** (5).

{: .warning }
Matching writes every setting to every enabled phone. If the reference phone
is the one that drifted, you have just spread the problem to the whole rig.
Look at the differences before you match, not after.

## Markers, and the mistake that does not announce itself

![The Markers page with the printed size field and the print controls numbered](../assets/screens/console-markers.webp)

A phone calibrates by looking at a printed marker whose real-world size it has
been told. It solves for where it is standing from the size the square appears
to be against the size it was told to expect.

So the number in **Printed size** (1) has to match the square that came out of
your printer, measured with a ruler.

**It does not fail loudly if it is wrong.** A wrong size solves perfectly
cleanly and produces a stage that is the wrong scale, consistently, in every
axis. Every distance the system reports is then out by the same ratio, which
is exactly the kind of error that survives a casual look at the output and
gets discovered during a rehearsal.

| Printed on | The square measures |
|---|---|
| A4 at true size | 195 mm |
| A3 at true size | 280 mm |

The console tells you which it has assumed (5), in the form
`all phones at 280 mm, prints on A3`. Read that line against the paper you
actually loaded.

Order of work: set the size (1), **Apply to all phones** (2) so every phone
is solving against the same number, then export (3) or print (4).

{: .note }
Applying writes the size to the roster and sends it to the phones. Loading a
stage layout also sets a rig-wide size from the layout's own sheet size, so if
you loaded a plan this may already be correct. Confirm it anyway: the plan can
only tell you what it assumed, not what your printer did.

## Sending the tracking output

![The Live view client output panel, with eight controls numbered](../assets/screens/console-live-client-output.webp)

This is the panel another system is waiting on. The stage view beside it is
the console's own picture and is not what anyone downstream receives.

**Send /track** (3) starts the tracking output to the host (4) and port (5)
beside it. Nothing is emitted until that is on, which is worth checking before
telling anyone their receiver is broken.

**Record /track** (6) writes the same output to a file. That file is what
turns an impression into a number: it can be scored afterwards for time to
acquire, identity losses and position error. See
[Evidence and claims](../operations/evidence.html).

**Hands** (7) decides whether hand positions ride in the bundle.

**Start simulator** (2) runs synthetic phones, so the whole chain can be
exercised with no hardware present. Useful for proving a receiver before a
rig exists.

### The console telling you what it cannot do

Look at **8**. The video output is reporting itself unavailable, and the line
under it gives the reason: a module is missing.

That is the system working as designed rather than failing. The console boots
with optional pieces absent instead of refusing to start, so a missing video
library costs you the video output and nothing else. The alternative, a
console that will not start because one optional dependency is absent, is
worse at 6pm on a show day.

The cost of that choice is that a dead feature can look like a bug. Which is
why the reason is printed next to it, and why
[Rig health](troubleshooting.html) exists.

## Where to go next

- [Running the console](running.html) for installation and the command line
- [The browser UI](ui.html) for every page and panel, control by control
- [Troubleshooting](troubleshooting.html) when something is not behaving
- [Built for a live show](resilience.html) for why the software is shaped this
  way
