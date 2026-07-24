"""Markdown catalog for ``face-cli explain <path>``.

Each entry is verbatim markdown. Keys are command-path tuples. The empty tuple
and ``("face-cli",)`` both resolve to the root entry.

Keep bodies self-contained: an agent reading one entry should get enough
context without chaining reads.
"""

from __future__ import annotations

_ROOT = """\
# face-cli

The expressive *output* side of a face: a simulated face rendered in a browser
that appears three-dimensional on a flat 2D screen and can look in any
direction, drivable by an agent. The sibling `face-recognition-cli` is the
perceptual *input* side — this tool does no recognition.

**Status: scaffold.** There is no renderer, no gaze primitive, and no render
verbs on disk yet; what follows is the introspection surface. The build brief
is <https://github.com/agentculture/face-cli/issues/1>.

## Verbs

- `face-cli whoami` — identity probe from `culture.yaml`.
- `face-cli learn` — structured self-teaching prompt.
- `face-cli explain <path>` — markdown docs for any noun/verb.
- `face-cli overview` — descriptive snapshot of the agent.
- `face-cli doctor` — check the agent-identity invariants.
- `face-cli cli overview` — describe the CLI surface.

## Exit-code policy

- `0` success
- `1` user-input error
- `2` environment / setup error
- `3+` reserved

## See also

- `face-cli explain whoami`
- `face-cli explain doctor`
"""

_WHOAMI = """\
# face-cli whoami

Reports the agent's identity from `culture.yaml`: nick (`suffix`), backend,
served model, and the package version. Read-only.

## Usage

    face-cli whoami
    face-cli whoami --json
"""

_LEARN = """\
# face-cli learn

Prints a structured self-teaching prompt covering purpose, command map,
exit-code policy, `--json` support, and the `explain` pointer.

## Usage

    face-cli learn
    face-cli learn --json
"""

_EXPLAIN = """\
# face-cli explain <path>

Prints markdown documentation for any noun/verb path. Unlike `--help` (terse,
positional), `explain` is global and addressable by path.

## Usage

    face-cli explain face-cli
    face-cli explain whoami
    face-cli explain --json <path>
"""

_OVERVIEW = """\
# face-cli overview

Read-only descriptive snapshot of the agent: identity (from `culture.yaml`), the
verb surface, and the sibling-pattern artifacts this repo carries. Accepts an
ignored `target` so a stray path never hard-fails.

## Usage

    face-cli overview
    face-cli overview --json
"""

_DOCTOR = """\
# face-cli doctor

Checks the agent-identity invariants `steward doctor` verifies:
prompt-file-present and backend-consistency (`colleague` → `AGENTS.colleague.md`), plus a
skills-present check. Exits 1 when unhealthy.

## Usage

    face-cli doctor
    face-cli doctor --json
"""

_CLI = """\
# face-cli cli

Noun group for CLI-surface introspection. `cli overview` describes the CLI
itself (distinct from the global `overview`, which describes the agent).

## Usage

    face-cli cli overview
    face-cli cli overview --json
"""


ENTRIES: dict[tuple[str, ...], str] = {
    (): _ROOT,
    ("face-cli",): _ROOT,
    ("face",): _ROOT,
    ("whoami",): _WHOAMI,
    ("learn",): _LEARN,
    ("explain",): _EXPLAIN,
    ("overview",): _OVERVIEW,
    ("doctor",): _DOCTOR,
    ("cli",): _CLI,
    ("cli", "overview"): _CLI,
}
