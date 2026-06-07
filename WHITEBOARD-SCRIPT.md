# Whiteboard Script — SPC Sentinel (recording guide)

A ready-to-record guide for the 5–8 min whiteboard session (`SPEC.md` §3). Goal: a stranger watches this + reads `DECISIONS.md` and can explain *why the explainable detector*. Don't read it verbatim — these are the beats and the lines that must land. Record screen + voice (Loom or OBS → MP4); have the running app and `DECISIONS.md` open to point at.

**The one line to land:** *"I shipped the model an operator will act on at 2 a.m. — not the one that wins a benchmark."*

---

## Beat 0 — Frame it (~30s)
- "This is a live SPC dashboard that warns a wet-process line is drifting *before* it scraps a lot. Synthetic data — the point isn't the demo, it's the decisions behind it."
- "I'll walk the Situation → Decision → Risk → Change, then defend the hardest call against push-back."

## Beat 1 — Situation (~45s) · *show the live dashboard*
- "Plating/anodizing/etch baths drift slowly — concentration depletes, temperature creeps. By the time a part fails final inspection, you've scrapped a lot."
- "Operators already have SPC charts, but they're *retrospective* — they flag a bad point after it happened."
- "The fact I have: streaming sensor readings. The fact I'm missing: a clean labeled history of 'this drift caused that failure' — nobody logged it. So there's nothing trustworthy to train a supervised model on. That gap already nudges toward a transparent method."

## Beat 2 — Decision (~60s) · *inject a slow drift; watch time-to-breach fire*
- "Detection is classical Western Electric / Nelson rules — deterministic, explainable. The forecast is a rolling-trend time-to-breach. I deliberately **rejected a black-box anomaly model.**"
- *Click "Slow drift ↓", let it ramp:* "Watch — it's projecting the breach and naming the variable and a likely cause, in plain English."
- "The black box might win on offline AUC. But the on-floor metric isn't AUC — it's **acted-on alerts.** An alert an operator can't trace to a cause gets muted, and a muted accurate model catches nothing."

## Beat 3 — Risk (~60s)
- "The real risk is **alert fatigue.** Cry wolf a few times and operators mute the system — then a true drift sails through. That's the prevented-loss failure."
- "So I tuned to the cost of a wrong call, not a textbook 3σ. Rough numbers: a scrapped lot ~\$8k; a false alarm ~10 minutes, ~\$10. Pure dollars say 'be hypersensitive' — one lot pays for ~800 nuisance alerts."
- "**But the binding constraint is trust, not dollars.** Past a couple false alarms a shift, operators stop believing it. So I tune to a *trust budget* — about one or two nuisance alerts a shift — which is why the forecast only fires on a ~3σ-significant slope. I consciously accept missing some *weak* signals to protect trust in the *strong* ones."

## Beat 4 — Change (~30s)
- "Result: drift caught while it's still correctable, the alert says which knob to turn — and the operator still trusts it because it hasn't cried wolf. The prevented loss is the scrapped lot that never happened."

## Beat 5 — Defend under push-back (~2–3 min)
Answer these out loud as if an interviewer just asked (full versions in `WHITEBOARD-DRILL.md`):

1. **"The black box benchmarks higher — why ship the worse one?"**
   On-floor metric is acted-on alerts, not AUC. And here's my **reversal condition**: if a black box gave per-feature attributions an operator could act on *and* beat rules-plus-trend on acted-on-alert precision in a way that survives the trust test — I'd switch. Naming that is what makes it judgment, not dogma.

2. **"WE rules are from 1956 — where's the AI?"**
   The rules *are* deterministic if-logic, on purpose — that's the explainability. The only fitted piece is the time-to-breach forecast: a rolling least-squares slope plus a t-test. Cause attribution is a lookup. I won't dress up `x > 3σ` as machine learning — over-claiming is the red flag.

3. **"Justify the threshold with a number."**
   Cost asymmetry: ~\$8k lot vs ~\$10 false alarm — but the real ceiling is the trust budget (~1–2/shift), so I set the gate at a ~3σ slope significance. *(Honest caveat: my dollar figures are illustrative; on real lines I'd pull the actual scrap cost and investigation time.)*

4. **"It's synthetic data — how do you know it works on messy plant data?"**
   It doesn't prove field-readiness — only the method. First on real data: re-fit limits on a real in-control window, then measure the false-alarm rate on real *quiet* data before trusting any alert. Real failure modes I'd expect: sensor dropouts, clock skew, mislabeled tags, recalibration step-changes, a stuck sensor reading flat.

5. **"Operator ignores the alert and scraps anyway — whose fault?"**
   The system owns signal quality and clarity — name the variable, the cause, the action. If *actionable* alerts get ignored, that's a process/training gap. But burying the true signal under false alarms *is* a design failure — which is exactly why the tuning in #3 matters. The human owns the action; I own making the right action obvious.

## Beat 6 — Close (~15s)
- Point at `DECISIONS.md`: "The surviving reasoning lives here." Then land the line:
- *"I shipped the model an operator will act on at 2 a.m. — not the one that wins a benchmark."*

---

### After recording
- [ ] Export the MP4 / get the Loom link.
- [ ] Add it to the README "Links" and `DECISIONS.md` → Whiteboard session → Recording.
- [ ] Embed on hector-garza.com.
- [ ] Confirm a stranger can watch it + read `DECISIONS.md` and explain the explainable-detector choice (the M7 acceptance).
