# SPC Sentinel — Design Spec

**Project 1 of the Hector Garza portfolio.** Self-contained: everything needed to start this as its own repository is in this file and its companion `PLAN.md`. You do not need any other file from the `career/` folder to build this.

- **Owner:** Hector Garza · hectorg@smartxchain.com · hector-garza.com
- **Status:** Spec — ready to build
- **Suggested repo name:** `spc-sentinel`
- **One-liner:** A live statistical-process-control dashboard that predicts when a process will drift out of spec *before* it does — built so a 2 a.m. operator will actually trust and act on the alert.

---

## 0. Read this first — what this project is *really* for

This is a job-search portfolio project, but it is **not** a "look, it runs" demo. In 2026, anyone can make a demo run with AI; a working app no longer proves you understood the problem. The scarce, hireable signal is **judgment** — what you noticed, what you decided, what you *rejected*, the risk you removed, and what changed because you were in the room.

So this project has **three deliverables of equal weight**:

1. **The working app** (hosted, clickable).
2. **A Decision Record** (`DECISIONS.md`) structured around the four questions below.
3. **A recorded whiteboard session** (5–8 min) where you talk through the hardest design decision and defend it against push-back.

A hiring manager who opens this repo should learn *how you think*, not just that you can code.

---

## 1. The spine — four questions that make judgment portable

Every project in this portfolio is organized around these four questions. They appear here, in `DECISIONS.md`, and on the project's page at hector-garza.com. Fill them in *as you build*, while the reasoning is still alive.

> **1 · Situation** — What's happening, who's involved, the constraints, the facts you have and the facts that are *missing*. Context is where judgment begins.
>
> **2 · Decision** — The plausible paths, the one you took, and the credible options you *rejected*. Rejection shows what you refused to hand-wave.
>
> **3 · Risk** — What could go wrong, what you removed, and what you *consciously accepted*. Prevented losses count — name the bad outcome that didn't happen.
>
> **4 · Change** — What's different now: clearer, safer, faster. Connect the judgment to a real change in the work, not a diary entry.

### 1.1 First-draft answers for SPC Sentinel (defend/revise these on camera)

These are your starting position. The whiteboard session (§3) exists to pressure-test them.

- **Situation.** Wet-process lines (plating, anodizing, etch) drift slowly: bath concentration depletes, temperature creeps, deposition thickness wanders. By the time a part fails final inspection, you've already scrapped a lot. Operators have SPC charts, but they're retrospective — they tell you a point was out of control *after* it happened. The facts you have: streaming sensor readings. The facts you're missing: a labeled history of "this drift led to that failure," because nobody logged it cleanly.
- **Decision.** Use **classical SPC rules (Western Electric / Nelson) plus a transparent, explainable drift detector** (e.g., EWMA / rolling-trend with a clear threshold), and surface a short-horizon forecast. **You rejected a higher-accuracy black-box model** (e.g., a deep anomaly autoencoder) on purpose — an operator will not act on an alert they can't understand, so a model that's 3% more accurate but unexplainable is *worse* on the floor.
- **Risk.** The real risk is **alert fatigue**: too many false alarms and operators mute the system, so a true drift gets ignored — the classic prevented-loss failure. You tune sensitivity around the *cost of a wrong call* (scrap cost vs. nuisance), not a textbook 3-sigma default. You consciously accept slightly more missed weak signals to protect trust in the strong ones.
- **Change.** Drift is caught while it's still correctable, scrap drops, and the alert tells the operator *which* variable is moving and *why it matters* — in plain English, not a z-score.

---

## 2. Why this project (market fit)

- AI-in-manufacturing hiring (~620k roles, $145–310k) is driven first by **quality and predictive maintenance**; real-time anomaly detection and drift monitoring are named in nearly every manufacturing-AI job description.
- The 2026 theme is **agentic AI with a human keeping final approval** — this project demonstrates exactly that discipline: the model advises, the operator decides.
- It directly backs a claim already on the resume ("Built SPC dashboards with automated control-limit calculation and alerting"), so a manager can *click and verify* it.
- **Your unfair advantage:** you've lived control limits and floor reality for 25+ years. The judgment in §1.1 is yours, not something an AI-only candidate can fake.

---

## 3. The staged whiteboard session (recorded deliverable)

**Format.** 5–8 minutes. Screen + voice (Loom, or OBS → MP4). You at the "whiteboard" (a shared doc, a diagram, or the running app), talking through the design while an adversary pushes back. The adversary can be a strong engineer friend, or you can use the scripted challenges below and answer them on camera as if defending in an interview. Preserve the final, survived reasoning in `DECISIONS.md`.

**The point is not to be right on the first take.** It's to show you can hold a line when the argument is sound and update when it isn't — "learning in public without becoming mushy."

