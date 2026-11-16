---
title: Props and inertial nodes
parent: Reference
nav_order: 8
---

# Props and inertial nodes

{: .no_toc }

A prop is an object on stage with its own inertial sensor: a wheel or a staff,
something the phones cannot track as a body. The console has a path for them.
This page says what that path is, how far it has been proven, and how a
client's own inertial nodes would reach it. Read the levels in the tables
first: **no prop, board or node exists, and nothing on this page has run
against one.**

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## What exists, and at what level

| Part | State | Level |
|---|---|---|
| The wire, TPRP v1 | Specified, packed and parsed in Python and in a host C++ test, the two cross-checked | Simulated |
| ESP32 firmware | Written for an ESP32-S3 with a BNO085, ICM-42688-P or MPU-6050. Never compiled for the board (no toolchain on the dev Mac), never run. No board or sensor has been bought | Designed |
| Console module, `WebConsole/props.py` | Receiver, clock master, control messages, `/api/props`, one Rig health row per prop, `/track/prop`, a relay to TouchDesigner. Off by default. Its self-test runs over real loopback UDP, and a scratch console has run it end to end with simulated props | Simulated |
| TouchDesigner receiver | In the tox since v95 (16 November 2026) as `props_receiver` with its two DATs, switched off (`Propsactive`). The DAT code has run outside TouchDesigner against stand-ins (`props_td_test.py`, 13 checks); inside TouchDesigner it has received nothing, simulated or real | Designed |
| Radio on a stage, battery life, heading drift, real latency | Not measured | Unknown |

The levels are the project's usual four: measured, simulated (synthetic devices,
no hardware), designed (code or a calculation exists, never run on the thing it
is for), unknown (nobody has measured it).

## The wire, TPRP v1

