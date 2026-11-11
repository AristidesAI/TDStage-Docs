---
title: Phones on USB cables
parent: Operations
nav_order: 11
---

# Phones on USB cables

A phone on a USB-C cable is on a real network link, not a tunnel. There is no
`iproxy`, no Personal Hotspot and no forwarding process: UDP crosses the cable
the same way it crosses Ethernet. On a Mac the round trip measures **0.55 ms
against about 8 ms over Wi-Fi**.

{: .warning }
> **On Windows this is written from the code and has never been run against a
> phone.** The two-phone cable rig runs daily on a Mac. The Windows path exists
> and is checked by its own self-tests, which is not the same as working. Treat
> the procedure below as the thing to try and to record, not as a thing known
> to work.

## How the link comes up

A cable brings up an NCM/ECM interface at both ends. Nothing hands out
addresses on a two-host cable, so **both ends self-assign a `169.254.x.y`
address at random**, and that address can change when the cable is re-plugged.

On the phone the cable appears as an interface alongside Wi-Fi. The LIVE page's
Link picker has a **Cable** mode that pins the stream to it, and **Auto** with
Prefer Ethernet on also takes the cable, because a cable counts as wired.

## Two phones means two cables on one subnet

Every cable is `169.254.0.0/16` at both ends, so two cables into one PC give
two adapters on the same prefix. **Inbound is fine**: each phone sends to the
machine's address on its own cable.

Outbound is where it goes wrong. The machine now has two on-link routes for one
prefix and picks between them by interface metric, so a `/ctl` reply meant for
phone B can leave on cable A and never arrive. macOS avoids this by cloning a
per-host route out of its ARP cache, which is why the Mac rig works with no
routing work at all. **Windows has to be checked rather than assumed**, and
step 4 below is that check.

## The procedure

1. **Install the driver and turn the hotspot off.** The Apple Devices app
   carries the USB driver that makes a plugged-in iPhone appear as a network
   adapter; reboot once after installing. Leave **Personal Hotspot off** on
   every phone: with it on the phone becomes a router handing out
   `172.20.10.x`, and two of those on one machine do collide.
2. **Plug in one phone and confirm the adapter.** `ipconfig /all` shows a new
   adapter with an autoconfiguration address `169.254.a.b`, which is the
   machine's address on that cable. No adapter means the driver is missing or
   the phone has not been trusted; an adapter with no address usually just
   needs ten seconds.
3. **Point the phone at that address**, with Link set to Cable, then press
   **Ping all** in the console and watch for the pong. That pong is the
   machine-to-phone direction working over this cable. Repeat for the second
   phone, typing **its own cable's** address rather than the first one's.
4. **Check the routing, which is what decides whether two phones work.** With
   both online, confirm **both** pongs arrive, then on the machine:

   ```
   arp -a
   route print -4 | findstr 169.254
   ```

   Each phone's address should appear under its own adapter, and there should
   be two on-link routes with their metrics.

   **If only one phone pongs**, the control traffic for both is leaving by the
   lower-metric adapter. Pin each phone to its own cable with a persistent host
   route, as Administrator, reading the interface index from `route print`:

   ```
   route -p add <phone> mask 255.255.255.255 <machine address on that cable> if <idx>
   ```

   Re-plugging a phone can change its address and leave that route stale.
5. **Check the firewall profile.** A new Apple adapter lands in the **Public**
   profile, where inbound UDP is blocked, so the rules `firewall.bat` adds for
   the LAN profile do not apply to it. Either set that adapter to Private or
   re-run `firewall.bat` afterwards, then confirm with `doctor.py`, which lists
   the USB iPhone links it can see.

## What the console does about a cable that moves

Since 2026-11-03 the console watches every cable rather than the first one it
found. It raises a per-phone `CABLE_MOVED` when a phone's cable changes under
it, and `GET /api/rig` reports a `cables` list.

{: .note }
> **Cable tracking is keyed by interface name**, so a re-plug that renames the
> adapter reads as a different cable. On Windows the name is assigned by the
> driver and is not guaranteed stable across re-plugs, which is one more thing
> the first real run has to establish.

## What to record on the first Windows run

Worth capturing while somebody is in front of the machine with phones
attached, because none of it can be reconstructed afterwards:

- The exact adapter names the driver assigns, and whether they survive a
  re-plug.
- `ipconfig /all`, `arp -a` and `route print -4 | findstr 169.254` with both
  phones connected.
- Whether both phones pong **without** the host routes of step 4, which is the
  question the Mac cannot answer.
- The firewall profile each adapter landed in before anything was changed.
