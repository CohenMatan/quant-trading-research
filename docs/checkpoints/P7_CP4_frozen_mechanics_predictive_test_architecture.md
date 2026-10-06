# P7-CP4 — Frozen Mechanics and Predictive-Test Architecture

- **Status:** design checkpoint, 2026-10-06. Owner decision D175; this report is D176.
- **Scope:** everything is frozen and pinned before any real future return exists. No real future return, IC, score-band return or portfolio was computed. The only returns used are synthetic (power and null calibration).
- **Frozen specification:** `research/phase7/P7_predictive_spec.md` v1, SHA-256 `389f9364…2bd9`, pinned in `qresearch.p7pred` at commit `4c497df` (test `tests/test_p7_pred_spec.py`).

## The answer in brief

- **Score, data and mechanics are frozen exactly as the owner decided**, with the 20% grown-winner rule defined for the portfolio stage only.
- **The predictive test (H022) asks one question:** does a higher frozen Score v1 rank higher one-month total shareholder return among the eligible stocks? It is tested with:
  - one primary statistic: the Newey-West t-statistic of the monthly Spearman IC over 83 non-overlapping months, 2011-01-31 → 2017-11-30;
  - four gates (significance at one-sided 1% against a 5,000-world identity-tethered null, an 80+ group economic floor of +3% a year, monotonicity, stability).
- **Synthetic power (real score tables, synthetic returns):**

| Power | IC | 80+ group excess |
|---|---|---|
| 50% | ≈ 0.033 | ≈ +6.3% a year |
| 80% | ≈ 0.047 | ≈ +10.2% a year |

  The full procedure's false-promotion rate is 0.3%.
- **Recommendation: GO**, for the one real evaluation, with the limitation stated plainly: an edge much below about 4–6% a year in the 80+ group would usually go undetected.

## 1. Frozen decisions (items 1–17)

| # | Item | Frozen |
|---|---|---|
| 1 | P7-CP3R | Approved: "MECHANICS CONFIRMED — READY TO FREEZE FOR PREDICTIVE TEST DESIGN" (D175) |
| 2 | Revenue baseline | The company's revenue True TTM recorded **live** at the month-end review of the same month one year earlier, for every company in the PIT store, whether eligible or not. No recomputation, no nearby date, no interpolation, no later filing. No valid recorded value means H2 (`qr_p7_export.RevenueLedger`, hash `40e1410e…`) |
| 3 | CIK | **Option A:** reject only when a registrant change is known (CIK known at both dates and different). An unknown CIK never rejects by itself (`baseline_check`) |
| 4 | Security life | The baseline requires the security's current price life to have started on or before the baseline review (D167). Every component quarter must be usable by then (checked in-host) |
| 5 | Score v1 | `qr_p7_score.py` `84b67317…` and `qr_p7.py` `86abb2b2…`: byte-identical to the P7-CP2 pins. Technical 40 / Fundamental 45 / Sector 15; features, bands, weights, lookbacks, sector and volatility definitions, H1–H7 unchanged except the approved H2 baseline |
| 6–8 | Entry / exit / buffer | **80 / 70 / 5** |
| 9 | Positions | **K = 10**, 10% maximum initial position |
| 10 | Relaxation ladder | **None**; cash allowed |
| 11 | Regime limits | **STRONG 10 / NORMAL 8 / WEAK 5 / RISK_OFF 2**. Lowest-ranked holdings exit first at the monthly review |
| 12 | Sector cap | At most **3** per PIT FF12 sector; skip and take the next candidate |
| 13 | Share classes | One company, one exposure. No second class of a held company; a held class is kept on its own score and never switched for liquidity |
| 14 | Weekly check | Hard disqualifiers of holdings only, sell only; cash until the next monthly review |
| 15 | Tie-break | Total, then Fundamental subtotal, then Technical subtotal, then ADV20, then security id |
| 16 | Grown-winner cap | **20%** (`qr_p7_mech.grown_winner_trims`): at each monthly review, valued at that close, trim any holding above 20% of equity back to 20% at the next open. A ceiling, never a target. **Portfolio stage only:** it has no role in the signal validation, which holds no positions |
| 17 | Costs | $7 per buy, $7 per sell, 0.10% slippage per side; $100K primary, $200K sensitivity; mechanical estimates 0.80% / 0.64% a year (P7-CP3R) |

