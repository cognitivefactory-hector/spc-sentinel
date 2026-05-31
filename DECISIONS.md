# Decision Record — SPC Sentinel

The four questions that make judgment portable. These are **first-draft answers** (from `SPEC.md` §1.1) — pressure-test and revise them in the recorded whiteboard session, then keep what survives.

## Situation
Wet-process lines (plating, anodizing, etch) drift slowly: bath concentration depletes, temperature creeps, deposition thickness wanders. By the time a part fails final inspection, a lot is already scrapped. Operators have SPC charts, but they're retrospective — they flag an out-of-control point *after* it happened. Facts I have: streaming sensor readings. Facts I'm missing: a clean labeled history of "this drift led to that failure," because nobody logged it cleanly.

## Decision
Use classical SPC rules (Western Electric / Nelson) **plus a transparent, explainable drift detector** (EWMA / rolling-trend with a clear threshold) and a short-horizon time-to-breach forecast.
**Rejected:** a higher-accuracy black-box anomaly model — an operator won't act on an alert they can't understand, so a model that's a few % more accurate but unexplainable is *worse* on the floor.

## Risk
The real risk is **alert fatigue**: too many false alarms and operators mute the system, so a true drift gets ignored — the classic prevented-loss failure. I tune sensitivity around the *cost of a wrong call* (scrap cost vs. nuisance), not a textbook 3-sigma default.
**Consciously accepted:** slightly more missed weak signals, to protect trust in the strong ones.

## Change
Drift is caught while it's still correctable, scrap drops, and the alert tells the operator *which* variable is moving and *why it matters* — in plain English, not a z-score. The prevented loss: the scrapped lot that didn't happen because the trend was caught early.

## Whiteboard session
- Recording: _TBD_
- What I revised under push-back: _…_
- What I held the line on, and why: _…_

---

## Engineering decisions (recorded as built)
- **Backend:** Django + Channels (ASGI) — one framework across the whole portfolio; Channels handles the live WebSocket. Channel layer: in-memory (single-process demo).
- **Host:** Render (Dockerized) behind Cloudflare. _Why:_ lowest-friction Docker + WebSocket support; AWS would be overkill for a small always-on demo.
- **Frontend:** Django templates + HTMX + Plotly (no SPA — the substance is the SPC engine, not a JS framework).
