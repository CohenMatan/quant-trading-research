# RR programme — candidate screen and confirmation rules (v2, READY TO FREEZE)

**Status:** v2 = RR4's v1 with the owner's D267 corrections. **Not yet frozen.**
- On owner confirmation, this file is renamed `RR_screen_confirmation.md` with status FROZEN, and its SHA-256 is pinned in code and tests **before any strategy return is calculated**.
- After that, no rule here changes because of any strategy result.

**Written before any new strategy result.** No RR strategy has been registered, built or run.

**Sources:**
- RR2 §5–§7 (D262; architecture approved in principle, D263);
- RR4 §3 (D266);
- owner D267 (D1 / D2 approved in principle, clarifications A and B, run-budget reconciliation);
- Amendment 3 (`research/phase2/P2_amendment3_spec.md`, frozen D121; constants in `qresearch.wealth`);
- D226 (long-horizon objective).

**Changes from v1:**
- §1 clarification B;
- §5 clarification A (one Holdout candidate for the whole programme);
- §2.2 explicit run budget, including the sensitivity runs;
- §4 G4′ runs listed;
- §8 trial-history ledger.

## 1. Evidence labels and what they do NOT mean (clarification B)

| Label | Meaning |
|---|---|
| **DEVELOPMENT — EXPOSED** | Any result on 2010–2021. That period has been used by 30 hypotheses (H001–H030) and thousands of variants. A pass means "worth a further look", never "validated" (D261) |
| **HOLDOUT — NOT FALSIFIED** | Passed the one-time Holdout gates (§5). A falsification check on 4.7 years, not proof |
| **FORWARD — TRACKED** | Data after the freeze timestamp (D094 category F), after owner approval |
| **INDEPENDENT HISTORICAL CONFIRMATION** | **Not available.** QuantConnect has no valid 1999–2009 universe (RR3 W0 = FAIL, D265). No report may claim it |

**Stated in every report that mentions D1 or D2:**
- D1 and D2 are evaluated on heavily exposed development data.
- Passing either does **not** establish independently validated statistical significance or investable alpha.
- The Holm adjustment in §4 corrects only for the hypotheses of the current tranche. It does **not** erase the programme-wide search history: 30 earlier hypotheses on the same years, listed in the trial-history ledger (§8).
- Any p-value or W2 ratio is therefore reported as a **nominal, tranche-level** figure.

## 2. Scope, constraints and the run budget

### 2.1 Scope and constraints

- At most 3 pre-registered hypotheses per tranche. Tranche size m is fixed when the owner approves the tranche, before any result. **Tranche 1: m = 1 (H031, K1), unless the owner adds another before any H031 result.**
- Per hypothesis:
  - one primary specification;
  - no post-result variant, re-tuning or rerun beyond §2.2;
  - a failed hypothesis is closed.
- Costs and constraints unchanged:
  - $7 per order and forced-liquidation fee (D039 / D049); 10 bps slippage per side (D024);
  - at most 15 positions, $5,000 minimum position (D044); 10% maximum initial position;
  - D051 no borrowing, 15% gap reserve; long-only, no leverage; signal at T, execution at the T+1 open or later.
- **Universe:** the approved rule (US common, NYSE / Nasdaq / AMEX, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) on QuantConnect's vendor market cap.
- **Window:** set by the owner after the UR-1 audit (RR5), before the first strategy run, and never after a result. Default 2010-01-04 → 2021-12-31.

### 2.2 Cloud-run budget (closed list: nothing else is authorised implicitly)

| Run | Purpose | When | Counts as |
|---|---|---|---|
| C | Event / plumbing canary: aggregate counts and timing checks only, no returns | after the universe decision is accepted (D267 item 3) and with its own approval | infrastructure |
| R1 | Primary: $100,000, 10 bps. Carries in-host SPY, equal-weight and 5 random controls (§3 P3) as shadow books | on explicit owner approval of the strategy run | research |
| R1d | Determinism rerun of R1 (identical code; the trade-list and equity hashes must match) | with R1 | research (no new information) |
| R2 | Sensitivity: 20 bps slippage per side. Needed for P5 and equal to G4′'s 2× slippage | with R1 | sensitivity |
| R3 | Sensitivity: $200,000 account (reported; never selects, decides or rescues) | with R1 | sensitivity |
| G1–G6 | Amendment 3 G4′: the 6 perturbations fixed in the hypothesis spec | **only** if D1 and the rest of D2 pass, **and** after a separate owner approval | robustness |
| retry | At most **one** documented infrastructure retry per hypothesis, in total, of any run above | after a documented failure | — |

- **Per hypothesis:** at most 5 runs before D1 (C, R1, R1d, R2, R3), plus 6 conditional G4′ runs, plus 1 retry.
- **Tranche ceiling:** 12 runs before any G4′ run, including the platform canary.
- **No other run is authorised by this protocol.** In particular: no rerun with changed code or data, no other cost or account variant, no window change.