The mechanics are implemented in `qr_p7_mech.py` (`838ffce8…`; the P7-CP2 `plan_review` remains only as a superseded reference). They are used **only** at a later portfolio stage, and only if H022 qualifies.

## 2. The predictive test (items 18–29)

**18 — Question.** Do eligible stocks with a higher frozen Score v1 at a monthly review earn a higher total shareholder return over the following month than lower-scoring eligible stocks? The score is tested as frozen. There is no refit, reweighting or component mining, and no Score v2.

**Population.** At each review: the eligible, fully scorable stocks (data-v1 universe, kept share class, no hard disqualifier). That is 196–612 per review, mean 479; the fewest are in autumn 2011, when many stocks carried H6.

**19 — Primary response.**
- The stock's one-month total shareholder return minus the equal-weighted mean of the population's returns over the same window.
- This removes the market and isolates selection.
- SPY is not used: it would mix in size and beta.
- Ranks, and therefore the IC, are unchanged by the demeaning; the economic and monotonicity statistics use the demeaned values.

**20 — Primary horizon: one month, non-overlapping.**
- From the open after review t to the close of the next review session.
- **Why:**
  - the decision is re-made monthly;
  - high scores are short-lived (median spell 1 month);
  - median holding is about 2 months but each month is a fresh decision;
  - one month gives 83 independent responses with simple inference.
- **Diagnostics, never gates:** 2 and 3 months. These overlap, so they use Newey-West lag h.
- **Overlap and dependence:**
  - The unit of inference is the monthly cross-sectional IC, never the stock-month.
  - Repeated stocks, persistent scores, common market shocks and sector correlation all enter through the time series of ICs.
  - Newey-West lag 2 covers mild autocorrelation from score persistence.
  - The tethered null carries the same dependence (item 31).

**21 — Timing.**
- Score_i(t) uses only data available on the selection day reflecting session t (frozen store and timing rules).
- The response starts at the **next session's open**, never at the close of t.

**Decision dates:** 2011-01-31 → 2017-11-30 (83).
- The first has a valid 12-month revenue baseline (ledger from 2010-01).
- The 2017-12 review is unused because its response would reach into 2018.
- No price after 2017-12-29 is requested.

**22 — Corporate actions and delistings** (`qr_p7_pred.response`):
- **Total return** = close × multiplier at exit ÷ open × multiplier at entry − 1. The multiplier is QuantConnect's own split feed × dividend feed (dividends, specials and spin-offs reinvested at the reference price), the H019 construction.
- **Delisting, acquisition or halt before the window ends:** exit at the **last real close**, then cash.
- **No bar after t:** return 0.
- **An unverified split inside the window:** excluded and counted.
- Every status is counted, by quintile and year. Nothing is silently dropped.
- **Disclosed limitation:** QuantConnect has no delisting return, so a rare bankruptcy may be overstated.

**23 — Primary statistic:** t_IC = mean monthly Spearman IC between score and response ÷ its Newey-West standard error (lag 2).

**24 — Economic statistic:** the 80+ group's demeaned return, averaged over the months with at least one 80+ stock and annualised.
- It must be **≥ +3.0% a year**: about 4× the 0.8% / yr mechanical cost, and the H020 precedent.
- The 80+ group is the frozen entry population, not a threshold choice.

**25 — Monotonicity:**
- Score quintiles each month, using the frozen `qr_p7_score` average-rank convention.
- Mean demeaned return per quintile over all months.
- Spearman(quintile 1–5, mean) **≥ 0.90** and Q5 > Q1.

**26 — Stability:**
- mean IC > 0 in **both halves** (dates 1–41 and 42–83);
- no calendar block (2011–12, 2013–14, 2015–16, 2017) contributes more than **50%** of the summed IC.

**27 — Sector diagnostic (non-gating):** the IC on the FF12 sector-demeaned response. If its t-statistic is below half of t_IC, the result is flagged "substantially sector-driven".

