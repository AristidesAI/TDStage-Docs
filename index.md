---
title: Overview
nav_order: 1
---

# TDStage

Multi-phone LiDAR stage tracking for live performance.

Several tripod-mounted iPhone Pros stream LiDAR depth grids over UDP into a
single TouchDesigner project, which fuses them into one point cloud in a
shared stage coordinate space and drives real-time visuals. A web console
manages the devices and carries the tracking outputs to other systems.

## The parts

| Part | What it does |
|---|---|
| iOS app | Captures raw LiDAR depth and streams it. Nothing is rendered or cleaned on the phone. |
| TouchDesigner hub | Receives every phone, merges, cleans, fuses, and produces the visual output. |
| Web console | Device roster, calibration, health, and the tracking outputs to other systems. |

## Where to start

- Setting a rig up for the first time: [Quick start](operations/quick-start.html)
- Running a show: [Show day checklist](operations/show-day.html)
- Integrating another system with the tracking output: [Reference](reference/)

## How to read the numbers in these pages

Every figure says where it came from. A number measured on one phone on a
desk is not a number measured on a rig, and the difference matters when
someone is deciding what the system can do.

| Label | Meaning |
|---|---|
| **Measured, real phone** | Taken from hardware. The phone count is stated, because it changes the answer. |
| **Measured, simulation** | Taken from synthetic streams. Proves the code path, not the physics. |
| **Built, not verified** | The code exists and runs. No rig evidence yet. |
| **Not yet verified** | Needs hardware we have not had. |

A "built" item is not a working item. Do not quote one as proven.