## 3. Stage D1 — "Promising" (P1–P6, unchanged)

All must pass on R1, except P5 on R2.

| | Criterion (exact) |
|---|---|
| P1 | Terminal wealth > SPY total-return buy-and-hold, same capital and dates, after costs (Amendment 3 W1) |
| P2 | g / SE ≥ **1.0**, with g and SE exactly as Amendment 3 W2 (daily log wealth ratio; SE = max(iid, stationary bootstrap, q = 1 − 1/126)) |
| P3 | CAGR > the equal-weight control of the same universe **and** > at least 4 of 5 random-selection controls (same universe, positions, schedule, costs and mechanics; seeds fixed in the hypothesis spec) |
| P4 | Σ d_t > 0 and no calendar two-year block (2010–11, …, 2020–21; a partial block counts) contributes more than 50% of it (Amendment 3 R3) |
| P5 | P1 still holds on R2 (20 bps slippage per side) |
| P6 | Up-capture ≥ 0.85 **or** down-capture ≤ 0.85, on calendar-month returns vs SPY: up-capture = mean strategy return in SPY-up months / mean SPY return in those months; down-capture likewise for SPY-down months |

**Unevaluable criterion = fail.** A D1 pass is reported as DEVELOPMENT — EXPOSED and STOPS for the owner.

## 4. Stage D2 — "Development-qualified" (on the same exposed data)

Needed before any candidate may ask for the Holdout:
- Amendment 3 §3 in full on R1 / R2: W1, W2, W3, R1, R2, R3, R4.
- Then G4′, from G1–G6 and R2.
- **W2 with Holm across the tranche:** p_k = 1 − Φ(g_k / SE_k), α₀ = 1 − Φ(2.15) = 0.0158. Thresholds: m = 1 → 2.15; m = 2 → 2.41 then 2.15; m = 3 → 2.57, 2.41, 2.15. Hypotheses that fail D1 still count in m.
- **Clarification B applies:** D2 is a stricter test on exposed data, not independent significance.

**Why D2 exists (decided before any result):**
- No independent historical period exists.
- The Holdout (§5) tests wealth and drawdown only.
- So the strength of the evidence must be tested before the Holdout is used.

**Honest power:** Amendment 3's full framework passes about half the time only at a true edge of ≈ 6% a year over SPY (20 positions, 12 years). A shorter window needs more.

## 5. Stage C1 — the Holdout (clarification A)

- **The 2022-01-01 → 2026-08-31 Holdout may be used for at most ONE candidate across the entire research programme**, not one per tranche. Once it is opened, it is spent for every later hypothesis.
- **Opening it requires separate, explicit written owner approval** (CP5, recorded in `HOLDOUT_UNLOCK.md`). A D2 pass only allows a request.
- The run uses the frozen code once. Amendment 3 §4 unchanged:
  - HO-W: CAGR > CAGR(SPY);
  - HO-R: MaxDD ≥ MaxDD(SPY) − 10 points;
  - defensive / market-timing exception: CAGR > CAGR(SPY) also over 2023-01-01 → 2026-08-31 alone.
- Reported, not gated: W2 statistic, W3, R2, P6 capture, the 2022 / 2023–2026 split.
- **The same run carries the universe audit aggregates for 2022–2026.** They cannot be measured before opening.
- Outcome: pass = HOLDOUT — NOT FALSIFIED; fail = closed, and the strategy is never modified.

## 6. Stage C2 — forward tracking (category F)

- Starts only after a full freeze and owner approval. Same code, same rules.
- Reviews at +12, +24 and +36 months after the freeze: HO-W and HO-R on the forward data alone, reported. The +36-month review is decisive for the research programme: fail = closed.
- A **Production Candidate** status needs, at least: D1, D2, C1 and the +36-month C2 review passed, then a separate owner decision. Research only: no real money is involved in any stage.

## 7. Integrity conditions on every run

1. The host reports the monthly E counts of the universe. A difference from the UB-1 / SCA-1 snapshot (E804-01 / E805-01) does not change any verdict; it is reported, and one aggregate universe re-check run is requested before any verdict is accepted.
2. Every report repeats the universe limits accepted with the UR-1 decision (RR3 / RR4 / RR5): missing-cap residue, no-fundamentals population, blank fields, 2021 survivorship not assessable, build / dataset instability.

## 8. Trial-history ledger (kept visible)

- Every RR hypothesis, specification, run (including failures, retries and sensitivity runs) and stage outcome is entered in `research/rr/RR_LEDGER.md` **before** its result exists, and in `experiments/INDEX.csv`.
- The ledger opens with the programme-wide history: H001–H030 on 2010–2021, none qualified.
- Every D1 / D2 report states:
  - the tranche size m;
  - the cumulative number of hypotheses tested on 2010–2021;
  - the number of RR runs used.
