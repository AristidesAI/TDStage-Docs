---
title: Your three questions of 21 October
nav_order: 8
---

# Your three questions of 21 October

Mathias, your email of 21 October with the F1 0.4 draft asked us three
questions. Our answers:

1. The console emits sparse occupancy on the 0.4 WebSocket, and the phones'
   points at a quarter density if you ask for them (*simulated*).
2. Each depth frame carries its capture time, intrinsics and transform, and a
   recording keeps all of it (*measured*). Most OSC telemetry and the NDI
   output carry no capture stamp, and the phone does not send the ARKit camera
   pose (*not built*).
3. We would keep the phones low, rigid and angled, and hang the Mid-360
   overhead. Our calibration cannot follow a swaying phone (*not built*).

Facts here come from TDStage AR, the app the phones run, and the console on
`main`, as of 10 November.

## The evidence words

| Word | Meaning |
|---|---|
| **measured** | We saw it on real iPhones, at a desk or in a room, on the date given. |
| **simulated** | The code exists and we have run it on synthetic data or in tests, with no phone involved. |
| **designed** | We have written it down. No code exists. |
| **not built** | Nothing exists yet. |

Nothing has run on a stage yet.

## 1. Fusion output

The console sends three of your channels on the 0.4 WebSocket, port 9001, at
15 frames a second by default:

- **SMSF field.** 5 cm cells over a box 12 m wide, 4 m high and 8 m deep,
  centred on the stage floor. Each occupied cell carries a weight from 0 to
  255, smoothed from frame to frame, and we send no distance grid.
  *Simulated:* our encoder passes a parity test against your `sms_td.py`.
- **SMSP presence.** Body clusters on a 10 cm floor grid, with centre, radius
  and top height, and no identity. *Simulated.*
- **SMSS sensor poses.** One fixed pose per phone, about once a second.
  *Simulated.*

A client that connects with `?points=1` also receives our own `TDMP` message:
every fourth point of the phones' clouds, float32 xyz in stage metres, with no
colour and no phone id. We made it opt-in because your decoder rejects a
message type it does not know. *Simulated.*

TouchDesigner merges its own full-density cloud on the GPU for the visuals
and keeps it. Sending it to you would be new work for us to scope.

## 2. The phones as measuring sensors

**A capture timestamp on everything.** Each depth frame carries
`captureMicros`, the `ARFrame` timestamp in microseconds on the phone's uptime
clock, which `CMDeviceMotion` shares. On 26 October we timed one hot phone
over Wi-Fi with it: 95.7 ms median from capture to arrival on the Mac, 73.5 ms
of it the phone's own capture age. *Measured*, though the clock offset below
adds its own unmeasured error. The 10 Hz OSC pose message carries
the same clock. The rest of the OSC telemetry and the NDI output carry no
capture stamp. *Not built.*

**Gyro and accelerometer while recording.** During a take the phone writes
rotation rate, user acceleration, gravity and attitude to a `.imu` file beside
the take, with float64 times on the uptime clock. The app asks Core Motion for
100 Hz and offers no higher rate. *Simulated* in unit tests.

**Intrinsics and the camera transform.** Each frame carries a 3 x 3
intrinsics matrix scaled to the depth grid and a 4 x 4 matrix with a flag
bit. With the bit set, the phone has calibrated on the floor markers and the
matrix maps camera to stage. With the bit clear, the matrix is a
gravity-levelling rotation and the console's alignment places the phone.
*Measured:* the console placed two phones from these frames in October. The
app reads the ARKit camera transform on each frame but neither sends nor
records it. *Not built.*

**Recording with all of that.** A take stores each frame as sent: capture
time, intrinsics, the matrix, float16 metric depth, ARKit confidence, colour
and the phone's unix time. A real colour take compressed 2.2 times. *Measured.*
`take_to_mcap.py` converts takes to MCAP with ROS 2 messages, `/tf` and IMU
included. *Simulated:* it passes its self-test, and we have not opened one
beside your scanner's bags.

**A point-cloud header.** The phone sends a depth grid with no xyz, and the
receiver unprojects it, so the frame header above does that job.

**Several phones.** The console pings each phone about once a second, takes a clock
offset from the fastest of the last 20 round trips, and stamps the 0.4 field
on the Mac's clock with it. The error stays within half that round trip, which
the console shows per phone. *Measured* in use; we have not checked the offset against a
reference clock.

The console merges each phone's newest frame as it arrives and does not match
frames from different phones by capture time. A take keeps the phone's own
unix clock and stores neither the console's offsets nor its alignment.

Our gyro matcher `imu_sync.py` lines up two `.imu` files to within 0.1 ms on
synthetic 100 Hz data. *Simulated.* We have not run it on real phones or a
Mid-360, and reading a Mid-360's IMU into that layout is *not built*. iOS gives
apps no PTP, as far as we know, so joining the phones to a PTP clock shared by
the Mac and a Mid-360 through these offsets stays *designed*.