**28 — Regime diagnostics (non-gating):** mean IC by STRONG / NORMAL / WEAK / RISK_OFF with month counts. Never used to rescue a failure.

**29 — Incremental information (the single secondary test; non-gating):**
- A monthly Fama-MacBeth rank regression of the sector-demeaned response on rank(score), rank(12-1 momentum) and rank(log PIT market cap).
- Reported: the score slope, its t-statistic and its null quantile.
- Controls: the market is removed by the demeaning and sectors by the sector demeaning; size and momentum enter as regressors.
- No component or feature-level statistic is computed.

## 3. Null, threshold and gates (items 30–34, 40)

**30 — Primary null:** the H020 identity-tethered within-date permutation (`qr_p7_pred.Tether`, one stratum, no self-matching).
- Each stock receives the score side (score, quintile, 80+ flag) of a partner stock and keeps that partner while both remain in the population.

**31 — Why it preserves the relevant dependence:**
- Each date's exact score distribution is kept (80+ counts, quintile counts).
- Each stock's null score history is a real score history, so persistence and autocorrelation are kept.
- The real returns are untouched: market shocks, sector co-movement, volatility differences, the changing universe, delistings and the monthly calendar.
- Only the link between a stock's own score and its own future return is broken.
- **Rejected alternatives:**
  - a global shuffle, which destroys persistence and dates;
  - a stratified tether, which made the H020 null too narrow.
- Tests confirm an exact within-date permutation, no self-match, partners persisting more than 80% month to month, and determinism by seed.

**32 — Full-procedure null:** every world recomputes the whole chain (IC series, t_IC, 80+ excess, quintiles and monotonicity, halves and blocks, diagnostics). The false-promotion rate of all four gates together is reported.

**33 — Threshold:**
- **One-sided 1%:** c_IC = the 50th largest of 5,000 null t_IC, never below 2.326 (the normal 1% quantile, which guards against a too-narrow null).
- H022 is the programme's 22nd hypothesis. 1% is kept, not loosened. It is the H019–H021 standard, and the procedure's synthetic false promotion is 0.3%.
- Later safeguards remain: 2018–2021 internal out-of-sample and the locked Holdout.
- The owner may choose a stricter level (e.g. 0.5%) **before** the null is computed.

**34 — Null worlds:** **R = 5,000**, seeds 1–5,000, in batches E023-01 … 05 of 1,000.

**40 — Exact gates (all required):**

| Gate | Rule |
|---|---|
| G1 | t_IC > c_IC and mean IC > 0 |
| G2 | 80+ excess ≥ +3.0% a year |
| G3 | Monotonicity ≥ 0.90 and Q5 > Q1 |
| G4 | Both halves positive and largest block share ≤ 50% |

**Outcomes:**
- **QUALIFIED:** the owner may authorise the portfolio-stage design (frozen Part B mechanics, 2011–2017), then the 2018–2021 internal out-of-sample.
- **NOT QUALIFIED:** H022 is rejected and preserved as tested; no rescue.

## 4. Synthetic power study (items 35–39)

**35 — Design** (`research/phase7/P7_power.py` → `P7_power.json`, seed base 20261006, 4 workers, 8 minutes). It uses the **real** E993-02 score tables, which contain scores and no prices:
- 83 dates and 196–612 stocks per date;
- the real score distribution and its persistence;
- the changing universe;
- the real PIT sectors, volatility bands, momentum bands and fundamental subtotals.

**Synthetic returns:**
- market (0.8% ± 3.5% a month) × beta (1 ± 0.25);
- 16 sector factors (± 2.5%);
- three zero-mean style factors that the score itself loads on (momentum, low volatility, quality). They are calibrated so the null monthly IC has a standard deviation ≈ 0.09–0.10, typical of composite equity factors;
- fat-tailed t(5) idiosyncratic noise by the stock's real volatility band (4.5–8.5% a month).

**Planted edge:** κ per standard deviation of the normal score of the stock's score rank.

**Procedure:**
- c_IC from 2,000 null worlds over 10 independent null datasets;
- the full-procedure false-promotion rate on 1,000 held-out null worlds;
- 200 datasets per κ;
- three noise scenarios.

