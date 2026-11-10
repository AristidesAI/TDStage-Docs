---
title: When the show machine dies
parent: Operations
nav_order: 7
---

# When the show machine dies

The show machine runs the bridge, TouchDesigner and the console together, so
when it goes, every output goes at once. This page is the second machine and
the restore that puts the show back on it.

{: .warning }
> **Scope.** The restore was rehearsed for real on a Mac on 9 November 2026,
> beside a live demo, and the times below come from that. **Nothing here has
> run on Windows, on the show PC, or on a rig.** Treat the switchover itself as
> designed, not proven, and read the levels in each table.

This is for a machine that will not come back within a couple of minutes. A
single process crashing, or TouchDesigner crashing, is handled on the show PC
itself. [During a show](failure.html#during-a-show) covers those.

## What fails, and what covers it

| Failure | Effect | Covered by | Level |
|---|---|---|---|
| Power cut, a plug pulled, a tripped circuit | The PC and the switch go dark; the phones lose their link | A UPS on the PC **and** the switch | Designed |
| Show PC hardware or Windows dies | Everything stops: bridge, TouchDesigner, console, YOLO, and the client's content if it runs there | The standby machine | Designed |
| One process crashes | TouchDesigner and the console lose the phones for 2.1 to 2.8 s; `/track`, F1 and NDI pause for the console's 3 s restart | The launchers restart it | Simulated (bridge); designed (console) |
| TouchDesigner crashes | Visuals stop, and so does phone telemetry to the console | Reopen it on the same PC, then `doctor.bat --only temp` | Designed; a remote relaunch has never run ([#26](https://github.com/AristidesAI/TDStage/issues/26)) |
| The switch dies | No phone reaches any machine | A spare switch of the same PoE budget | Designed |

## The standby machine

**A second Windows PC is the one to want**, installed the same way as the show
PC, so the switchover is the same software on the same operating system. With
an NVIDIA GPU, YOLO runs on CUDA as it does on the show PC; without one,
`install.bat` fits the CPU build of torch and the rate has not been measured on
Windows.

**The Mac is a degraded standby.** TouchDesigner's GPU merge held 60 fps at 8,
12 and 16 simulated streams on it, but YOLO drops to 10 to 15 Hz per phone.
It starts the same processes through `Tools/show_mac.sh`.

{: .warning }
> **The standby needs a TouchDesigner licence of its own.** A Non-Commercial
> licence caps images at 1280 × 1280, and the depth atlas is **1351 rows at
> seven phones and 1544 at eight**. A standby with the free licence does not
> fall back gracefully; it cannot carry the rig at all.

Prepare it once, at home, with internet. Keep it off the show network until it
is needed, holding the show PC's static address ready rather than live, and
refresh it from the newest snapshot after any change to the roster, the
markers, the alignment or the console's settings.

## Taking a snapshot

```bash
./Tools/backup_state.sh            # ~/TDStage-Backups/<date-time>/
```

Run it from the checkout, in Terminal on a Mac or Git Bash on Windows. Measured at
**2.5 to 2.6 s for 423 MB**, three runs at the lowest CPU priority beside a
live console, and it is read-only against the checkout it reads.

| In the snapshot | What |
|---|---|
| `repos/<repo>.bundle` | Every branch and tag of both repositories; clones with no network |
| `repos/<repo>.uncommitted.patch` | The working tree against HEAD, binaries included: a modified tox, a `.toe` |
| `repos/<repo>.untracked.tgz` | Files git neither tracks nor ignores. A nested clone is kept; linked worktrees are left out and listed |
| `console/config.json`, `config-backups/`, `profiles/` | The roster, markers, settings and targets; the console's own last 50 saves; each phone's stored profile |
| `td/*.tox` | The working tox and the newest numbered one |
| `td/learned/*.npz` | TouchDesigner's learned background and floor |
| `restore_state.sh` | The restore below, copied into every snapshot |
| `MANIFEST.txt` | Branch, commit and origin per repository, a sha256 per file, and the restore lines |

The console's log is in the snapshot as evidence and is deliberately not
restored.

## Restoring it

The snapshot carries its own restore script, so a restore needs **neither a
checkout nor a network**.

```bash
bash /Volumes/USB/<date-time>/restore_state.sh ~/Show     # Mac
bash /e/<date-time>/restore_state.sh /c/Show              # Windows, in Git Bash
```

The folder you name is the one that **holds** the checkouts, never a checkout
itself: it receives `TDStage/` and `TDStageARKit/` side by side. A folder inside
a git checkout, or one holding `WebConsole/`, is refused.

- **No `TDStage` there: a fresh restore.** Each repository is cloned from its
  bundle on the branch the MANIFEST names and checked against its commit, with
  its origin set to GitHub rather than to the snapshot. Then the uncommitted
  patch, **then** the untracked files in that order, then the console's
  `config.json`, `backups/` and `profiles/`, the tox files, and
  TouchDesigner's learned state, creating its folder if it has never run.
- **`TDStage` already there: a refresh**, allowed only for a checkout this
  script made, and refused for the checkout the snapshot came from or while a
  console is running from it.
- It stops at the first step that fails and names it, and the patch and the tar
  are both verified **before any file changes**, so a damaged snapshot leaves
  the folder as it was.
- It writes nothing outside that folder except TouchDesigner's learned-state
  folder.

A restore that stopped part way is simply run again into the same folder: it
becomes a refresh, which clears what the first run left.

## The switchover

1. **Take the show PC off the network.** Pull its cable or switch it off. It
   must not still hold the show address.
2. **Plug the standby into the show switch.**
3. **Start the stack**: `WebConsole\windows\show.bat`, or `Tools/show_mac.sh`.
4. **Open TouchDesigner from the same account and session** as the launcher,
   and load the tox, setting `Udpport` 9004, `Udpactive` on, Console Link
   Active on and the GPU merge path on. The saved tox has `Udpactive` and the
   console link **off**, and the next step needs that link.
5. **Check the link.** On link-up the console sends the poses of the phones
   that were checked when the snapshot was taken. Unchecked phones stay
   unchecked and their poses are held, and the Dashboard names them in a
   warning. Press **Push poses** if that warning is there, or if the
   registration does not match the roster.
6. **The phones need no change.** They keep sending to the same address.
   Telemetry reaches the console through TouchDesigner, so it appears once
   TouchDesigner is up.
7. **Client outputs** come back in the state the console last saved. Whether
   the client's own software reconnects by itself is unknown.
8. **Run `doctor.bat`** with everything up: no FAIL in Firewall, Bridge file
   and TEMP, or Power and Windows Update.

{: .warning }
> **Never over Remote Desktop.** On Windows, drive the standby at the machine,
> or from a tool that shares its console session. An RDP session can have its
> own `TEMP` folder, which is where the bridge's memory-mapped file lives, so
> the bridge and TouchDesigner stop sharing one. It also takes over the
> machine's own screens.

## How long it takes

| Step | Time | Level |
|---|---|---|
| Snapshot, 423 MB | 2.5 to 2.6 s | Measured on a Mac |
| Fresh restore, both repositories and all state | 3.1 to 3.3 s | Measured on a Mac |
| Refresh of a prepared standby | 0.5 to 1.9 s | Measured on a Mac |
| Console start to `/healthz` answering | under 4.5 s, with YOLO and Apple Vision off | Measured on a Mac |
| **Decision to phones streaming into TouchDesigner** | **3 to 5 min** | **Designed** |
| A standby built from nothing | about 30 min plus downloads | Designed |
| Any of the above on Windows | | Unknown |

The seconds are measured; the minutes are not. What is missing from the
measured column is everything slow: TouchDesigner's start with the tox, YOLO
starting on CUDA, and the phones finding the new machine.

## What a switchover costs

| Lost | Why | Way back |
|---|---|---|
| Every change since the last snapshot: roster, markers, alignment, settings, profiles | A snapshot is one moment, and the show PC's own backups are on the dead machine | Snapshot after every such change |
| TouchDesigner edits not saved into the tox | The snapshot copies the file on disk | Save the tox, numbered, after every edit |
| The learned background and floor, if the standby is in another room | They belong to one room | Learn them again on the empty stage |
| Clock offsets, learned phone addresses, `/track` performer ids, consensus history, the motion background | The console holds these in memory only | Rebuilt as the phones stream. **`/track` ids start again, and the client must treat them as new** |
| Uncommitted edits inside linked worktrees | Left out of the snapshot; their commits are in the bundle | Nothing needed for a show |
| Per-machine installs: the venvs, TouchDesigner and its licence, NDI, drivers | Ignored by git, or outside the checkout | Installed once on the standby |

**The phones lose nothing.** Their settings live on the phones, and their
stored profiles come back with the console.

## What the rehearsal found

Every one of these would otherwise have been found during a real switchover.

| Found | What it would have done |
|---|---|
| `git clone` from the bundle checked out the **wrong branch** | Five branches pointed at the same commit and the bundle's HEAD names a commit, not a branch. The old restore lines, followed literally, produced a working tree from a feature branch |
| Copying the learned state failed on a machine where TouchDesigner had never run the tox | Nothing created the folder. The script now makes it |
| The console's `backups/` was never put back | The old lines had no step for it |
| The old snapshot script **rewrote the live checkout's git index** | `git status` refreshes it, and `git diff` does so too unless told otherwise. The content staged does not change, but the file is rewritten under other programs using that checkout |
| It would have packed **8.3 GB of agent worktrees** | Each linked worktree lists as one untracked folder, and the tar takes a folder whole |

After the fixes: a fresh restore compared 1,086 files against the live
checkout, and **1,083 were identical byte for byte**. The three that differed
were `.bat` files differing only in line endings.