The floor markers set the shared frame, with its origin at stage-floor centre,
Y up, in metres.

## 3. Sensors on an overhead frame

**Range.** From 4 to 4.5 m up, a phone sees the floor near the end of its
range. We assume a 5 m ceiling for the phone's LiDAR and plan on 4.5 m of
usable range. We have measured neither on a person nor on a floor at that
distance.

**Viewpoint.** A phone looking straight down stacks limbs onto bodies. Angled
views from several sides let our fusion separate two performers standing close.

**Moving poses.** A marker-calibrated phone solves its pose once and keeps it,
so a swaying frame would move the cloud with it. An uncalibrated phone
re-levels to gravity every 0.25 s, which corrects its tilt and leaves its
position and heading alone. Once you lock a phone's pose, the console raises
PHONE MOVED at 0.5 degrees of tilt; it displays a change of heading without an
alarm. *Simulated.*

Tracking a moving pose is *not built*. ARKit world tracking runs while the
phone captures, but the marker solve runs in a separate ARKit session, so the
two frames have no tie. We would need marker detection inside the capture
session, then a test on a swaying mount, before SMSS could carry a moving pose
with real uncertainties. We tried reading tilt from the clouds on two real
phones on 28 October. Open3D's roll answer scattered 3.4 degrees over six runs
and missed a 6 degree roll we added on purpose. *Measured.* Tilt comes from the
IMU.

**Markers.** Our default plan puts each phone's marker about 3.2 m out along
its aim line. Phones looking down would need markers moved into their
downward view, so an overhead mount changes the layout.

## For Adam

| Item | Fact | Source |
|---|---|---|
| 0.4 producer | Port 9001, 15 Hz. SMSF `<4sBBBBIdHHf3fI`, SMSP `<4sBBBBIdHHH2x`, SMSS `<4sBBBBIdHH` + 56 B rows. Cell 0.05 m, box origin (-6, 0, -4) m. Flags `?points=1`, `?presence=1`. | [f1_field.py](https://github.com/AristidesAI/TDStage/blob/main/WebConsole/f1_field.py) |
| `t` and `window` | `t` = newest capture time merged, on the Mac's clock (arrival time for a phone with no offset yet). `window` = span of capture times + 1000/30 ms. | [f1_field.py](https://github.com/AristidesAI/TDStage/blob/main/WebConsole/f1_field.py) |
| SMSS rows | Source 0, fixed. `residual_mm` = RMS scatter of the marker solve's repeated fixes, NaN if uncalibrated. Sigmas NaN. | [f1_field.py](https://github.com/AristidesAI/TDStage/blob/main/WebConsole/f1_field.py) |
| Clock offset | `/tdlidar/ctl/ping seq hostTime`; offset = device time - (send + receive)/2, best of 20. | [server.py](https://github.com/AristidesAI/TDStage/blob/main/WebConsole/server.py) |
| Depth frame | TDP4, 120 B header: `u64 captureMicros`, flags bit 0 `extrinsicValid`, `f32 intrinsics[9]`, `f32 extrinsic[16]` row-major. | [TDP4 spec](https://github.com/AristidesAI/TDStage/blob/main/docs/superpowers/specs/2026-07-18-tdp4-udp-depth-transport.md) |
| Pose OSC | `/tdlidar/<id>/device/pose tHi tLo qx qy qz qw roll pitch yaw`, 10 Hz. | TDStage AR `ShowTelemetry.swift` |
| `.imu` record | 60 B: `f64 t`, then `f32` rotation rate (rad/s), user acceleration (g), gravity (g), quaternion xyzw. | TDStage AR `TakeIMUWriter.swift` |
| Takes | `.tdp4rec` v2. | [spec](https://github.com/AristidesAI/TDStage/blob/main/docs/superpowers/specs/2026-09-06-tdp4rec-take-format-v2.md), [take_reader.py](https://github.com/AristidesAI/TDStage/blob/main/TD/newtox/take_reader.py) |
| MCAP | Phone-clock stamps; `--clock wall` uses unix time and drops the IMU. An uncalibrated phone's `/tf` is its levelling rotation. | [take_to_mcap.py](https://github.com/AristidesAI/TDStage/blob/main/TD/newtox/take_to_mcap.py) |
| Gyro matching | Cross-correlation, refined on three axes in 0.05 ms steps. | [imu_sync.py](https://github.com/AristidesAI/TDStage/blob/main/Tools/imu_sync.py) |
| NDI | No capture stamp, no metadata. | [ndi_out.py](https://github.com/AristidesAI/TDStage/blob/main/WebConsole/ndi_out.py) |

The TDStage AR sources sit in a separate private repository. Ask us for the
files.