### 3.1 Adversarial challenge script (the push-back)

Answer each out loud; capture what survives.

1. **"A black-box anomaly model benchmarks higher on your synthetic data. Why are you shipping the 'worse' model?"**
   *(Defend the trust-over-accuracy decision. When is the black box actually right? Name the condition under which you'd reverse this.)*
2. **"Western Electric rules are from 1956. Isn't this just a dashboard with if-statements? Where's the 'AI'?"**
   *(Distinguish detection from short-horizon forecasting and cause attribution. Be honest about what's ML and what's rules — over-claiming is a red flag.)*
3. **"Your false-alarm tuning is a judgment call. Justify the threshold with a number."**
   *(Tie sensitivity to scrap cost vs. nuisance cost. Show the asymmetry math, even rough.)*
4. **"This runs on synthetic data you generated. How do I know it works on real, messy plant data?"**
   *(Name the gap honestly: sensor dropouts, clock skew, mislabeled tags. Describe what you'd validate first on real data.)*
5. **"An operator ignores the alert and scraps a lot anyway. Whose fault is the system design?"**
   *(Defend the human-in-the-loop framing; what does the UI do to earn the action?)*

### 3.2 What the recording must show

- The **Situation → Decision → Risk → Change** arc (§1.1), in your words.
- At least **one place you revised** your position under push-back (or a crisp reason you held it).
- A pointer to where the surviving reasoning lives (`DECISIONS.md`).

---

## 4. Product specification

### 4.1 Users
- **Primary:** a process engineer / line operator watching one or more wet-process lines.
- **Demo viewer:** a hiring manager who lands cold and must "get it" in 60 seconds.

### 4.2 Core features (MVP)
1. **Live chart view.** Real-time line charts for 3 simulated signals — e.g., *bath concentration (g/L)*, *bath temperature (°C)*, *deposition thickness (µm)* — with control limits (UCL/LCL/centerline) drawn.
2. **Rule engine.** Flags Western Electric / Nelson rule violations (1 point beyond 3σ; 2/3 beyond 2σ; 8 in a row one side; trend of 6/7; etc.).
3. **Drift forecast.** A short-horizon projection (EWMA or rolling linear trend) that estimates *"time-to-breach"* for each signal and warns *before* the limit is crossed.
4. **Plain-English alerts.** When something fires, show a human sentence: *"Bath concentration trending down — projected to fall below 18 g/L in ~22 min. Likely cause: drag-out depletion. Recommend a chemistry addition."*
5. **"Inject drift" control (the demo hook).** A button/slider that injects a drift, low/high excursion, or step shift into a chosen signal so a viewer can *watch the system catch it live*.
6. **Alert log.** A scrolling list of fired alerts with timestamp, signal, rule, and the projected vs. actual outcome.

### 4.3 Screens
- **Dashboard** (default): the live charts + alert banner + inject controls + alert log.
- **About / Decision Record** (or link out to hector-garza.com): the SDRC story and the embedded whiteboard recording.

### 4.4 Explicit non-goals (YAGNI)
- No real plant connectivity, no historian/OPC-UA integration. Synthetic data only.
- No user accounts, no multi-tenant, no persistence beyond a rolling window (a small in-memory buffer or SQLite/Postgres is fine; long-term storage is out of scope).
- No mobile-native app; responsive web is enough.
- No "AutoML" — the model choice is a deliberate, explainable one (that *is* the point).

---

## 5. Synthetic data (no employer IP — ever)

A generator produces realistic-but-fake telemetry. **No TAT/MSI data, numbers, or recipes are used.**

- Each signal = baseline + diurnal drift + Gaussian noise + occasional injected events.
- Suggested baselines (illustrative, generic): concentration ~25 g/L, temp ~35 °C, thickness ~12 µm; pick round numbers that are obviously synthetic.
- Generator runs server-side on a timer (e.g., 1 sample/sec, configurable) and streams to the client.
- The "inject" control writes an event into the generator's state so the next samples reflect the chosen disturbance.
- Ship a fixed **seed** so demos are reproducible.

---

## 6. Architecture & stack

Chosen to match the owner's existing stack (Django · Postgres · Docker) and to be trivially hostable as a live demo.

```
┌─────────────────────────────────────────────────────────┐
│  Browser (single-page dashboard)                          │
│   • Plotly/Chart.js live charts                            │
│   • WebSocket client ← streaming samples + alerts          │
│   • REST calls: inject drift, reset, get config            │
└───────────────▲───────────────────────┬───────────────────┘
                │ WebSocket (samples,     │ REST (control)
                │ alerts)                 │
┌───────────────┴───────────────────────▼───────────────────┐
│  Backend — Django + Channels (ASGI)                        │
│   • Data generator (timer task, seeded)                    │
│   • SPC engine: control limits + WE/Nelson rules           │
│   • Drift forecaster: EWMA / rolling trend → time-to-breach │
│   • Alert builder: rule hit → plain-English message        │
│   • Optional: SQLite/Postgres rolling buffer               │
└────────────────────────────────────────────────────────────┘
```

**Backend:** **Django + Channels** (ASGI) for the real-time WebSocket layer — one framework across the whole portfolio. The front end is **Django templates + HTMX + Plotly** (no heavy JS framework). Run under an ASGI server (`uvicorn`/`daphne`).

**Libraries:** `numpy`, `pandas`, `scipy` (stats), `plotly` (or Chart.js via CDN). Keep ML deliberately light — `scikit-learn` only if you add a learned residual model later.

---

## 7. SPC / detection logic (the substance)

- **Control limits.** Compute centerline (mean) and ±1/2/3σ from a rolling window or a fixed "in-control" warm-up period. Document which and why.
- **Rules (implement at least 4 of the 8 Western Electric / Nelson):**
  1. 1 point > 3σ from centerline.
  2. 9 (or 8) points in a row on one side of centerline.
  3. 6 points in a row steadily increasing or decreasing (trend).
  4. 2 of 3 points > 2σ on the same side.
  *(Cite the source in code comments.)*
- **Drift forecast.** Fit EWMA or a rolling linear regression to the last N points; extrapolate to estimate samples-until-limit-breach; convert to a time estimate using the sample rate.
- **Sensitivity knob.** A single, documented parameter (e.g., trend window length / EWMA λ) that trades false alarms vs. lead time. The whiteboard session defends its value.

---

## 8. Definition of Done

The project is "done" — and portfolio-ready — when **all three** exist and are linked together:

- [ ] **App** deployed and reachable at a public URL; "inject drift" visibly works; alerts render in plain English.
- [ ] **`README.md`** explains what it is, how to run locally (one command via Docker), and links the live demo + decision record + whiteboard video.
- [ ] **`DECISIONS.md`** completed using the §1 four-question template, including the option you rejected and the risk you accepted.
- [ ] **Whiteboard recording** (5–8 min) linked from the README and embedded on hector-garza.com.
- [ ] **Synthetic-data disclaimer** present in README and UI footer ("Simulated data; not affiliated with any employer").
- [ ] Tests for the SPC engine and forecaster pass (see `PLAN.md`).

---

## 9. Hosting / deployment

- Containerize with a single `Dockerfile` (+ `docker-compose.yml` if you add Postgres).
- **Live demo target:** any host that supports a long-running WebSocket process — Render, Railway, Fly.io, or a small VPS. (Cloudflare Pages is static-only, so it can host a *link/landing* but not the WebSocket backend.)
- Point a subdomain at it, e.g., `spc.hector-garza.com`, and link it from the resume's future "Selected Work" section.

---

## 10. Repo bootstrap (how to start this as its own repo)

You will create the repo yourself. Suggested steps:

```bash
# 1. Make the project folder and drop SPEC.md + PLAN.md in it
mkdir spc-sentinel && cd spc-sentinel
cp /path/to/01-spc-sentinel/SPEC.md .
cp /path/to/01-spc-sentinel/PLAN.md .

# 2. Seed the standard files
#    README.md (start from the Definition of Done links)
#    DECISIONS.md (paste the §1 four-question template)
#    .gitignore (python: __pycache__/, .venv/, *.pyc, .env)
#    LICENSE (MIT is fine for a portfolio)

# 3. Init and create the GitHub repo under your account
git init && git add -A && git commit -m "chore: scaffold spc-sentinel (spec + plan)"
git branch -M main
gh repo create cognitivefactory-hector/spc-sentinel --public --source=. --remote=origin --push
```

> **Note:** keep this repo PUBLIC (it's a portfolio piece) and confirm no real employer data is ever committed.

### `DECISIONS.md` starter (paste into the new repo)

```markdown
# Decision Record — SPC Sentinel

## Situation
<what's happening, who's involved, constraints, facts you have, facts missing>

## Decision
<the path taken; the credible options REJECTED and why>

## Risk
<what could go wrong; what you removed; what you consciously accepted>

## Change
<what's different now — clearer/safer/faster; the prevented loss>

## Whiteboard session
- Recording: <link>
- What I revised under push-back: <…>
- What I held the line on, and why: <…>
```

---

## 11. Open questions to resolve in the plan
- Channels layer: in-memory channel layer (fine for a single-process demo) vs. Redis (only if you scale out) — record the choice.
- Plotly vs. Chart.js for live charts.
- In-memory rolling buffer vs. SQLite/Postgres (default: in-memory for MVP).
