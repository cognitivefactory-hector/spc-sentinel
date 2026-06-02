# Whiteboard Drill — SPC Sentinel (design-stage)

> Rehearsal for the recorded whiteboard session. **The push** is me playing tough reviewer; **Defense** is the position that survives; **⚠ Your move** is what only you can answer once you've built/measured it. Fold the survivors into `DECISIONS.md`, then record.
> Scope: design-stage (pre-build reasoning). Re-run a second drill after **M5** once you've tuned sensitivity on real injected drifts.

## Q1 — "A black-box anomaly model benchmarks higher on your synthetic data. Why ship the 'worse' one?"
**The push:** You're leaving accuracy on the table to feel good about explainability.
**Defense (survives):** On the floor the metric isn't AUC, it's *acted-on* alerts. An alert an operator can't trace to a cause gets muted — and a muted accurate model catches nothing. I optimized for the alert that triggers a correct action at 2 a.m., not the one that wins an offline benchmark. The black box also can't tell the operator *which knob to turn*.
**⚠ Your move:** State the actual AUC gap on your synthetic data, and the gain that *would* flip you (e.g., "if a black box gave per-feature attributions I could surface, and beat rules by >X, I'd revisit"). Naming the reversal condition is what makes this judgment, not dogma.

## Q2 — "Western Electric rules are from 1956. Isn't this just a dashboard of if-statements? Where's the 'AI'?"
**The push:** Don't dress up `if x > 3*sigma` as machine learning.
**Defense (survives):** Correct — the rule engine *is* deterministic, and that's a deliberate feature (explainability where it's earned). The learned part is the **short-horizon drift forecast (time-to-breach)** and cause attribution, not the rules. I'll say exactly what's rules vs. modeled. Over-claiming "AI" is the red flag here; precision is the credible move.
**⚠ Your move:** Be ready to point at the forecasting code and say what model it is (EWMA/rolling-trend) and why it's enough.

## Q3 — "Your false-alarm threshold is a judgment call. Justify it with a number."
**The push:** You picked a sensitivity out of the air.
**Defense (survives):** I tied it to the **cost asymmetry**, not a textbook 3σ: cost(false alarm) ≈ operator-investigation-minutes × alert frequency; cost(missed drift) ≈ scrapped-lot value. I set sensitivity where expected nuisance cost is a small fraction of expected prevented scrap, and I bias toward protecting trust in the strong signals.
**⚠ Your move:** Put rough dollars on it — scrap cost per lot, minutes per false alarm. Even ballpark numbers make this concrete and senior.

## Q4 — "It runs on synthetic data you generated. How do I know it works on real, messy plant data?"
**The push:** Your generator can't fake sensor dropouts, clock skew, mislabeled tags.
**Defense (survives):** It can't, and I won't pretend otherwise — the synthetic demo proves the *method*, not field-readiness. First validation on real data: re-fit control limits on a real in-control window, then measure the detector's false-alarm rate on real *quiet* data before trusting any alert. Honest about the gap is the point.
**⚠ Your move:** Name the top 2–3 real-data failure modes from your actual experience (you've lived these) — that lived specificity is your edge.

## Q5 — "An operator ignores the alert and scraps a lot anyway. Whose fault is the design?"
**The push:** Your dashboard didn't prevent anything.
**Defense (survives):** The system is accountable for **signal quality and clarity** — the alert names the variable, the likely cause, and a recommended action, so it's actionable, not a z-score. If actionable alerts are ignored, that's a process/training gap; but burying the true signal in false alarms *is* a design failure — which is exactly why Q3 (tuning) matters. The human owns the action; I own making the right action obvious.

## Verdict — SDRC after the drill
- **Holds:** the trust-over-accuracy decision; the alert-fatigue risk framing; HITL accountability split.
- **Sharpen:** add the **reversal condition** to the Decision (Q1) and **rough dollar numbers** to the Risk (Q3); state plainly what's rules vs. learned (Q2).
- **Land this line in the room:** *"I shipped the model an operator will act on at 2 a.m. — not the one that wins a benchmark."*
