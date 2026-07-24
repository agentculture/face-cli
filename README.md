# face-cli

A simulated face rendered in the browser that appears three-dimensional on a
flat 2D screen and can look in any direction — an agent-drivable gaze surface
for robots, kiosks, and screens.

> **Status: scaffold.** The renderer does not exist yet. What ships today is
> the agent-first CLI baseline, the mesh identity, and CI. The face itself is
> being designed in the open — see [the build brief][brief] and
> [`CLAUDE.md`](CLAUDE.md).

[brief]: https://github.com/agentculture/face-cli/issues/1

## The idea

Two halves, and both are the interesting part: the **illusion of depth** on a
flat surface, and a **gaze that can be pointed anywhere** and reads as pointed
there. Everything else is in service of those.

`face-cli` is the *expressive output* side of a face. Its sibling
[`face-recognition-cli`](https://github.com/agentculture/face-recognition-cli)
is the *perceptual input* side — it identifies real people from camera frames.
They share a subject and nothing else.

## Decided so far

- **The render target is the browser** — a local page driven over
  canvas/WebGL/SVG. It needs no display server (so it runs on a headless robot
  box), the screen showing the face need not be the machine running the
  process, and a page can be screenshotted and diffed in CI. The *technique*
  within the browser is still open.
- **The rendered face must survive face recognition.** Not photorealism — a
  detector-passing bar: OpenCV **YuNet** should detect it above the standard
  `0.6` score threshold, and **SFace**'s 128-dim embedding should stay stable
  across the whole gaze range. That turns "it looks 3D" into an assertion CI
  can actually make, and it is the seam along which this repo composes with
  `face-recognition-cli`.

Open questions — the gaze primitive, the control channel between a one-shot CLI
call and a live page, whether expression is in scope, one face or many — are
tracked in [`CLAUDE.md`](CLAUDE.md) and [the brief][brief].

## Quickstart

```bash
uv sync
uv run pytest -n auto                 # run the test suite
uv run face whoami                    # identity from culture.yaml
uv run face learn                     # self-teaching prompt (add --json)
uv run teken cli doctor . --strict    # the agent-first rubric gate CI runs
```

The console command is **`face`**; the import package is `face_cli` and the
PyPI distribution is `face-cli`. The mismatch is deliberate — a bare `face` is
already a published distribution on PyPI, so squatting that import would shadow
it.

## CLI

| Verb | What it does |
|------|--------------|
| `whoami` | Report this agent's nick, version, backend, and model from `culture.yaml`. |
| `learn` | Print a structured self-teaching prompt. |
| `explain <path>` | Markdown docs for any noun/verb path. |
| `overview` | Read-only descriptive snapshot of the agent. |
| `doctor` | Check the agent-identity invariants (prompt-file-present, backend-consistency). |
| `cli overview` | Describe the CLI surface itself. |

Every command supports `--json`. Results go to stdout, errors/diagnostics to
stderr (never mixed). Exit codes: `0` success, `1` user error, `2` environment
error, `3+` reserved.

No gaze or render verbs exist yet — the list above is the scaffold's
introspection surface.

## What's in the box

- **An agent-first CLI** cited from [teken](https://github.com/agentculture/teken)
  (`afi-cli`) — the runtime package has no third-party dependencies.
- **A mesh identity** — `culture.yaml` (`suffix` + `backend`) and the matching
  resident prompt file (`AGENTS.colleague.md`, since this agent runs
  `backend: colleague`).
- **The canonical guildmaster skill kit** under `.claude/skills/`, vendored
  cite-don't-import. See [`docs/skill-sources.md`](docs/skill-sources.md).
- **A build + deploy baseline** — pytest, lint, the agent-first rubric gate, and
  PyPI Trusted Publishing wired into GitHub Actions.

## Contributing

Every PR bumps the version (`version-check` CI blocks merge otherwise) and adds
a real CHANGELOG entry. See [`CLAUDE.md`](CLAUDE.md) for the full conventions —
the `cicd` PR lane, worktree layout, and deploy setup.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
