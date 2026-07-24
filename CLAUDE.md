# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`face-cli` is the **expressive output side of a face**: a simulated face
rendered in the browser that reads as three-dimensional on a flat 2D screen and
can look in any direction — an agent-drivable gaze surface for robots, kiosks,
and screens.

**Status on disk today: scaffold only.** There is no renderer, no browser
asset, no gaze primitive, and no `serve` verb in this repo yet. What exists is
the `culture-agent-template` baseline — an agent-first CLI skeleton, a mesh
identity, the vendored skill kit, and CI. *The face is the work, and it has not
started.* Keep that distinction visible when you write docs: describe the repo
as it is, and mark anything else `(planned)` or put it under a roadmap heading.

The authoritative statement of the lane is the build brief,
[agentculture/face-cli#1](https://github.com/agentculture/face-cli/issues/1).
Read it before designing anything. This file summarizes the parts that are
already decided and the parts that are still open; the issue is the source of
truth and the place to renegotiate.

## Naming — deliberately decoupled, do not "fix"

| Thing | Value |
|---|---|
| Console command | `face` |
| Import package | `face_cli` |
| PyPI distribution | `face-cli` |
| Argparse `prog` | `face-cli` |

The command is `face` but the import package is `face_cli` because a bare
`face` is a real published PyPI distribution (a `glom` dependency) — squatting
that top-level import would shadow it. This mismatch is intentional; leave it.

Practical consequence: the installed entry point is **`uv run face …`**, not
`uv run face-cli …`. The help text and `explain` catalog say `face-cli`
(the `prog`), and `explain` accepts both `face` and `face-cli` as the root key.

## Commands

```bash
uv sync                                  # create/refresh .venv from uv.lock
uv run pytest -n auto                    # full suite (xdist, ~22 tests, <1s)
uv run pytest tests/test_cli.py::test_whoami_json -v   # a single test
uv run pytest -n auto --cov=face_cli --cov-report=term # coverage (fail_under = 60)
uv run face whoami                       # identity from culture.yaml
uv run face learn --json                 # self-teaching prompt
uv run teken cli doctor . --strict       # the agent-first rubric gate CI runs
```

Lint — CI runs all five and any one failing fails the `lint` job:

```bash
uv run black --check face_cli tests      # line-length 100
uv run isort --check-only face_cli tests
uv run flake8 face_cli tests
uv run bandit -c pyproject.toml -r face_cli
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

Version bump (required on every PR — see Conventions):

```bash
python3 .claude/skills/version-bump/scripts/bump.py patch|minor|major
```

## Architecture — the CLI as it stands

The whole CLI is cited (cite-don't-import) from teken's `python-cli` reference,
which is why **the runtime package has zero third-party dependencies**;
`teken` is a dev dependency only. Four contracts hold it together, and the
rubric gate (`teken cli doctor . --strict`, 26 checks) enforces all of them:

- **Registration.** `face_cli/cli/__init__.py::_build_parser` imports each
  module under `cli/_commands/` and calls its `register(sub)`. Every command
  module owns its own parser, flags, and `set_defaults(func=…)`. Adding a verb
  never touches the dispatcher.
- **Errors.** Every failure raises `CliError(code, message, remediation)`
  (`cli/_errors.py`). `_dispatch` catches it, and wraps *any* other exception
  into one, so a Python traceback can never reach stderr. `_CliArgumentParser`
  overrides `argparse`'s `.error()` so parse failures take the same path and
  exit `1` rather than argparse's default `2`. Because parse errors happen
  before `args.json` exists, `main()` pre-scans raw argv for `--json` and
  stashes it in the class-level `_json_hint` — that is why the flag is peeked
  at twice, and it is load-bearing.
- **Streams.** `cli/_output.py` is the only writer: results to stdout,
  errors and diagnostics to stderr, never mixed, in both text and JSON mode.
- **Explain.** `face_cli/explain/catalog.py` maps command-path *tuples* to
  verbatim markdown. `tests/test_cli.py::test_every_catalog_path_resolves`
  walks every key, so an entry that exists must resolve; the rubric separately
  requires an entry for the root and a non-zero exit for a bogus path.

Two modules encode mesh identity rather than CLI mechanics:

- `cli/_commands/whoami.py` walks up from `__file__` (**not** the CWD) to find
  this agent's own `culture.yaml`, and hand-parses the first agent block
  without a YAML dependency — that is what keeps runtime deps empty. A wheel
  install ships no `culture.yaml`, so it falls back to literal defaults.
- `cli/_commands/doctor.py` mirrors the two invariants `steward doctor`
  verifies — prompt-file-present and backend-consistency — via the
  `_PROMPT_FILE` map (`claude` → `CLAUDE.md`, `colleague` →
  `AGENTS.colleague.md`, `acp` → `AGENTS.md`, `gemini` → `GEMINI.md`), plus a
  skills-present check. It returns the rubric's
  `{healthy, checks: [{id, passed, severity, message, remediation}]}` shape.

### Adding a verb or noun group

Five places, and the tests will catch you if you miss one:

1. A module in `face_cli/cli/_commands/` exposing `register(sub)`; add
   `--json` to every parser you create.
2. A `register()` call in `_build_parser()`.
3. An entry in `face_cli/explain/catalog.py` keyed by the path tuple.
4. The command map inside `cli/_commands/learn.py` — both `_TEXT` and
   `_as_json_payload()`. The rubric greps `learn` output for markers.
5. Tests in `tests/`.

Any noun group that gains action verbs must also expose `overview`
(`overview_cli_noun_exists`); descriptive verbs must not hard-fail on a bad
target path (`overview_graceful_on_bad_path` — see the ignored `target`
positional in `overview.py`).

### When the renderer lands

The empty-runtime-deps property is a feature of the scaffold, not a law of the
project — a browser renderer will need a server and screenshot tooling. Follow
the sibling pattern instead of adding hard top-level deps: put them behind an
extra (`[serve]`, `[vision]`), import them **lazily inside functions**, and
surface a missing dependency as a clean `CliError` with `EXIT_ENV_ERROR` (2)
pointing at the extra. `reachy-mini-cli`'s `reachy/vision/face.py` is the
reference implementation of that pattern in this workspace.

## The face work — what is decided

**The render target is the browser.** Decided by the operator; hold the line
when it gets inconvenient. Three reasons, all still true: no display server is
needed on a headless robot box or server; the screen showing the face need not
be the machine running the process; and a page can be screenshotted and diffed
in CI, which a native window effectively cannot. WebGL vs 2D canvas vs SVG is
an open technique choice — the operator specified the target, not the method.

**The rendered face must survive face recognition.** This is an operator
requirement layered on the brief: our virtual face should be recognizable *as a
face, and as a consistent identity*, by the same machinery that recognizes real
people. The concrete pipeline is the sibling `face-recognition-cli`'s, which
extracts `reachy-mini-cli`'s OpenCV engine (`reachy/vision/face.py`):

- **YuNet** (`face_detection_yunet_2023mar.onnx`) for detection — default
  score threshold `0.6`, NMS `0.3`, `320x320` input, largest-face selection.
- **SFace** (`face_recognition_sface_2021dec.onnx`) for a 128-dim embedding,
  taken after `alignCrop` on YuNet's five landmarks.

That has three consequences worth holding onto:

1. It effectively answers the brief's stylised-vs-realistic question. A face
   abstract enough to be two floating eyes will not fire a YuNet detection at
   `0.6`. The render needs the landmark geometry YuNet regresses — two eyes, a
   nose tip, two mouth corners — in plausible proportion, with enough tonal
   contrast to survive `alignCrop`. It does not need photorealism, and chasing
   photorealism buys the uncanny valley; "passes a detector" is a much cheaper
   and much more testable bar than "looks real".
2. It replaces "it looks 3D" with an assertion CI can actually make. Render at
   a known gaze angle → YuNet detects exactly one face above threshold →
   SFace's embedding stays cosine-close to an enrolled reference across the
   whole gaze range. That gates *both* halves of the brief at once: a face that
   stops being detectable at ±40° yaw has failed the 3D illusion in a way a
   screenshot diff would not have caught.
3. It defines the composition with the sibling without merging the lanes.
   `face-cli` renders; `face-recognition-cli` enrolls and matches; the loop
   closes when the same identity comes back. That integration is explicit and
   coordinated through issues (use the `communicate` skill), not a merge —
   this repo does no recognition, and that one does no rendering. Note the
   sibling is *also* a bare scaffold today, so the near-term testable path is
   OpenCV's YuNet/SFace directly, behind an extra, with the sibling adopted as
   soon as it has a surface.

### Lane boundaries with siblings

- `face-recognition-cli` — perception (identifies real people from frames).
  Shares the subject, nothing else.
- `reachy-mini-cli` — a physical head that actually turns; the on-screen
  counterpart to this. Plausible that a Reachy gets its face from here; agree
  it with that agent rather than assuming.
- `storybook-cli` — also renders to a browser, but its output is a *document*;
  this one is a *live surface*.
- `reterminal-cli` — e-paper; its refresh rate is hostile to continuous gaze.
  Not a first target.

## The face work — what is still open

Decide these deliberately and **record the decision** (a `docs/` note plus a
CHANGELOG entry); do not let them get settled by accident in a commit:

- **How a one-shot CLI call moves an already-rendered face.** Served page plus
  a control channel (websocket / SSE / polled state file), a state file the
  page watches, or something else.
- **Whether there is a `serve` verb** that owns the page, with `look` /
  `express` driving it — and what happens when nothing is serving: error, or
  autostart.
- **The gaze primitive.** Yaw/pitch degrees, a normalized direction vector, a
  screen-space point, or a named target. Whatever it is, an agent must be able
  to compute it with no human in the loop.
- **Whether expression is in scope at all.** The operator asked for direction.
  Expression is the obvious neighbour and was *not* requested — decide
  explicitly rather than drifting into it. (Note the repo description and
  `pyproject.toml` already say "gaze and expression surface", which is drift to
  resolve one way or the other.)
- **What `--json` returns for a verb whose real output is pixels.** A
  screenshot path is one honest answer; the resolved gaze state is another.
- **Who runs the render loop** — browser-side animation with the CLI setting
  targets (almost certainly right) or process-side frame pushing.
- **One face or many** per host.
- **Pre-rendered assets and their licence**, if any ship. A public repo with
  vendored face art needs that answer before the first release.

The path for deciding them is the vendored workflow chain: `/scope` → `/think`
→ `/challenge` → `/spec-to-plan`, then `/assign-to-workforce` if the plan wants
parallel lanes.

## Identity

```yaml
agents:
- suffix: face-cli
  backend: colleague
  model: sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP
```

`backend: colleague` fixes the resident prompt file to **`AGENTS.colleague.md`**
— the mesh runtime reads that file, while this `CLAUDE.md` is the Claude Code
guidance file. Both `steward doctor` and `face doctor` check the pair, and it
currently passes. (The scaffold seed this file replaced claimed
`backend: claude`; that was wrong — the checked-in value is `colleague`.) The
build brief asks that `culture.yaml` be reconciled against the backend actually
run; if this agent is promoted to `claude`, flipping the `backend` value is the
whole change — `doctor` already maps `claude` → `CLAUDE.md`, but
`tests/test_cli.py` asserts `backend: colleague` in two places and would need
updating with it.

## Conventions and workflow

- **Every PR bumps the version** — even docs/config/CI-only PRs. Use the
  `version-bump` skill; the `version-check` CI job blocks merge otherwise, and
  the bump script leaves the CHANGELOG sections blank, so write a real entry.
- **PRs go through the `cicd` skill** (`devex pr` + SonarCloud gating). Sign
  online posts as `- face-cli (Claude)`; the `cicd` / `communicate` scripts
  resolve that nick from `culture.yaml` automatically, so do not hand-sign in
  bodies those scripts author.
- **Reach for `ask-colleague` reflexively.** Its value is a *second,
  independent mind* (a different backend/model), not a stronger one. Before
  presenting or opening a PR on a non-trivial committed diff, run `review`; for
  a fresh read of an unfamiliar area, run `explore`. Both are read-only in a
  throwaway worktree, so the reflex is always safe. `write --apply` / `--pr`
  needs the user's go-ahead. Treat its output as an opinion to verify and own.
- **The vendored `.claude/skills/` are cited verbatim** — do not reformat or
  edit their scripts. Re-sync from guildmaster (or the tracked direct-from-origin
  exceptions) per `docs/skill-sources.md`. Prerequisites on PATH: `devex`
  (>=0.21) and `agtag` (>=0.1); `colleague` is optional.
- **Deploy**: pushing to `main` publishes to PyPI via Trusted Publishing;
  PRs do a TestPyPI dry-run. Both jobs only fire on changes to `pyproject.toml`
  or `face_cli/**`. A PyPI / TestPyPI Trusted Publisher must be registered for
  `face-cli` before the first real release — `guild create` configured the
  GitHub side only.

### Worktrees

Every worktree you create by hand lives in one repo-named directory beside the
checkout, one subfolder per worktree:

```bash
git worktree add ../.worktrees.face-cli/<name> -b <branch>
```

Never a shared `../worktrees/`: this workspace holds ~150 sibling projects, and
a generic shared folder accumulates orphaned trees from several repos at once
with nothing indicating ownership — a stale-tree sweep cannot tell a live lane
from junk. Scope the branch prefix to the work (`gaze/t2`, not `agent/t2`);
plain `agent/*` collides with leftovers from earlier fan-outs and `git worktree
add -b` fails on an existing branch. The vendored `assign-to-workforce` skill's
fan-out example uses *both* the shared path and `agent/<task-id>` branches —
it is cited verbatim and must not be edited, so override both when following
it. Remove with `git worktree remove <path>` (which deletes the directory);
`git worktree prune` only clears metadata for directories already gone. Never
`rm -rf` a worktree you did not create. Exception: `ask-colleague`'s read-only
verbs create their own detached worktree under `${TMPDIR:-/tmp}` and reap it on
an EXIT trap — outside this rule, not a violation of it.

### Memory discipline — recall before, remember after

This repo keeps its eidetic memory **in-repo and public**: a plain `/remember`
resolves to `<repo-root>/.eidetic/memory` — committed, shared with the team and
mesh peers, with the `claude` and `colleague` backends reading the same
`face-cli` scope. So memory travels with the repo rather than a private
home-dir store.

- **`/recall` before you start** a non-trivial task — prior decisions, gotchas,
  "have we done this before?" — so you build on what is known.
- **`/remember` when something worth keeping surfaces**: a non-obvious decision
  and its rationale, a constraint, a fix and *why*, a gotcha that cost time.
  Capture it as it happens.

Pass `--visibility private` to keep a record out of the committed store (it
routes to `$HOME/.eidetic/memory`); `/recall` reads both and merges. Do not
store what the repo already records — code structure, git history, or anything
already in this file or `CHANGELOG.md`.

## Layout

```text
face_cli/                 agent-first CLI (cited from teken's python-cli reference)
  cli/                    parser, error/output contract, _commands/ (verbs)
  explain/                markdown catalog for `explain`
tests/                    pytest smoke + introspection tests
.claude/skills/           vendored guildmaster/devague/colleague skill kit (verbatim)
docs/skill-sources.md     skill provenance ledger + re-sync procedure
culture.yaml              mesh identity (suffix + backend)
AGENTS.colleague.md       resident prompt for the colleague backend
.github/workflows/        tests + lint + version-check; PyPI Trusted Publishing
```
