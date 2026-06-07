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
- **Control limits: frozen from a warm-up window, not rolling.** _Why:_ a rolling recompute would slowly absorb a genuine drift into the limits and never breach — the exact failure this tool exists to prevent. _Accepted cost:_ the limits don't adapt to a legitimately new normal; for a synthetic demo that trade is clearly right, and on real data you'd re-baseline deliberately, not continuously.
- **σ via the moving-range estimator (MR̄/d₂), not the sample std.** _Why:_ the sample std is inflated by any trend present in the warm-up window, widening the band and masking drift; the I-chart moving-range estimate is the standard, more robust choice.
- **Shared single Engine + one producer task.** _Why:_ the in-memory channel layer is single-process, so one shared engine (stepped by a lone producer, broadcast to a Channels group) is the simplest correct design — REST `inject`/`reset` mutate the same instance every client sees. Redis/multi-process is a non-goal for the demo.
- **Forecast alerts gated by a slope t-statistic (~3σ), not raw breach projection.** _Why:_ with tight limits and noise, "project the trend to a limit" fires on every noise-driven wobble — textbook alert fatigue, the exact failure this project is about. The gate fires only when the trend is statistically real (slope ≥ 3 standard errors from zero). _This is the sensitivity knob_ defended in the whiteboard (Q3): a single, tunable number tied to the cost of a wrong call. _Accepted cost:_ slightly later warning on weak signals, to protect trust in the strong ones.
- **Alerts are edge-triggered (debounced per signal+rule), not re-fired every sample.** _Why:_ a persistent condition (a long run, a held breach) would otherwise emit an identical alert every sample and bury the signal in its own noise — again, alert fatigue. A given (signal, rule) re-alerts at most once per cooldown.
- **Injected drift persists (holds after its ramp); steps self-heal.** _Why:_ a real process drift doesn't auto-correct — it keeps going until someone acts. Holding makes the demo honest (drift → breach → stays breached until Reset) and matches the human-in-the-loop story; a step disturbance is genuinely transient, so it reverts.
- **Dashboard status is derived from the live value vs. limits each tick, not from the (sparse, debounced) alert stream.** _Why:_ a debounced alert stream leaves the banner stale and occasionally contradicting the chart; deriving status from current data keeps the headline always truthful, while the rich plain-English alert text still drives the log.
