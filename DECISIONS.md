# Decision Record — SPC Sentinel

The four questions that make judgment portable (`SPEC.md` §1). These started as the first-draft answers in §1.1; what's below is the version that **survived** the adversarial drill (`WHITEBOARD-DRILL.md`) and the build — sharpened with the reversal condition, the cost numbers, and the precise rules-vs-learned line that the drill flagged as the work only I could do.

## Situation
Wet-process lines (plating, anodizing, etch) drift slowly: bath concentration depletes, temperature creeps, deposition thickness wanders. By the time a part fails final inspection, a lot is already scrapped. Operators have SPC charts, but they're retrospective — they flag an out-of-control point *after* it happened. Facts I have: streaming sensor readings. Facts I'm missing: a clean labeled history of "this drift led to that failure," because nobody logged it cleanly — so a supervised "predict the failure" model has nothing trustworthy to train on, which itself pushes toward a transparent method over a learned one.

## Decision
Use classical SPC rules (Western Electric / Nelson) **plus a transparent, explainable drift detector** — a short-horizon **rolling linear-trend** forecast with a slope-significance threshold — to estimate time-to-breach and warn before the limit is crossed.

**Rejected: a higher-accuracy black-box anomaly model** (e.g., a deep autoencoder). An operator won't act on an alert they can't trace to a cause, so a model that's a few % better on offline AUC but can't say *which knob to turn* is *worse* on the floor. The on-floor metric isn't AUC — it's **acted-on alerts**, and a muted accurate model catches nothing.

**Reversal condition (when I'd change my mind):** if a black box produced **per-feature attributions an operator could act on** ("concentration is driving this") *and* beat rules-plus-trend on **acted-on-alert precision** by a margin that survives the trust test — not just a benchmark — I'd adopt it. Naming that condition is what makes this judgment rather than dogma.

**What's rules vs. what's "learned" (no over-claiming):** detection is deterministic if-logic, on purpose — that's the explainability. The only fitted component is the time-to-breach forecast (a rolling least-squares slope + a t-test). Cause attribution is a per-signal lookup, not a model. I don't call the rules "AI."

## Risk
The real risk is **alert fatigue**: too many false alarms and operators mute the system, so a true drift gets ignored — the classic prevented-loss failure. So I tune sensitivity to the **cost of a wrong call**, not a textbook 3σ default.

**The asymmetry, in rough numbers** *(illustrative, synthetic — replace with real plant figures):* a scrapped wet-process lot might be ~$8k; a false alarm costs an operator ~10 min to investigate, ~$10 of loaded labor. On pure dollars that says "be extremely sensitive" — one prevented lot pays for ~800 nuisance alerts. **But the binding constraint isn't dollars, it's trust:** past a couple of false alarms a shift, operators stop believing the system. So the real ceiling is a *trust budget* (≈1–2 nuisance alerts/shift), not the dollar break-even — which is exactly why the forecast gate is set at a ~3σ slope significance, high enough to protect that budget.

**Consciously accepted:** slightly more missed *weak* signals, to protect trust in the *strong* ones. A weak drift gets caught on the next pass; a muted system catches nothing.

## Change
Drift is caught while it's still correctable, scrap drops, and the alert tells the operator *which* variable is moving and *why it matters* — in plain English, not a z-score. The prevented loss: the scrapped lot that didn't happen because the trend was caught early, by a system the operator still trusts because it hadn't cried wolf.

## Whiteboard session
- **Recording:** _TBD — record per `WHITEBOARD-SCRIPT.md` (5–8 min), then link here and in the README._
- **What I revised under push-back:** the first-draft Decision asserted "ship the explainable one" but hand-waved *when* that's wrong. Under the drill I added a concrete **reversal condition** (per-feature attributions + acted-on-alert precision) and put **rough dollars** on the risk — moving it from a stance to a defensible trade.
- **What I held the line on, and why:** trust over accuracy. The on-floor metric is the alert an operator acts on at 2 a.m., not the one that wins an offline benchmark — and the build proved the point when the first live run drowned in noise-driven forecast alerts and I had to add the significance gate and debounce to make it trustworthy.
- **The line to land in the room:** *"I shipped the model an operator will act on at 2 a.m. — not the one that wins a benchmark."*

---

## Engineering decisions (recorded as built)
- **Backend:** Django + Channels (ASGI) — one framework across the whole portfolio; Channels handles the live WebSocket. Channel layer: in-memory (single-process demo).
- **Host:** Render (Dockerized) behind Cloudflare. _Why:_ lowest-friction Docker + WebSocket support; AWS would be overkill for a small always-on demo.
- **Frontend:** a single Django template + Plotly + vanilla JS over the WebSocket (no SPA, and no HTMX — the realtime layer is a socket, so HTMX would add a dependency without earning it; the substance is the SPC engine, not a JS framework).
- **Control limits: frozen from a warm-up window, not rolling.** _Why:_ a rolling recompute would slowly absorb a genuine drift into the limits and never breach — the exact failure this tool exists to prevent. _Accepted cost:_ the limits don't adapt to a legitimately new normal; for a synthetic demo that trade is clearly right, and on real data you'd re-baseline deliberately, not continuously.
- **σ via the moving-range estimator (MR̄/d₂), not the sample std.** _Why:_ the sample std is inflated by any trend present in the warm-up window, widening the band and masking drift; the I-chart moving-range estimate is the standard, more robust choice.
- **Shared single Engine + one producer task.** _Why:_ the in-memory channel layer is single-process, so one shared engine (stepped by a lone producer, broadcast to a Channels group) is the simplest correct design — REST `inject`/`reset` mutate the same instance every client sees. Redis/multi-process is a non-goal for the demo.
- **Forecast alerts gated by a slope t-statistic (~3σ), not raw breach projection.** _Why:_ with tight limits and noise, "project the trend to a limit" fires on every noise-driven wobble — textbook alert fatigue, the exact failure this project is about. The gate fires only when the trend is statistically real (slope ≥ 3 standard errors from zero). _This is the sensitivity knob_ defended in the whiteboard (Q3): a single, tunable number tied to the cost of a wrong call. _Accepted cost:_ slightly later warning on weak signals, to protect trust in the strong ones.
- **Alerts are edge-triggered (debounced per signal+rule), not re-fired every sample.** _Why:_ a persistent condition (a long run, a held breach) would otherwise emit an identical alert every sample and bury the signal in its own noise — again, alert fatigue. A given (signal, rule) re-alerts at most once per cooldown.
- **Injected drift persists (holds after its ramp); steps self-heal.** _Why:_ a real process drift doesn't auto-correct — it keeps going until someone acts. Holding makes the demo honest (drift → breach → stays breached until Reset) and matches the human-in-the-loop story; a step disturbance is genuinely transient, so it reverts.
- **Dashboard status is derived from the live value vs. limits each tick, not from the (sparse, debounced) alert stream.** _Why:_ a debounced alert stream leaves the banner stale and occasionally contradicting the chart; deriving status from current data keeps the headline always truthful, while the rich plain-English alert text still drives the log.
