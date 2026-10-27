---
title: Reference
nav_order: 6
has_children: true
---

# Reference

Ports, wire formats, HTTP and OSC surfaces, and the reasoning behind the
design. Written for someone integrating another system, not for someone
operating this one.

If you are at a venue with a rig that will not work, you are in the wrong
section. Go to [Operations](../operations/).

## What is in here

| Page | Answers |
|---|---|
| [The tracking output](track.html) | **Start here if you are writing the receiver.** Every message and argument, the coordinate frame, what an id promises, and the guarantees made and not made. |
| [Ports and topology](ports.html) | What listens where, which surface is UDP and which is not, and what must never carry depth. |
| [Why it is built this way](design.html) | The decisions that look arbitrary from outside: UDP with no TCP option, depth on the wire instead of points, dumb phones, receiver-side separation, and the one limit that must never be claimed away. |
| [Dependencies and requirements](dependencies.html) | What each side needs to run, where it is declared, and what breaks without it |

## What you are integrating against

Three surfaces, and they are not interchangeable. Picking the wrong one is
the most common integration mistake, because the names do not advertise what
the shapes are.

| You want | Surface | Shape |
|---|---|---|
| Performer positions, live, into a show control system | OSC over UDP | Small typed messages, fire and forget, no delivery guarantee. Documented message by message on [The tracking output](track.html). |
| Performer positions into something that speaks web protocols | A websocket over TCP | A connected stream. The console reports how many clients are attached. |
| Roster, settings, health, control, anything a person would press | HTTP | Request and response, from a browser or a script |
| A picture of the cloud, for a video-native system | Video over IP | An image. A picture of the data, not the data. |
| The point values themselves | **Not an integration surface** | They live inside TouchDesigner. Wire from the project's own outputs. |

The last two rows are worth reading twice. A video stream of the cloud is an
image and is only ever an image: a video codec throws away detail the eye
will not miss, and a depth value is not a pixel. There is no supported way to
subscribe to the point values from outside. The reasons are in
[Ports and topology](ports.html) under what must never carry depth.

## Two rules that will save you a day

**Everything carrying stage data is UDP.** It is not configurable, there is
no TCP mode, and a name containing "tcp" is not evidence of one. Check the
socket, not the label.

**Nothing in this system guarantees delivery of a frame.** That is a design
decision, not an oversight, and your integration should be written to expect
gaps rather than to detect them as faults. A missing frame means the next one
superseded it, which is the system working correctly.
