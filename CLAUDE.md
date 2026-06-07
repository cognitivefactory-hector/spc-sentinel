# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

A running Django + Channels app. `PLAN.md` milestones **M0–M6 are done** (scaffold, SPC engine, generator, forecaster, backend stream, dashboard UI, polish/deploy-prep); **M7** (Decision Record completion + recorded whiteboard) is the remaining differentiator. The build follows `PLAN.md` as thin vertical slices, each kept runnable.

### Commands
- `make run` (or `docker compose up --build`) — serve at http://localhost:8000
- `pytest` — full suite; `pytest tests/test_rules.py -q` for one file
- `ruff check .` and `ruff format --check .` — lint/format (CI runs both)
- `python -m sentinel.sim.generator` — print a reproducible sample stream
- Local venv: `python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt`

### Workflow conventions (this repo)
- Each milestone is built on its own branch and merged via PR (`gh pr create`), not committed straight to `main`.
- A commit-message hook **requires** a What / Why / Who / Where body — author messages from a file with `git commit -F`.
- TDD the pure logic (`sentinel/spc/`, `sentinel/sim/`): write the test, watch it fail, then implement.
- For UI changes, verify in a real browser (Playwright/Chrome DevTools MCP), not just tests — that's how the M5 alert-fatigue bugs were caught. Run with `SPC_SAMPLE_RATE_HZ=8 SPC_WARMUP=20` for fast verification.

## What this project really is (read before building)

This is a **job-search portfolio piece with three deliverables of equal weight**, not a "look, it runs" demo:

1. The working app (hosted, clickable).
2. `DECISIONS.md` — a Decision Record structured around four questions: **Situation · Decision · Risk · Change**.
3. A recorded 5–8 min whiteboard session defending the hardest design decision under push-back.

The hireable signal is **judgment**, not that the code runs. Milestone **M7** (decision record + whiteboard) is explicitly *the differentiator* — `PLAN.md`'s risk register calls out "skipping M7 because the app looks done" as the main failure mode. Treat M7 as load-bearing, not cleanup.

When your work touches a design choice (model selection, sensitivity tuning, host, channel layer), capture the reasoning in `DECISIONS.md` **as you build**, while it's alive — Situation / Decision (incl. what was *rejected*) / Risk (incl. what was *consciously accepted*) / Change.

## Hard constraints

- **Synthetic data only — never any employer IP.** No TAT/MSI data, numbers, or recipes. Use obviously-fake round baselines (concentration ~25 g/L, temp ~35 °C, thickness ~12 µm). A disclaimer ("Simulated data; not affiliated with any employer") must be in both the README and the UI footer.
- **Ship the explainable model, not the higher-accuracy black box.** This is the project's spine (see `DECISIONS.md` and `WHITEBOARD-DRILL.md` Q1). The SPC rule engine is deterministic *on purpose*; the only "learned" part is the short-horizon drift forecast. Be precise about what's rules vs. modeled — **over-claiming "AI" is a documented red flag.**
- **Hold the non-goals (YAGNI).** No real plant/historian/OPC-UA connectivity, no user accounts, no multi-tenant, no persistence beyond a rolling window, no SPA, no AutoML. See `SPEC.md` §4.4.
- **Host must support long-running WebSockets.** Target is Render (Dockerized) behind Cloudflare. Cloudflare Pages is static-only and **cannot** run the backend.

## Architecture (as planned)

A real-time pipeline: a seeded synthetic **data generator** (timer task, ~1 Hz) feeds each sample through a pure **SPC engine** (control limits + Western Electric/Nelson rules) and a **drift forecaster** (EWMA / rolling trend → time-to-breach), producing **plain-English alert** objects. Samples + alerts stream to the browser over a **Channels WebSocket**; REST endpoints handle control (`POST /inject`, `POST /reset`, `GET /config`). Frontend is Django templates + HTMX + Plotly — deliberately no JS framework, because the substance is the SPC engine.

- **Backend:** Django + Channels (ASGI), run under uvicorn/daphne. In-memory channel layer (single-process demo — Redis only if scaling out).
- **Logic libs:** numpy, pandas, scipy; scikit-learn only if a learned residual model is added later.
- **Planned layout** (`PLAN.md` "Suggested repo layout"): pure framework-free logic lives in `sentinel/spc/` (`limits.py`, `rules.py`, `forecast.py`) and `sentinel/sim/generator.py`; `sentinel/consumers.py` is the WebSocket consumer; `sentinel/alerts.py` turns a rule hit into a sentence.

## Testing strategy

- **TDD the pure logic.** The `spc/` and `sim/` modules are pure, deterministic-with-a-seed functions — write tests *first*. Per `PLAN.md`: each SPC rule needs both a positive test (a hand-built series that trips it) and a negative test (a clean series that trips none).
- One smoke test for the WebSocket pipeline (a sample round-trips; an injected drift produces an alert).
- Don't chase UI test coverage — the UI is demonstrated by the whiteboard recording.
- Tooling (planned in M0): `pytest` for tests, `ruff` for lint, GitHub Actions CI. Local run via `docker compose up` (or a `make run`).

## Source-of-truth docs

- `SPEC.md` — full product spec, the four-question framing (§1), SPC/detection logic (§7), Definition of Done (§8).
- `PLAN.md` — milestone build sequence M0–M7 with per-milestone acceptance criteria.
- `WHITEBOARD-DRILL.md` — rehearsed adversarial challenges; the "⚠ Your move" notes mark answers only the owner can supply (real AUC gap, dollar costs, real-data failure modes) once built/measured.
