# Phase 7 — Frozen Score / Mechanics and Predictive-Test Specification (H022)

- **Status:** FROZEN v1 (P7-CP4, 2026-10-06), written before any real future return, IC or score-band return was computed. Hash-pinned with every module it names in `qresearch.p7pred` (`tests/test_p7_pred_spec.py`).
- **Authority:** owner D169–D175.
- **Change rule:** nothing here changes after any real future return is computed. A genuine bug means STOP, document it, ask the owner, and issue v2 before the real evaluation. After the real evaluation, nothing changes at all.

## Part A — Frozen data and score

1. **Data infrastructure:** frozen v1 (`research/phase2/data_freeze_v1.json`, `qresearch.datafreeze`):
   - the PIT fundamentals layer `qr_fundamentals` (availability = filing + 1 day, estimated dates + 90, quarantine, restatement blocks, SEC timing holds, field releases, 200-day freshness);
   - the SEC correction layer;
   - SEC SIC at filing.
2. **Universe:** data-v1 at each review: US common stock, NYSE / Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M.
3. **Score v1:** `src/qresearch/lean/qr_p7_score.py` + `qr_p7.py`, byte-identical to the P7-CP2 pins (`qresearch.p7score`; QuantConnect appends one newline on storage). Unchanged:
   - Technical 40, Fundamental 45, Sector 15;
   - features, quintile bands, weights, lookbacks, the FF12 sector breadth context, 60-day total-return volatility;
   - hard disqualifiers H1–H7.
4. **Revenue baseline** (D173 / D175; `qr_p7_export.RevenueLedger` and `baseline_check`, X993 v1.1):
   - For a review in calendar month M of year Y, the baseline is the company's revenue True TTM recorded **live** at the month-end review of month M, year Y − 1, from the frozen PIT store as it existed then, for every company in the store whether eligible or not.
   - It is never recomputed. No nearby date, no interpolation, no later filing.
   - No valid recorded value means H2.
5. **CIK Option A:** reject a baseline only when the SEC registrant CIK (PIT SIC table) is known at both dates and differs. An unknown CIK never rejects by itself.
6. **Security life** (D167): the security's current price life must have started on or before the baseline review session, else H2. Every component quarter must be usable on or before the baseline selection day (checked in-host).
7. **One share class per company:** the class with the highest PIT ADV20 (then the smallest id) is scored. Other classes are scored with the class substituted, used only for a held class (Part B).

## Part B — Frozen portfolio mechanics (used only at a later PORTFOLIO stage, if H022 qualifies)

Implemented in `src/qresearch/lean/qr_p7_mech.py` (the P7-CP2 `qr_p7_score.plan_review` is a superseded reference).

| Rule | Frozen value |
|---|---|
| Review | Monthly, at the last session of each calendar month; orders at the next session's open |
| Entry / exit / replacement buffer | **80 / 70 / 5**. Exit when the score is < 70; replace only if candidate ≥ held + 5 |
| Maximum positions | **K = 10** |
| Position size at entry | **10%** of equity (maximum initial position; D051 reserve rules) |
| Relaxation ladder | **None**. Cash when fewer than K stocks score ≥ 80 |
| Regime position limits | **STRONG 10, NORMAL 8, WEAK 5, RISK_OFF 2**. When holdings exceed the limit at a monthly review, the lowest-ranked holdings exit first. The regime never changes a score or the ordering |
| Sector cap | At most **3** holdings per PIT FF12 sector. A candidate from a full sector is skipped and the next-ranked one taken |
| Ranking and tie-break | **Total, then Fundamental subtotal, then Technical subtotal, then PIT ADV20, then security id** |
| Share classes | One company, one held exposure. No second class of a held company. A held class is evaluated on its own score and never switched for liquidity; it is sold only if it becomes ineligible or disqualified |
| Weekly check | Hard disqualifiers of holdings only, sell only. The freed capital stays in cash until the next monthly review (no intra-month entries) |
| Grown-winner cap | **20%** of equity (`grown_winner_trims`). At each monthly review, valued at that session's close, a holding above 20% is trimmed back to 20% at the next open. A ceiling, never a target: no trimming between 10% and 20% and no top-up. **Portfolio stage only; irrelevant to the signal validation (Part C)** |
| Costs | $7 per buy and per sell; 10 bps slippage per side; $100K primary, $200K sensitivity; no leverage. P7-CP3R mechanical estimate: 0.80% / 0.64% a year |

