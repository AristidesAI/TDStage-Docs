---
title: Maintenance
parent: TouchDesigner
nav_order: 7
---

# Maintenance

The hub is a binary file edited live. That makes two things essential: a
versioning discipline so you can always get back, and a check that the code
inside the file is the code the repository thinks it is.

## The loop

Every change to the component goes round this. It is four steps and one check,
and skipping the check is how the repository and the binary drift apart
without anything saying so.

```mermaid
flowchart TD
  ED["Edit the tox<br/>live in TouchDesigner"]
  LS["ls TD/*.tox<br/>read the highest number off disk"]
  CL["Clear runtime state<br/>Udpactive off, unstore pcstate,<br/>cook merged, prune sim rows,<br/>clear the log"]
  SV["Save vNN AND re-save<br/>the working copy"]
  SZ{"File size<br/>about 145 KB?"}
  DR["python3 TD/newtox/tox_drift.py"]
  R0{"What does it say?"}
  OK["0 differ, 0 tox-only.<br/>The repository IS the tox's code"]
  D1["N differ: decide which side is<br/>right, load or copy, save again"]
  D2["DATs with text and no repo copy:<br/>code that exists only in<br/>the binary. Copy it out"]

  ED --> LS
  LS --> CL
  CL --> SV
  SV --> SZ
  SZ -- "much larger" --> CL
  SZ -- "yes" --> DR
  DR --> R0
  R0 --> OK
  R0 --> D1
  R0 --> D2
  D1 --> SV
  D2 --> SV
```

### Why it is a binary edited by hand

There is a generator, `TD/newtox/build_tox.py`, and the component it was meant
to produce was never finished. What exists is a component edited live in
TouchDesigner, which is the normal way to work in TouchDesigner and is not
going to change.

So the artefact is a binary. Git can store it but cannot tell you what changed
inside it. The numbered snapshots are the only usable history, because you can
open a snapshot but you cannot read a diff of two snapshots. That is why the
discipline below exists, and why the **code** inside the component is also kept
as plain text in the repository, where you can diff and review it like anything
else.

`tox_drift.py` keeps the two copies honest. Without it, nobody knows whether
the repository matches what is in the binary.

## The versioning rule

**Every change to the tox is saved as the next numbered version, and the
working copy is re-saved.**

```
TD/TDStageConductor.tox         <- the working copy, always the latest
TD/TDStageConductor_v01.tox     <- history
...
TD/TDStageConductor_v87.tox     <- the highest number at the time of writing
```

List the directory before picking a number:

```
ls TD/*.tox
```

Do not trust a session note, a changelog line or your memory for the current
number. A number has been re-used because someone trusted a note that said
"now v36" while v37, v38 and v39 already existed on disk.

The Python modules and GLSL shaders under `TD/newtox/` are plain text and
tracked in git. They need no numbered versioning. The tox does, because a diff
of a binary tells you nothing.

## Clear runtime state before you save

A Script operator saves its last output into the tox. Component storage saves
too. So a save taken while streaming bakes a live point cloud and a live device
list into the file.

The symptom is file size. A clean working copy is around 145 KB (146,758 bytes
at v87; it was 130 KB at v66 and grows slowly as the component does). One that
baked `pcstate` reached 1 MB; one that baked the merged Script CHOP's cloud
reached 340 KB.

The size is the lesser problem. A baked `pcstate` comes back on the next load
with timestamps from the previous session. `absTime` restarts at zero, so those
devices read as newer than now, stay LIVE for ever, and show a frozen cloud
that never updates. This happened on 2026-09-04. The hub now clears `pcstate`
in `udp_pc_exec.onStart`, which logs `pcstate cleared on start (fresh
session)`, so the frozen-ghost case is handled on load. The file is still
bloated, and the save is still wrong.

### Clean save with a phone or a sim streaming

Do this in separate steps rather than one script. Module and callback reloads in
TouchDesigner are lazy, so a single script that changes something and then
depends on the change sees the old state.

1. Set `Udpactive` to 0. Stop here and let a frame pass.
2. Then, in the next step:
   - `parent().unstore('pcstate')`, plus any test keys you added
   - `op('merged').cook(force=True)`, so the Script CHOP's saved output is the
     empty one and not a baked cloud
   - prune rows with id 100 or above from `registration`, which are sims
   - `logtable.clear(keepFirstRow=True)`
   - save the numbered snapshot and the working copy
3. Set `Udpactive` back to 1.
4. Check the file size.

## Check the saved tox against the repository: `tox_drift.py`

The tox carries its scripts and shaders as DAT text. The repository keeps the
same text under `TD/newtox/`, in `tox_dats/` and in the shared modules. An edit
made live in TouchDesigner and never copied back, or a repository edit never
loaded into TouchDesigner, leaves one of them wrong, and nothing says so.

`tox_drift.py` expands a saved tox with TouchDesigner's own `toeexpand`, which
needs no running TouchDesigner, decodes every DAT's text, and compares it byte
for byte with the repository file of the same name.