**38 — False positives (main scenario):**
- synthetic c_IC = 2.50 (null t_IC mean −0.04, standard deviation 1.03);
- the significance gate alone passes 0.9% of held-out null worlds, and **the full procedure 0.3%**;
- with no planted edge, **0 of 200** real-assignment datasets passed.
- Gate pass rates under the null:

| Gate | Pass rate |
|---|---|
| G1 | 0.9% |
| G2 | 25% (the 80+ group averages about 7 stocks, so it is noisy) |
| G3 | 4.6% |
| G4 | 5.1% |

**36–37, 39 — Detectable effects:**

| Noise scenario (null IC sd) | Power | IC | 80+ excess / yr | Q5 − Q1 / yr |
|---|---|---|---|---|
| **Main (≈ 0.09)** | **50%** | **0.033** | **+6.3%** | +7.5% |
| | **80%** | **0.047** | **+10.2%** | +10.6% |
| Optimistic (≈ 0.06) | 50% | 0.027 | +4.9% | +6.0% |
| | 80% | 0.040 | +8.3% | +9.0% |
| Pessimistic (≈ 0.12) | 50% | 0.040 | +8.7% | +9.4% |
| | 80% | 0.056 | +12.1% | +13.1% |

**Pass probability by planted edge (main scenario):**

| Planted edge | Pass probability |
|---|---|
| IC 0.016 (80+ excess ≈ +3.6% / yr) | 12% |
| IC 0.030 (≈ +5.3% / yr) | 42% |
| IC 0.045 (≈ +9.9% / yr) | 79% |
| IC ≥ 0.06 | ≥ 94% |

- The significance and stability gates bind; the economic gate never binds at these effects.
- **Economic reading.** The test reliably finds an 80+ group edge of about 10% a year and has even odds at about 6%. Edges of 2–4% a year, which would still be economically useful after about 0.8% costs, are usually missed.
- **The translation assumes a linear relation in the score's normal rank.** If the real relation is concentrated at the top, the 80+ excess for a given IC would be higher, and the reverse if it is diffuse.

## 5. Integrity and canary plan (item 41)

**Implemented and passing:**
- `tests/test_p7_pred.py`: A–G, the gates, the critical-value floor and the grown-winner rule;
- `tests/test_p7_cp3r.py`: ledger A–E;
- `tests/test_p7_export.py`: host-level rescue, life, eligibility independence and determinism.

| Canary | What it checks |
|---|---|
| A. Future-data invariance | Later prices cannot change any score input at t; a later filing or restatement cannot change a recorded baseline |
| B. Truncation | Data truncated at t gives identical score inputs and baseline |
| C. Response timing | The response starts at the open of t + 1; no price at or before t (including the close of t) affects it; the score is computed independently of any response price |
| D. Corporate actions | A split, a dividend at its reference price, a delisting (last real close) and "no bar" reproduce hand-computed totals; an unverified split is excluded |
| E. Null determinism | Same seed gives the same result; an exact permutation; no self-match; persistent partners |
| F. Positive control | A planted edge passes all gates |
| G. Negative control | Independent scores almost never qualify (synthetic false promotion 0.3%) |

**Before the real run (next stage), the in-host canary X994 adds:**
- a fresh-history independent recomputation of responses on a deterministic sample (as X992);
- response status counts;
- score fingerprint checks.
It computes no IC and no gate.

## 6. Frozen artefacts, hashes and commit (items 42–43)

