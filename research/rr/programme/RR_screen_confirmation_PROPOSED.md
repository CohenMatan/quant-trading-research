# RR programme — candidate screen and confirmation rules (PROPOSED, ready to freeze)

**Status:** PROPOSED under D265 (RR4). **Not frozen.** On owner approval, this file is renamed `RR_screen_confirmation.md`, given status FROZEN, and its SHA-256 is pinned in code and tests before any strategy run. After that, no rule here changes because of any strategy result.

**Written before any new strategy result.** No RR strategy has been registered, built or run.

**Sources:**
- RR2 §5–§7 (D262; architecture approved in principle, D263);
- Amendment 3 (`research/phase2/P2_amendment3_spec.md`, frozen D121; constants in `qresearch.wealth`);
- D226 (long-horizon objective);
- RR3 / RR4 (universe limits, no independent historical period).

## 1. Evidence labels (used in every report)

| Label | Meaning |
|---|---|
| **DEVELOPMENT — EXPOSED** | Any result on 2010–2021. That period has been used by 30 hypotheses. A pass means "worth a further look", never "validated" (D261) |
| **HOLDOUT — NOT FALSIFIED** | Passed the one-time Holdout gates (§5). A falsification check on 4.7 years, not proof |
| **FORWARD — TRACKED** | Data after the freeze timestamp (D094 category F), after owner approval |
| **INDEPENDENT HISTORICAL CONFIRMATION** | **Not available.** QuantConnect has no valid 1999–2009 universe (RR3 W0 = FAIL, D265). No report may claim it |

## 2. Scope and run budget (per tranche)

- At most 3 pre-registered hypotheses per tranche. Tranche size m is fixed when the owner approves the tranche, before any result.
- Per hypothesis:
  - one primary specification, $100,000 account;
  - two pre-registered sensitivity replays: 20 bps slippage per side, and a $200,000 account. They never select, decide or rescue;
  - at most 3 cloud runs (primary, determinism rerun, one documented infrastructure retry);
  - no post-result variant, re-tuning or rerun. A failed hypothesis is closed.
- Costs and constraints unchanged:
  - $7 per order and forced-liquidation fee (D039 / D049); 10 bps slippage per side (D024);
  - at most 15 positions, $5,000 minimum position (D044); 10% maximum initial position;
  - D051 no borrowing, 15% gap reserve; long-only, no leverage; signal at T, execution at the T+1 open or later.
- Universe: the approved rule (US common, NYSE / Nasdaq / AMEX, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) on QuantConnect's vendor market cap, within the window the owner sets after RR4 §2.
- **Development window:** 2010-01-04 → 2021-12-31 by default. It is replaced by the owner's universe decision (RR4 §2.6) before the first strategy run, never after a result.

## 3. Stage D1 — "Promising" (P1–P6, unchanged from RR2)

All must pass on the primary run.

| | Criterion (exact) |
|---|---|
| P1 | Terminal wealth > SPY total-return buy-and-hold, same capital and dates, after costs (Amendment 3 W1) |
| P2 | g / SE ≥ **1.0**, with g and SE exactly as Amendment 3 W2 (daily log wealth ratio; SE = max(iid, stationary bootstrap, q = 1 − 1/126)) |
| P3 | CAGR > the equal-weight control of the same universe **and** > at least 4 of 5 random-selection controls (same universe, positions, schedule, costs and mechanics; seeds fixed in the hypothesis spec) |
| P4 | Σ d_t > 0 and no calendar two-year block (2010–11, …, 2020–21; a partial block counts) contributes more than 50% of it (Amendment 3 R3) |
| P5 | P1 still holds at 20 bps slippage per side |
| P6 | Up-capture ≥ 0.85 **or** down-capture ≤ 0.85, on calendar-month returns vs SPY: up-capture = mean strategy return in SPY-up months / mean SPY return in those months; down-capture likewise for SPY-down months |

**Unevaluable criterion = fail.** A D1 pass is reported as DEVELOPMENT — EXPOSED and STOPS for the owner.

## 4. Stage D2 — "Development-qualified" (new; justified below)

Needed before any candidate may ask for the Holdout. All on the same development data:
- Amendment 3 §3 in full: W1, W2, W3, R1, R2, R3, R4, then G4′ (perturbations fixed in the hypothesis spec).
- **W2 with multiplicity across the tranche (Holm):** with p_k = 1 − Φ(g_k / SE_k) and α₀ = 1 − Φ(2.15) = 0.0158, sort the tranche's D1-passing hypotheses by p; the k-th smallest passes only if p_(j) ≤ α₀ / (m − j + 1) for every j ≤ k. Equivalent thresholds: m = 1 → 2.15; m = 2 → 2.41 then 2.15; m = 3 → 2.57, 2.41, 2.15. Hypotheses that fail D1 still count in m.

**Why D2 is added (decided before any result):** RR2 placed the strict W2 test on an independent 1999–2009 confirmation window. That window does not exist (RR3 W0 = FAIL). The Holdout under Amendment 3 §4 tests wealth and drawdown only, and over 4.7 years a candidate with no edge beats SPY roughly half the time. Without D2, nothing in the chain would test the strength of the evidence. D2 moves Amendment 3's existing evidence test to the development data, labelled as exposed. P1–P6 are unchanged.

**Honest power (Amendment 3 §7 calibration):** the full framework passes about half the time only at a true edge of ≈ 6% a year over SPY (20 positions, 12 years). A 2–3% edge will usually fail. That is accepted.

## 5. Stage C1 — Holdout (once)

- At most **one** candidate per tranche, the D2 pass with the smallest W2 p-value. It needs written owner approval at CP5, recorded in `HOLDOUT_UNLOCK.md`.
- Window 2022-01-01 → 2026-08-31, run once with the frozen code. Amendment 3 §4 unchanged:
  - HO-W: CAGR > CAGR(SPY);
  - HO-R: MaxDD ≥ MaxDD(SPY) − 10 points;
  - defensive / market-timing exception: CAGR > CAGR(SPY) also over 2023-01-01 → 2026-08-31 alone.
- Reported, not gated: W2 statistic, W3, R2, P6 capture, the 2022 / 2023–2026 split.
- **The same run carries the universe audit aggregates for 2022–2026** (missing-cap share, no-fundamentals count, exit rates where assessable). They cannot be measured before unlocking without reading Holdout data.
- Outcome: pass = HOLDOUT — NOT FALSIFIED; fail = closed, and the strategy is never modified.

## 6. Stage C2 — forward tracking (category F)

- Starts only after a full freeze and owner approval. Same code, same rules.
- Reviews at +12, +24 and +36 months after the freeze: HO-W and HO-R on the forward data alone, reported. The +36-month review is decisive for the research programme: fail = closed.
- A **Production Candidate** status needs, at least: D1, D2, C1 and the +36-month C2 review passed, then a separate owner decision. Research only: no real money is involved in any stage.

## 7. Integrity conditions on every run

1. The host recomputes the RR3 monthly-count digest (category counts at each month-end, X804 definitions). A mismatch with `d0c2f430…` does not change any verdict; it is reported, and the next step is one rerun of the universe audit (aggregate only) before any verdict is accepted.
2. The report repeats the RR3 / RR4 universe limits (missing-cap residue, no-fundamentals population, blank fields, 2021 survivorship not assessable, build / dataset instability).
3. Ledger: every run, including failures, in `experiments/INDEX.csv` and the selection ledger; the tranche's m and every D1 / D2 result go in the final report.
