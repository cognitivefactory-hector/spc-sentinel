# SPC Sentinel — Implementation Plan

Companion to `SPEC.md`. This is the build sequence: milestones, concrete tasks, acceptance criteria, and the definition of done. It is self-contained — you can hand this repo to a fresh session (or another engineer) and start.

- **Repo:** `spc-sentinel` (public, under `cognitivefactory-hector`)
- **Approach:** thin vertical slices — each milestone produces something runnable. Write tests for the SPC engine *before* the engine (it's pure logic and easy to TDD).

---

## The spine (carry through every milestone)

Keep `DECISIONS.md` open as you build and capture reasoning live, organized as:

> **Situation** · **Decision** (incl. what you *rejected*) · **Risk** (incl. what you *accepted*) · **Change**.

The hardest decision (explainable detector over a black-box model) is the spine of the **recorded whiteboard session** — see `SPEC.md` §3.

---

## Prerequisites
- Python 3.11+, Docker, a GitHub account (`gh` CLI authenticated).
- A host that supports long-running WebSocket processes for the live demo (Render / Railway / Fly.io / VPS).

---

## Milestones

### M0 — Repo scaffold *(½ day)*
**Goal:** an empty-but-real repo that runs `hello`.
- [ ] Create folder, add `SPEC.md` + `PLAN.md`.
- [ ] Add `README.md` (stub), `DECISIONS.md` (paste the four-question template from `SPEC.md` §10), `.gitignore` (Python), `LICENSE` (MIT).
- [ ] Confirm **Django + Channels** (ASGI) for the WebSocket layer; note the channel-layer choice (in-memory for the demo) in `DECISIONS.md`.
- [ ] `pyproject.toml`/`requirements.txt`, a `Dockerfile`, and a `make run` (or `docker compose up`) that serves an empty page.
- [ ] `gh repo create … --public --source=. --push`.
- **Acceptance:** `docker compose up` serves a page at `localhost`; repo is on GitHub.

### M1 — SPC engine (pure logic, TDD) *(1–2 days)*
**Goal:** a tested, framework-free module that takes a series and returns control limits + rule violations.
- [ ] `spc/limits.py`: compute centerline, ±1/2/3σ from a warm-up window.
- [ ] `spc/rules.py`: implement ≥4 Western Electric / Nelson rules (cite source in comments).
- [ ] **Tests first:** `tests/test_rules.py` with hand-built series that trip each rule and a clean series that trips none.
- **Acceptance:** `pytest` green; each rule has a positive and a negative test.

### M2 — Data generator *(1 day)*
**Goal:** seeded synthetic telemetry with injectable disturbances.
- [ ] `sim/generator.py`: baseline + diurnal drift + Gaussian noise; 3 signals; fixed seed.
- [ ] Inject API: `inject(signal, kind=drift|spike|step, magnitude, duration)`.
- [ ] Tests: with seed set, output is reproducible; an injected drift shows the expected slope.
- **Acceptance:** `pytest` green; a script prints a reproducible sample stream.

### M3 — Drift forecaster *(1 day)*
**Goal:** short-horizon "time-to-breach" estimate.
- [ ] `spc/forecast.py`: EWMA or rolling linear trend → samples-until-limit → minutes (via sample rate).
- [ ] One documented sensitivity parameter (window length / EWMA λ).
- [ ] Tests: a known downward ramp yields a finite, decreasing time-to-breach.
- **Acceptance:** `pytest` green; forecaster returns sane estimates on injected drift.

### M4 — Wire backend: stream + control *(1–2 days)*
**Goal:** the generator → engine → WebSocket pipeline and REST controls.
- [ ] Timer task drives the generator (e.g., 1 Hz, configurable).
- [ ] Each sample runs through limits + rules + forecaster; build an alert object when something fires.
- [ ] WebSocket pushes `{samples, limits, alerts}`; REST endpoints: `POST /inject`, `POST /reset`, `GET /config`.
- [ ] Alert builder turns a rule hit into a plain-English sentence (see `SPEC.md` §4.2 #4).
- **Acceptance:** a WebSocket client receives a live stream; `POST /inject` changes it within seconds.

### M5 — Dashboard UI *(2 days)*
**Goal:** the clickable demo.
- [ ] Live charts (Plotly or Chart.js) with UCL/LCL/centerline drawn.
- [ ] Alert banner + scrolling alert log (timestamp, signal, rule, projected vs. actual).
- [ ] **"Inject drift" controls** (the demo hook) wired to `POST /inject`; a `reset` button.
- [ ] Footer disclaimer: "Simulated data; not affiliated with any employer."
- [ ] Responsive enough to look right on a laptop and a phone.
- **Acceptance:** open the URL, click inject, watch the chart drift and an alert fire with a readable message.

### M6 — Polish, README, deploy *(1 day)*
- [ ] `README.md`: what/why, one-command local run, screenshots/GIF, and links to live demo + `DECISIONS.md` + whiteboard video.
- [ ] Deploy to the chosen host; smoke-test the WebSocket in production.
- [ ] Point `spc.hector-garza.com` at it (optional but recommended).
- **Acceptance:** the public URL works from a fresh browser; the GIF in the README matches reality.

### M7 — Decision Record + Whiteboard session *(½ day)* — **do not skip; this is the differentiator**
- [ ] Complete `DECISIONS.md` (Situation/Decision/Risk/Change, the rejected option, the accepted risk).
- [ ] Record the 5–8 min whiteboard session using the challenge script in `SPEC.md` §3.1.
- [ ] Embed/link the recording in the README and on hector-garza.com.
- **Acceptance:** a stranger can read `DECISIONS.md` + watch the video and explain *why* you chose the explainable detector.

---

## Testing strategy
- **Unit-first** for `spc/` and `sim/` — pure functions, fast, deterministic with a seed.
- Smoke test for the WebSocket pipeline (one sample round-trips and an injected drift produces an alert).
- Don't chase UI test coverage; the UI is demonstrated by the recording. Keep the logic well-tested.

## Suggested repo layout
```
spc-sentinel/
├── README.md
├── SPEC.md
├── PLAN.md
├── DECISIONS.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml            # or requirements.txt
├── manage.py
├── config/  settings.py  asgi.py  urls.py     # ASGI entrypoint for Channels
├── sentinel/                 # the Django app
│   ├── consumers.py          # Channels WebSocket consumer: streams samples + alerts
│   ├── views.py              # REST: inject / reset / config
│   ├── spc/  limits.py rules.py forecast.py    # pure logic (framework-free)
│   ├── sim/  generator.py
│   ├── alerts.py             # rule hit → plain-English message
│   └── templates/  index.html   ( + HTMX / Plotly, static/ )
└── tests/  test_rules.py test_generator.py test_forecast.py
```

## Risk register (project execution, not the product)
| Risk | Mitigation |
|---|---|
| Scope creep into "real" data integrations | Hold the line on synthetic-only (it's in Non-Goals). |
| WebSocket host friction on a static-only platform | Pick Render/Railway/Fly early; Cloudflare Pages can't run the backend. |
| Skipping M7 because the app "looks done" | M7 *is* the point of the portfolio. The app without the decision record is the exact thing that "stopped working." |
| Accidentally over-claiming "AI" | Be precise in README: rules + forecasting + cause attribution; say what's ML and what isn't. |

## Definition of Done
See `SPEC.md` §8 — all three deliverables (app, decision record, whiteboard recording) exist and are linked from the README.
