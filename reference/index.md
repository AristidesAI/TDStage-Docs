---
title: Reference
nav_order: 6
has_children: true
---

# Reference

This section covers ports, wire formats, the HTTP and OSC surfaces, and the
reasoning behind the design. It is for someone integrating another system
with this one.

If you are at a venue with a rig that will not work, you are in the wrong
section. Go to [Operations](../operations/).

## What is in here

| Page | Answers |
|---|---|
| [The tracking output](track.html) | **Start here if you are writing the receiver.** Every message and argument, the coordinate frame, what an id promises, and what the system guarantees and what it does not. |
| [The field stream](field.html) | The second output: occupied 5 cm voxels, people as floor footprints, and the phones' poses, on a WebSocket. What is in each message and what it was computed from. |
| [Ports and topology](ports.html) | What listens where, which surface is UDP and which is not, and what must never carry depth. |
| [Why it is built this way](design.html) | The decisions that look arbitrary from outside: UDP with no TCP option, depth on the wire instead of points, dumb phones, receiver-side separation, and the one limit that must never be claimed away. |
| [Dependencies and requirements](dependencies.html) | What each side needs to run, where it is declared, and what breaks without it |

## What you are integrating against

There are four surfaces, and they are not interchangeable. Picking the
wrong one is the most common integration mistake, because the names do not
say what shape the data takes.

| You want | Surface | Shape |
|---|---|---|
| Performer positions, live, into a show control system | OSC over UDP | Small typed messages, fire and forget, no delivery guarantee. [The tracking output](track.html) documents them message by message. |
| Occupied space, people as footprints, and the phones' poses, into an engine that speaks web protocols | A websocket over TCP | A connected binary stream. [The field stream](field.html) documents it message by message. |
| Roster, settings, health, control, anything a person would press | HTTP | Request and response, from a browser or a script |
| A picture of the cloud, for a video-native system | Video over IP | An image of the data rather than the data itself. |
| The point values themselves | **Not an integration surface** | They live inside TouchDesigner. Wire from the project's own outputs. |

Read the last two rows twice. A video stream of the cloud is an image and is
only ever an image. A video codec throws away detail the eye will not miss,
and a depth value is not a pixel. There is no supported way to subscribe to
the point values from outside. The reasons are in
[Ports and topology](ports.html) under what must never carry depth.

## Two rules that will save you a day

**Everything carrying stage data is UDP.** It is not configurable, there is
no TCP mode, and a name containing "tcp" is not evidence of one. Check the
socket, not the label.

**Nothing in this system guarantees delivery of a frame.** That is
deliberate. Write your integration to expect gaps rather than to flag them as
faults. A missing frame means the next one superseded it, which is the system
working correctly.