```
python3 TD/newtox/tox_drift.py                            # the working copy
python3 TD/newtox/tox_drift.py TD/TDStageConductor_v87.tox
python3 TD/newtox/tox_drift.py --diff                     # print the differing lines
python3 TD/newtox/tox_drift.py --extract /tmp/v87-dats    # every DAT's text as files
```

Run it after every numbered save. The result you want is **0 differ and 0 in
the tox only**, which means the repository is the tox's code.

`--extract` doubles as a backup. It writes the tox's code out as
plain text files, readable and diffable without TouchDesigner.

On current TouchDesigner, `toeexpand` exits 1 even when it worked. The tool
judges it by its output rather than its exit code, so do not be alarmed by
that.

Give `--extract` a path **outside** the repository, or its text files show up
as untracked files that look like someone's work in progress. The tool itself
expands a copy of the tox in a temporary directory and removes it, so it leaves
nothing beside the tox. Running `toeexpand` by hand in `TD/` does: it writes a
`.tox.dir` folder and a `.tox.toc` beside the file, and left there those show
up as untracked too.

### A worked example

Run on 2026-10-27 against the working copy:

```
TD/TDStageConductor.tox: 32 DATs with a repo copy identical, 1 differ,
                         0 DATs with text and no repo copy
  DIFFERS  TDStageConductor/tdp4_receiver vs TD/newtox/tdp4_receiver.py (53 lines)
```

The repository's receiver was ahead of the tox's copy by one commit, so the
fix was to load the repository file into the DAT rather than copy the DAT back.
The tool cannot tell you which direction is right; it only tells you that you
have to decide.

That decision is the value of running it. The missing commit was the device-id
collision naming. With two phones sharing an id, the console would have warned
and TouchDesigner would have said nothing, and nobody would have known why the
two disagreed.

Loading the repository file and saving produced v77 and then v78, and the same
command now reads:

```
TD/TDStageConductor.tox: 33 DATs with a repo copy identical, 0 differ,
                         0 DATs with text and no repo copy
```

That is what a clean result looks like.

### Where it stands today

Run against the working copy on 9 November 2026:

```
TD/TDStageConductor.tox: 28 DATs with a repo copy identical, 5 differ,
                         0 DATs with text and no repo copy
  DIFFERS  TDStageConductor/clib         vs TD/newtox/tox_dats/clib.py (38 lines)
  DIFFERS  TDStageConductor/hands_lib    vs TD/newtox/tox_dats/hands_lib.py (80 lines)
  DIFFERS  TDStageConductor/hlib         vs TD/hlib.py (61 lines)
  DIFFERS  TDStageConductor/hlib_grid    vs TD/newtox/hlib_grid.py (10 lines)
  DIFFERS  TDStageConductor/udp_pc_exec  vs TD/newtox/tox_dats/udp_pc_exec.py (10 lines)
```

**So the repository is not the tox's code at the moment, and this is the
direction that matters: every one of the five is a fix that exists in the
repository and has not been loaded into the tox.** None of them is a live edit
that would be lost.

