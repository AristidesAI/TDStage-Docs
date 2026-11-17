---
title: TouchDesigner
nav_order: 5
has_children: true
---

# TouchDesigner hub

The hub receives every phone's stream, merges them into one cloud in stage
coordinates, cleans and fuses that cloud, and produces the visual output.

## The pages

| Page | For |
|---|---|
| [Running the hub](running.html) | Opening it, the ingest topology, and the ten-second check that something is arriving |
| [How the pipeline is built](pipeline.html) | The stage order, the two merge paths, where each transform is applied, and why it is built this way |
| [Parameters](parameters.html) | Every parameter, what it does, when it is reasonable to touch it, and which merge path reads it |
| [Outputs](outputs.html) | The five Out operators, what each carries, and what must never ride NDI or OSC |
| [Testing without hardware](testing.html) | Synthetic phones, recorded takes, the receive-side bench and the self-tests |
| [Maintenance](maintenance.html) | The save-and-verify loop, the drift check, and where learned state lives |
| [Consensus view](consensus-view.html) | The console's own person tracking, received in TouchDesigner from a copy of every `/track` bundle (UDP 7001) and kept as CHOP data. In the tox since v95 (16 November) on its own Consensus page, Active off by default. Drawn since v96 (17 November): a cylinder per performer and a sphere per hand in the preview render, while `Consensusshow3d` is on, tested only from a recorded `/track` file (simulated). No consensus Out operator, on purpose: content reads the two CHOPs with a Select CHOP. |

If you are trying to get a rig arriving, start with
[Running the hub](running.html). If you are integrating other work with the
cloud, read [Outputs](outputs.html) first, then
[How the pipeline is built](pipeline.html).