## Part C — The predictive test H022 (signal validation; no portfolio)

### C1. Question and population

**Question:** do eligible stocks with a higher frozen Score v1 at a monthly review earn a higher subsequent total shareholder return than lower-scoring eligible stocks?

**Population at review t:** the stocks that are eligible and fully scorable:
- data-v1 universe;
- kept share class;
- no hard disqualifier H1–H7.

This is exactly the set the frozen planner ranks: 196–612 stocks per review, mean 479. The fewest are in autumn 2011, when the sell-off put many stocks in a broken trend (H6).

### C2. Decision dates (development window, mechanical)

- **83 dates:** the month-end review sessions **2011-01-31 → 2017-11-30**.
- The first is the first review with a valid 12-month revenue baseline (the ledger starts 2010-01).
- The 2017-12-29 review has no one-month response inside 2017 and is not used.
- **No price after 2017-12-29 is requested.**

### C3. Primary horizon: one month (non-overlapping)

The response window runs from the open of the first session after review t to the close of the next review session t'. Why one month:
- the score is re-evaluated monthly and the portfolio re-decides every month;
- high scores are short-lived (median spell above 80: 1 month; P7-CP3R);
- one month gives 83 non-overlapping responses, which keeps inference simple and maximises the number of non-overlapping monthly response periods;
- longer horizons mostly measure decayed information.

**Diagnostic horizons (non-gating):** 2 and 3 months, ending at the close of the review two or three months later. These overlap; they use Newey-West lag h and are reported for the real assignment only. Their last decisions are 2017-10-31 and 2017-09-29.

### C4. Timing convention (point in time)

- Score_i(t) uses only data available on the universe-selection day reflecting session t (frozen store and timing rules).
- The response starts at the **next session's open** (t + 1), never at the close of t. No price at or before t enters the response, and no price after t enters the score (canaries A–C).

### C5. Response and accounting (`qr_p7_pred.response`)

**Total shareholder return** = (close × multiplier at exit) ÷ (open × multiplier at entry) − 1. The multiplier is QuantConnect's own split feed × dividend feed, with the factors of events after each row applied to it (the H019 / D148 construction, `qr_xs_panel`):
- dividends, special distributions and spin-off distributions in the dividend feed are reinvested at the reference price;
- splits verified by SCALED_RAW.

**Rules by case:**