| DAT | The fix waiting in the repository |
|---|---|
| `clib` | The Windows UDP connection-reset switch, which never actually ran |
| `hands_lib`, `udp_pc_exec` | The no-proxy hand poll, `parse_hands`, the sources in `Handsstatus`, a YOLO wrist with no pixel skipped, the bridge file named in the log |
| `hlib`, `hlib_grid` | A fused person id voted rather than averaged ([#51](https://github.com/AristidesAI/TDStage/issues/51)) |

Loading those five and saving the next numbered tox is what clears it. Until
then, a result of 5 differ is the expected one and does not mean something has
gone wrong. But the Windows fix in `clib` is only in the tox once that is
done, and the show machine is where that one counts.

### Hot-swapping a module DAT in a running tox

Module reload is lazy. After setting `dat.text`, `dat.module` still returns the
old module object in the same script; a frame later it is the new one. For the
receiver, which owns a thread and a socket, that matters: stopping and swapping
in different frames lets the arming callback re-arm the **old** module on the
port, and the new one then fails to bind on every frame afterwards.

Do it in three separate steps:

1. Set `Udpactive` off, call `stop_receiver()` on the **old** module, and check
   no receiver thread remains. Then set the text, opening the source file with
   `encoding='utf-8'`. TouchDesigner's Python defaults to ASCII on this rig and
   chokes on any file with a non-ASCII character in it, an em dash for one.
2. Next step: confirm the new module is loaded, and that the receiver singleton
   is `None`.
3. Next step: set `Udpactive` on.

### After editing a callback's text

An execute DAT or parameter-execute DAT whose `.text` you set does not
re-register its callbacks. The old behaviour keeps running: tables stop
updating, pulses do nothing. Toggle `par.active` off, cook, on, cook. Do this
after every scripted callback-text edit.

## Where learned state lives

Learned numpy state is large, and component storage is the wrong place for it.
It lives on disk as numpy checkpoints, and a module reloads it lazily when it
recompiles. The learned background and floor grids are stored compressed, in
one file; the level state is not.

| Platform | Directory |
|---|---|
| macOS | `~/Library/Application Support/TDStage-TD/` |
| Windows | `%LOCALAPPDATA%\TDStage-TD\` |

| File | What it holds | Written by |
|---|---|---|
| `learned_bg.npz` | The learned background and floor grids, the thing `Segmode` = `learned` subtracts | A `Learnbg` pass |
| `stage_level_state.npz` | The solved stage level and lens unwarp | A level or unwarp solve |

Two consequences follow.

**Back this directory up before testing in learned mode.** A learn overwrites
the background, and a learn run against a simulator throws away a real one.

**A fresh machine starts with no learned state.** Dropping the tox on a new
show machine gets you the cloud and the geometry, not the learned background or
the level solve. Both have to be re-run on site, and they have to be re-run
with the stage empty and the rig in its final position.

The learned background also depends on the rig not moving. Move a phone and the
learned background for that phone is wrong.

## What does not get versioned, and why

| Thing | Where it lives | Why |
|---|---|---|
| Tox | `TD/TDStageConductor*.tox` | Binary, numbered snapshots |
| Python modules and shaders | `TD/newtox/`, `TD/newtox/tox_dats/`, `TD/newtox/glsl/` | Plain text, git tracks them, `tox_drift.py` keeps them honest against the tox |
| Learned state | Application support directory | Site-specific and re-derivable. Never commit it. |
| Device roster and markers | The web console's own configuration | The console owns them, with its own rotating backups |
| Runtime tables and storage | Nowhere, by design | Cleared before every save |

## Snapshot everything before risky work

```
./Tools/backup_state.sh [destination]
```

Writes a snapshot to `~/TDStage-Backups/<time>/` containing:

- both repositories as **verified** git bundles, which clone with no network
- uncommitted work as a binary-safe patch (`git diff --binary --full-index`,
  so a modified tox restores rather than arriving corrupt)
- an archive of untracked files, which a patch alone would miss
- the console configuration with its rotating backups, the profiles and the log
- the working tox and the newest numbered one
- the TouchDesigner learned state from the platform's application-support
  folder, with a warning when that folder is empty
- a manifest carrying a checksum for every file and the restore steps

Restoring means cloning the bundle, applying the patch if there is one, and
extracting the untracked archive if there is one. **Verified on macOS against
a dirty tree.**

{: .warning }
On the Windows show machine this needs Git Bash. The repository pins shell
scripts to LF line endings in `.gitattributes` (2026-10-27), so a default Git
for Windows checkout keeps the script runnable. A checkout made before that
pin has CRLF endings and the script dies on its first `set` line: run
`git add --renormalize .` once in it.

Run it before anything you might want to undo.

## Rules that hold inside the tox

Each rule is here because breaking it caused a specific failure.

- **Never write to a table per frame on the hot path.** Ingest, merge, cleanup,
  fusion and output use storage dictionaries.
- **Learned state goes to disk, never into component storage.**
- **Control output uses a raw UDP socket**, not an OSC Out DAT. An OSC Out DAT
  cannot be re-bound inside a pulse callback: setting its address and port then
  sending needs a cook, which is not allowed mid-callback, so it silently sends
  to the old target or nowhere.
- **Gate periodic work on `absTime.seconds`, not on `frame % N`.** Frames are
  skipped under load, so a modulus gate lands erratically or never. This froze
  the health line (tox v42), and then the status table with its device
  auto-registration, the hands poller re-arm and autoframe the same way, until
  each was time-gated.
- **A Script operator whose `onCook` reads only Python dictionaries gets no
  cook dependency.** TouchDesigner marks it clean and the output silently goes
  stale. Read a channel from a per-frame-cooking CHOP inside `onCook` to create
  the dependency. The hub uses `cook_clock` for this.
- **Never add a TouchDesigner import to `hlib.py` or `hlib_grid.py`.** They are
  pure numpy and OpenCV so the same files run inside the tox and in the offline
  tests.
- **Worker threads touch numpy and plain module dictionaries only.** No
  TouchDesigner API calls from a thread.
- **Never load a native extension such as a Python Objective-C bridge into
  TouchDesigner's process.**

## Changing the wire format

TDP4 is implemented in four places plus its specification. All five move
together or the rig breaks in a way that looks like a network fault.

| Role | File |
|---|---|
| Phone packer | `TDStage/Net/PointCloudUDPStreamer.swift` |
| Hub parser | `TD/newtox/tdp4_receiver.py` |
| Simulator | `TD/newtox/tdp4_sim.py` |
| Bench | `TD/newtox/tdp4_bench.py`, which imports the parser and never reimplements it |
| Specification | `docs/superpowers/specs/2026-07-18-tdp4-udp-depth-transport.md`, authoritative |

Then run `python3 TD/newtox/tdp4_bench.py --selftest`, and reload the receiver
into the tox and re-check with `tox_drift.py`.

Shader constants have the same rule in miniature: a shader and its numpy
reference change together, and `python3 TD/newtox/glsl_parity_test.py` fails if
they do not.