| Artefact | File | SHA-256 (first 16) |
|---|---|---|
| Specification | `research/phase7/P7_predictive_spec.md` | `389f9364541588f7` |
| Hypothesis | `research/hypotheses/H022.md` | `54683a81ae334cc5` |
| Result template | `research/phase7/P7_CP5_result_template.md` | `ffd3ffeb8c233bca` |
| Score v1 | `src/qresearch/lean/qr_p7_score.py`, `qr_p7.py` | `84b67317023683da`, `86abb2b2e9284f1d` |
| Revenue store / ledger | `qr_p7_export.py`; PIT store `qr_fundamentals.py` (data freeze v1) | `40e1410ef00a7e1c`; `0774343f24820ce4` |
| Mechanics planner | `qr_p7_mech.py` | `838ffce8d9ab5fd3` |
| Response, statistics, gates, null | `qr_p7_pred.py` (+ `qr_h020_stats.py` tether, `qr_xs.py`, `qr_xs_panel.py`) | `bc6fd8e83e7c105e` (`426d37218f8a2770`, `bd69bc6ae5e0598e`, `4dd5f6df09d9cad3`) |
| Export host (score pipeline) | `strategies/X993_p7_score_mechanics_export/main.py` v1.1 | `912d841f1d1df36f` |
| Power study and result | `research/phase7/P7_power.py`, `P7_power.json` | `17952573cbad5874`, `f45d5145322f314b` |
| Tests | `tests/test_p7_pred.py`, `tests/test_p7_cp3r.py` | `e1c070bcc08897e1`, `912861b07ea2fb52` |

- **Pins:** `src/qresearch/p7pred.py`, checked by `tests/test_p7_pred_spec.py`; c_IC is deliberately **not** pinned yet.
- **Freezing commit:** `4c497df65436066f6126d8f221510d0758e83d79`.
- **Seeds:** null worlds 1–5,000; power study seed base 20261006.

## 7. Confirmations (items 44–49)

| # | Confirmation |
|---|---|
| 44 | **No real future return** was computed or loaded. The response module ran only on synthetic arrays; the power study used real scores with synthetic returns |
| 45 | **No real IC**, 80+ return or score-band return was computed |
| 46 | **No portfolio**, order, backtest, CAGR, Sharpe, drawdown, terminal wealth, win rate, alpha or SPY comparison. No QuantConnect run in P7-CP4 |
| 47 | **2018–2021 untouched** |
| 48 | **Holdout untouched** |
| 49 | **Nothing purchased** |

## 8. Recommendation (item 50): GO, for the one real predictive evaluation

**Why GO:**
- The design answers the owner's question directly and without discretion: everything from the response to the threshold is frozen and pinned.
- The false-promotion rate is very low (0.3%).
- The test has even odds at an 80+ edge of about 6% a year and 80% power at about 10% a year. Those are the sizes at which a 10-stock, about 70%-invested portfolio would clearly survive its about 0.8% costs.
- A failure ends Phase 7 cleanly.
- A pass is still followed by a portfolio-stage design, the untouched 2018–2021 internal out-of-sample and the locked Holdout.

**The honest limitation, stated before any data:**
- An edge of 2–4% a year would usually be missed, so a NOT QUALIFIED verdict would not prove the score is useless.
- Given the programme's history (12-1 momentum and GP/A did not reproduce in this universe), the prior chance of passing is modest.
- The test is cheap: one canary, five null batches and one real run of about 15 minutes each.

## 9. Owner decisions required before the real evaluation (item 51)

1. **Approve the frozen specification v1** as written: one-month horizon, demeaned TSR, t_IC primary, gates G1–G4, diagnostics, tethered null, R = 5,000, one-sided 1% with the 2.326 floor.
   - Alternatively, choose a stricter significance level (e.g. 0.5%) **now**, before any null is computed.
2. **Approve building host S023 / canary X994.** This is plumbing only: the X993 v1.1 score pipeline plus the frozen `qr_p7_pred` in-host, with only statistics exported. Then run, in order:
   - canary X994 (no IC);
   - null batches E023-01 … 05;
   - pin c_IC and the null-result hash in `qresearch.p7pred` and commit;
   - one real evaluation E023-06 from a clean committed tree;
   - P7-CP5 using the frozen template, then STOP.
3. **Confirm the disclosed conventions:**
   - last-real-close for delistings (no delisting-return data);
   - exclusion of the rare unverified-split windows;
   - the 80+ excess averaged over the months with at least one 80+ stock.

**STOP.** No real return, IC, 80+ performance or portfolio. No tuning of the score, 80 / 70 / 5, K, the sector cap or the regime limits. 2018–2021 and the Holdout untouched. Waiting for explicit owner approval.