| Case | Rule | Status |
|---|---|---|
| Normal | Entry at the first session in (t, t'] with a valid bar; exit at the close of t' | `ok` |
| Delisting / acquisition / halt before t' | Exit at the **last real close** in [entry, t'], cash afterwards | `truncated` |
| No bar at all in (t, t'] | Response **0** (the position could not be opened) | `no_bar_after_t` |
| An unverified split event inside the window | Response excluded (NaN; unreliable) | `unverified_split` |

- Nothing is silently dropped: every status is counted and reported.
- QuantConnect gives no delisting return. The last-real-price rule may overstate the few bankruptcies in a ≥ $2B universe; this is disclosed, and the status counts are reported by score quintile.

**Primary response:** the stock's one-month total shareholder return minus the **equal-weighted mean** of the population's responses on the same window (cross-sectional demeaning).
- This removes the market and isolates selection.
- SPY is not used: it would mix in size and market beta.
- Ranks, hence the IC, are unchanged by demeaning; the economic and monotonicity statistics use the demeaned values.

### C6. Primary statistic

- **IC_t** = the Spearman rank correlation between Score v1 and the response across the population at date t (average ranks for ties).
- The primary statistic is **t_IC** = mean(IC_t) ÷ its Newey-West standard error with **lag 2**, over the 83 dates.
- Lag 2 is used because the responses do not overlap, but persistent scores and common shocks induce mild autocorrelation.
- Stock-months are never treated as independent: the time series of monthly cross-sectional ICs is the unit of inference.

### C7. Gates (all four required; `qr_p7_pred.promotion`)

| Gate | Rule |
|---|---|
| **G1 Significance** | t_IC > c_IC and mean IC > 0. c_IC = max(the 50th largest t_IC among 5,000 null worlds (one-sided 1%), 2.326) |
| **G2 Economic** | the 80+ group's demeaned return, averaged over the months with at least one 80+ stock and annualised (× 12), is **≥ +3.0% a year** (≈ 4× the 0.8% / yr mechanical cost; the H020 precedent). The group is the frozen portfolio entry population, not a search |
| **G3 Monotonicity** | score quintiles of the population each month (`quintile_labels`, the frozen `qr_p7_score` average-rank convention); mean demeaned return per quintile over all dates; Spearman(quintile 1..5, mean) **≥ 0.90** and Q5 − Q1 > 0 |
| **G4 Stability** | mean IC > 0 in **both halves** (dates 1–41 and 42–83), and no calendar block (2011–12, 2013–14, 2015–16, 2017) contributes more than **50%** of the summed monthly IC |

**Outcome:**
- **QUALIFIED:** all four gates pass. This permits the owner to authorise the next stage: frozen-mechanics portfolio design on 2011–2017, then 2018–2021 internal out-of-sample with separate approval.
- **NOT QUALIFIED:** H022 is rejected, preserved as tested, with no rescue, no re-weighting and no other horizon or threshold.

### C8. Diagnostics (pre-registered, NON-gating, reported once)

1. **Sector:** IC on the FF12 sector-demeaned response (groups of ≥ 5 stocks, else the population mean) and its t-statistic. If t_sector < ½ t_IC, the result is flagged "substantially sector-driven".
2. **Regime:** mean IC by frozen regime state (STRONG / NORMAL / WEAK / RISK_OFF) with month counts. Never used to rescue a failed score.
3. **Incremental information (the one secondary test):** a monthly Fama-MacBeth rank regression of the sector-demeaned response on rank(score), rank(12-1 momentum) and rank(log PIT market cap). Report the mean slope on the score, its NW t-statistic (lag 2) and its null quantile from the same null worlds. Interpreted only, never a gate.
4. **Horizons:** 2 and 3 months (C3).
5. **Coverage:**
   - response status counts by quintile and year;
   - population size per date;
   - 80+ count per date;
   - per-year mean IC;
   - the quintile means.

No component-level (Technical / Fundamental / Sector alone) or feature-level statistic is computed.

### C9. Null and threshold

**Primary null: the H020 identity-tethered within-date permutation** (`qr_p7_pred.Tether`; one stratum, no self-matching):
- every population stock receives the score side (score, quintile, 80+ flag) of a partner stock;
- it keeps that partner while both remain in the population; free stocks are re-matched at random each date;
- every fixed point is removed.

**What it preserves:**
- on every date, the exact multiset of scores (distribution, 80+ count, quintile counts);
- each receiver's null score history is another real stock's score history (persistence and its autocorrelation);
- the real returns, with all their market, sector, volatility and common-shock structure, the changing universe, delistings and the monthly calendar.

**What it breaks:** only the link between a stock's own score and its own future return.

**Not used:**
- a global shuffle (destroys persistence and dates);
- a stratified tether (H020 design check: dynamic strata shorten the partner tenure and make the null too narrow).

**Full-procedure null:** every world recomputes the whole statistic chain (IC series, t_IC, 80+ excess, quintiles, monotonicity, halves, blocks, diagnostics). c_IC comes from these worlds, and the share of worlds passing all four gates (the procedure's false-promotion rate) is reported.

**Worlds:** R = **5,000**, seeds 1–5,000 (`qr_p7_pred.SEEDS`), in 5 batches of 1,000 (seeds 1–1,000, …, 4,001–5,000).

**Threshold:**
- **one-sided 1%** (the H019–H021 standard), floored at the normal 2.326;
- the full procedure is stricter: synthetic false promotion is 0.3%.

**Multiple-testing context:** H022 is the programme's 22nd hypothesis.
- The 1% level is kept rather than loosened.
- A Bonferroni correction across all phases is not applied, because each phase was closed before the next was designed, and the 2018–2021 internal out-of-sample and the locked Holdout remain as further independent confirmations.
- The owner may choose a stricter level (e.g. 0.5%: the 25th largest of 5,000) **before** the null is computed.

### C10. Execution plan (next stage; each step needs explicit owner approval)

1. **Host S023 (H022) and canary X994** (a byte copy).
   - S023 is the X993 v1.1 export pipeline (frozen score at the 84 reviews), plus `qr_p7_pred.response` on the same RAW, split and dividend panel (history 2007-01-01 → 2017-12-29), plus `qr_p7_pred.prepare / run_world / critical_value / promotion` in-host.
   - Only statistics leave QuantConnect: no per-stock return or price.
   - Configs are gated by `owner_approval_required`.
2. **Canary X994: plumbing only.** Checks:
   - response timing;
   - corporate-action recomputation on a deterministic sample (an independent fresh-history path, as X992);
   - status counts;
   - score fingerprint and integrity.
   It computes **no** real IC and no gate.
3. **Null E023-01 … 05:** 1,000 worlds each. Only null-world statistics are exported. Then c_IC is computed, frozen and committed (null result hash) **before** the real evaluation.
4. **Real E023-06:** run exactly once from a clean committed tree. The checkpoint report then follows and the process STOPS.

## Part D — Integrity canaries (pre-real-run)

Tests are in `tests/test_p7_pred.py`, `tests/test_p7_cp3r.py` and `tests/test_p7_export.py`; the in-host checks run in X994.

| Canary | What it checks |
|---|---|
| A. Future-data invariance | Changing prices after t does not change any score input at t. A later filing or restatement cannot change a recorded revenue baseline (test A of P7-CP3R) |
| B. Truncation | Inputs computed from data truncated at t equal those from the full data; the truncated PIT store reproduces the ledger value |
| C. Response timing | The response starts at the open of t + 1. Changing any price at or before t (including the close of t) leaves it unchanged. No response price enters any feature or ranking (the score is computed before and independently) |
| D. Corporate actions | A split, a dividend at its reference price, a delisting (last real close) and "no bar after t" reproduce hand-computed totals; an unverified split is excluded and counted. In-host (X994): an independent fresh-history recomputation on a deterministic sample |
| E. Null determinism | The same seed gives the same mapping and result; the null is an exact within-date permutation with no self-match and persistent partners |
| F. Positive control | A planted score-return link passes all gates |
| G. Negative control | Independent scores qualify at most rarely (synthetic false promotion 0.3% in the power study) |

## Part E — Synthetic power study (`research/phase7/P7_power.py` → `P7_power.json`)

**Design:**
- the **real** E993-02 score tables (scores only; 83 dates; 196–612 stocks; real sectors, volatility bands, momentum bands, fundamental subtotals, persistence, universe changes);
- **synthetic** returns: market, 16 sector factors, three zero-mean style factors the score loads on (calibrated to a null monthly IC sd ≈ 0.10), and t(5) idiosyncratic noise by real volatility band;
- a planted edge κ per standard deviation of the score's normal rank score.

**Main scenario results:**
- c_IC (synthetic) 2.50;
- significance-gate size 0.9%;
- full-procedure false promotion **0.3%** (1,000 held-out null worlds);
- no κ = 0 dataset passed (0 of 200).

**Detectable effects:**

| Power | Monthly IC | 80+ excess | Q5 − Q1 | Optimistic / pessimistic noise (80+ excess) |
|---|---|---|---|---|
| **50%** | ≈ 0.033 | ≈ **+6.3% / yr** | ≈ 7.5% / yr | 4.9% / 8.7% |
| **80%** | ≈ 0.047 | ≈ **+10.2% / yr** | ≈ 10.6% / yr | 8.3% / 12.1% |
