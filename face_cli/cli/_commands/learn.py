"""``face-cli learn`` — the learnability affordance.

Prints a structured self-teaching prompt. Must satisfy the agent-first rubric:
>=200 chars and mention purpose, command map, exit codes, --json, and explain.
"""

from __future__ import annotations

import argparse

from face_cli import __version__
from face_cli.cli._output import emit_result

_TEXT = """\
face-cli — a browser-rendered face that reads 3D on a 2D screen and looks
anywhere.

Purpose
-------
The expressive *output* side of a face: a simulated face rendered in a browser
that appears three-dimensional on a flat screen and can point its gaze in any
direction, drivable by an agent. Its sibling face-recognition-cli is the
perceptual *input* side; this tool does no recognition.

Status: scaffold. No renderer, no gaze primitive, and no render verbs exist
yet — the commands below are the introspection surface only. See the build
brief at https://github.com/agentculture/face-cli/issues/1.

Commands
--------
  face-cli whoami             Identity from culture.yaml.
  face-cli learn              This self-teaching prompt.
  face-cli explain <path>...  Markdown docs for any noun/verb path.
  face-cli overview           Descriptive snapshot of the agent.
  face-cli doctor             Check the agent-identity invariants.
  face-cli cli overview       Describe the CLI surface itself.

Machine-readable output
-----------------------
Every command supports --json. Errors in JSON mode emit
{"code", "message", "remediation"} to stderr. Stdout and stderr never mix.

Exit-code policy
----------------
  0 success
  1 user-input error (bad flag, bad path, missing arg)
  2 environment / setup error
  3+ reserved

More detail
-----------
  face-cli explain face-cli
"""


def _as_json_payload() -> dict[str, object]:
    return {
        "tool": "face-cli",
        "version": __version__,
        "purpose": (
            "Browser-rendered face that reads 3D on a 2D screen and looks in any "
            "direction. Scaffold: no render verbs yet."
        ),
        "commands": [
            {"path": ["whoami"], "summary": "Identity probe from culture.yaml."},
            {"path": ["learn"], "summary": "Self-teaching prompt."},
            {"path": ["explain"], "summary": "Markdown docs by path."},
            {"path": ["overview"], "summary": "Descriptive snapshot of the agent."},
            {"path": ["doctor"], "summary": "Check the agent-identity invariants."},
            {"path": ["cli", "overview"], "summary": "Describe the CLI surface."},
        ],
        "exit_codes": {
            "0": "success",
            "1": "user-input error",
            "2": "environment/setup error",
        },
        "json_support": True,
        "explain_pointer": "face-cli explain <path>",
    }


def cmd_learn(args: argparse.Namespace) -> int:
    if getattr(args, "json", False):
        emit_result(_as_json_payload(), json_mode=True)
    else:
        emit_result(_TEXT, json_mode=False)
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "learn",
        help="Print a structured self-teaching prompt for agent consumers.",
    )
    p.add_argument("--json", action="store_true", help="Emit structured JSON.")
    p.set_defaults(func=cmd_learn)