UDP, little-endian, one message per datagram. The authoritative layout is the
docstring of `TD/newtox/props_receiver.py`; the firmware's copy is
`firmware/esp32-prop-imu/prop_wire.h`, and the two must be changed together
(the firmware's `test/run.sh` cross-checks them). Every message starts with 8
bytes: the magic `TPRP`, a version byte (1), a type byte, and the prop id as a
u16.

| Type | Direction | Carries |
|---|---|---|
| 1 DATA | prop to host | A 40-byte header (boot id, packet and sample counters, the device clock of the first sample, the sample count, which fields are present, status bits, battery, RSSI, tare counter, nominal rate, accuracy), then up to 32 samples of 44 bytes: the sample's own time offset from that clock, quaternion, angular rate, acceleration |
| 2 PING | host to prop | A ping id and the host's time, for the clock |
| 3 PONG | prop to host | The ping echoed with the device's receive and send times, and the boot id |
| 4 HELLO | prop to host, every 2 s | Boot id, device time, and a JSON block: name, firmware, sensor, rate, batch, forward axis, tare yaw, MAC, IP, RSSI, free heap, counters, and two flags (a second destination set; the id derived from the MAC) |
| 5 CTL | host to prop | A command with two arguments: tare, untare, identify, rate, reboot, LED |
| 6 ACK | prop to host | The command id and command echoed back with a result: ok, refused, or unknown |

The same parser runs in the console and in the tox, so the two cannot read a
byte differently. The console is the clock master and pings each prop; TD runs
a one-way clock from arrival times alone. The console can also relay the
props' DATA and HELLO datagrams to TouchDesigner unchanged, for props that send
to the console only; it relays a packet once, never a duplicate, and refuses a
relay back to its own port.

Ports: 9020 props to the console, 9021 props to TouchDesigner (sent direct, or
relayed by the console), 9022 the prop's own socket for what the host sends
back. All three are listed on [Ports and topology](ports.html). If 9020 is taken
on the show machine, the console's `--props-port` flag moves its listener; the
flag is in the table on [Running the console](../console/running.html).

## What a receiver would get

When the console's props module is on and `/track` output is on, each bound
prop appears on the tracking output as

```
/track/prop  id(i) x(f) y(f) z(f) yaw(f) vx(f) vy(f) vz(f) confidence(f)
```

in the same OSC bundle as the frame's performers and hands, after the hands.
The orientation comes from the prop's own sensor; the position comes from what
the operator has bound the prop to in `/api/props`: a fixed spot on the stage,
a performer, or a performer's hand. A prop bound to nothing reports nothing.
`yaw` follows the same z sign as the rest of the bundle.

One thing keeps this off a client's bus today: the props module is off until
its own configuration file, kept beside the console's, says
`{"enabled": true}`, or an operator posts that to `/api/props`. Once it is on,
`/track/prop` rides the bundle. A second switch exists in the settings schema,
`output.emitProps`, off and locked, with the note that the client has not
defined props in the contract, prop yaw is undefined there, and their bus
shares one smoothing filter across all props. Nothing reads it yet; it records
a decision and gates nothing. The message above is what the code emits. The
client has agreed to none of it.

## Inertial nodes from a client

Default Ltd described, on 16 November 2026, inertial nodes of their own:
nRF52840 boards on SlimeVR's Enhanced ShockBurst radio, publishing an "objects
stream" with, per node, an id, a quaternion, an angular rate and a timestamp.
The stream's format is not agreed. Nobody on this side has seen a node.

The design note for taking that stream (`Notes/Props-ESB-Adapter-Design-2026-11-17.md`
in the system repository) recommends a small separate process: a stdlib
adapter that reads the objects stream (over UDP, if that is what the client
sends; the first open question below) and sends TPRP v1 to the console's props
port. Towards the console and TouchDesigner each node then looks like one prop,
and the wire, the receiver, the tox and the ports stay as they are. The console
module needs no required change; the note lists four optional ones (Rig health
wording and the RSSI threshold, both written for Wi-Fi props; a radio-loss
warning; naming the two hardware ids in a conflict row). The adapter is
**designed only, not written**.

What the adapter would do, in short:

- Map each node id to a prop id from a configuration table, so a prop id
  survives swapping a node. If the nodes have a stable hardware id (an open
  question), carry it in HELLO so the conflict row in `/api/props` and Rig
  health can name the two nodes configured onto one id; the conflict itself is
  flagged by their alternating boot ids either way.
- Stand in for the device clock. The console cannot ping a node, so the adapter
  answers every PING from its own clock and maps the node's timestamps onto it;
  the console's two-way clock then measures only the adapter-to-console link.
- Apply the tare on the node's stream the way the firmware applies it on a
  prop: store the heading at the tare, turn every later quaternion by its
  negative, refuse within 25 degrees of vertical.
- Default to the batching the firmware was written for, 200 Hz in packets of
  four samples. Each extra sample in a packet adds one sample period of latency
  (four samples cost 15 ms at 200 Hz). The console's throughput at one sample
  per packet with eight or more props is unknown.

Six questions decide the stream's format, and Default Ltd have to answer them
before anyone can write the adapter:

- Transport and framing: UDP or not; one datagram per sample or per tick;
  binary, OSC or JSON.
- Identity: whether the node id survives power cycles and a second dongle, and
  whether a hardware id exists.
- Time: whose clock the timestamp is on, its unit, whether it wraps, whether
  the node's clock restarts at power-on, and whether a per-node counter lets
  radio loss be counted.
- Quaternion: component order, frame, handedness, whether a magnetometer is
  used (on a stage it should not be), and whether anything in the client's
  software re-zeroes the heading under the tare.
- Angular rate: unit and frame.
- Downlink: whether anything can be sent back to a node.

SlimeVR's own published firmware notes, unverified, describe receiver reports
with a one-byte tracker id and no timestamp, sequence number or gyro. A
per-node timestamp and angular rate as described would therefore come from
Default Ltd's own firmware or software. That makes the clock question the
first one.

## What is not known

Radio range on a stage, battery life, the sensor's heading drift and the
latency from a node or a prop to the console are unknown: there is no
measurement because there is no hardware. The bench plan that would settle
them for an ESP32 prop is section 14 of `Notes/Props-IMU-Integration.md`, and
it needs a board in a room. For a node there is no plan yet beyond the same
list of unknowns; the stream's format has to be agreed first.

## See also

- [The tracking output](track.html) for the bundle `/track/prop` rides in, and
  for what an id promises
- [Ports and topology](ports.html) for 9020, 9021 and 9022 beside everything
  else that listens
- [How far each part is proven](status.html) for the props row with its
  evidence, generated from the system repository's own status table
- [Parameters](../td/parameters.html#props) for the Props page the tox has
  carried since v95 (`Propsactive`, `Propsport`, `Propsdelayms`,
  `Propstareyaw`, `Propsstatus`)
