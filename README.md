# SPC Sentinel

A live statistical-process-control dashboard that predicts when a process will drift out of spec **before** it does — built so a 2 a.m. operator will actually trust and act on the alert.

> **Status:** scaffolded (spec + plan in place). Build follows `PLAN.md` (M0 → M9).
> **Illustrative tool on synthetic data — not affiliated with any employer.**

Part of [hector-garza.com](https://hector-garza.com)'s portfolio. This repo is one of three equal deliverables: the app, a **Decision Record** ([`DECISIONS.md`](./DECISIONS.md)), and a recorded whiteboard session. A working demo no longer proves competence — the judgment behind it does. See [`SPEC.md`](./SPEC.md) §0.

## What it does
- Streams synthetic process telemetry (bath chemistry, deposition thickness, etch rate) with control limits.
- Flags Western Electric / Nelson rule violations.
- Forecasts short-horizon **time-to-breach** and warns before the limit is crossed.
- Plain-English alerts an operator can act on; an **inject-drift** control to demo it live.

## Tech stack
- **Backend:** Django + Channels (ASGI) for the real-time WebSocket layer
- **Logic:** NumPy / pandas / scikit-learn (pure, test-first SPC engine)
- **Frontend:** Django templates + HTMX + Plotly
- **Packaging:** Docker · **Quality:** pytest + ruff + GitHub Actions CI

## Deployment
- **Live demo:** Dockerized Django app on **Render**, fronted by **Cloudflare** (planned subdomain `spc.hector-garza.com`).
- Local run: one command via Docker (added in build step M0).

## Links (filled in as the build progresses)
- 🔗 Live demo: _TBD_
- 🧠 Decision record: [`DECISIONS.md`](./DECISIONS.md)
- 🎥 Whiteboard walkthrough: _TBD_

## Build
See [`PLAN.md`](./PLAN.md) — milestones M0 (scaffold) through M9 (decision record + whiteboard).
