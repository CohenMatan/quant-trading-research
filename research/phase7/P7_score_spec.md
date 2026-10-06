# Phase 7 Multi-Factor Conviction Score v1 — pre-registration

- **Status:** FROZEN CANDIDATE v1 (P7-CP2, 2026-10-06), written before any historical score, return or threshold was computed. Hash-pinned in `qresearch.p7score`.
- **Authority:** owner D169; P7-CP1 accepted.
- **Code:** `src/qresearch/lean/qr_p7_score.py`, using `qr_p7` (security-life rule D167). Both are hash-pinned.
- **Change rule:** nothing in sections 1–9 changes after any historical score is computed (P7-CP3) except by a recorded owner decision **taken before any return is seen**. Thresholds deferred to P7-CP3 (section 10) are chosen **only** from availability / mechanics, **never** from returns.

## 1. Universe and scorable set (decision date t)

1. **Eligible universe:** the frozen data-v1 universe at t: US common stock, NYSE/Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, with the SEC correction layer.
2. **One share class per company:**
   - **Company key:** the SEC CIK carried by the latest periodic filing visible at t (the same table rows as the PIT SIC).
   - **Choice:** the class with the highest PIT ADV20; on a tie, the smallest security id.
   - A security without a key stands alone, but it is excluded anyway by H1.
3. **Hard disqualifiers H1–H5 (data)** define the **data-scorable set**, the population for all percentile ranks:

   | Code | Disqualifier |
   |---|---|
   | H1 | No PIT SEC SIC visible at t, or SIC in 6000–6999 (financial institutions, insurers including health insurers, real estate, REITs 6798, holding / investment offices). The PIT rule is D113 (`qr_industry`): the SIC carried by the latest periodic filing, effective the day after filing |
   | H2 | Any required fundamental input missing, stale or invalid (section 4) |
   | H3 | Fewer than **253** valid bars in the current security life: the longest technical window (`MIN_HISTORY = max(221, 253)`) |
   | H4 | Corporate-event contamination (section 6) |
   | H5 | Last price bar older than **5** sessions |

4. **Hard disqualifiers H6–H7 (economic)** are applied after scoring. They make a stock ineligible but it stays in the ranking population:

   | Code | Disqualifier |
   |---|---|
   | H6 | Broken long-term trend: split-adjusted close < SMA200 **and** SMA200 falling (SMA200(t) < SMA200(t − 21 bars)) |
   | H7 | Financial impairment: equity ≤ 0, **or** (net income TTM ≤ 0 **and** operating cash flow TTM ≤ 0) |

5. **Same-universe rule.** Every future comparison or control book is drawn from the same eligible, scorable set with the same disqualifiers. **No missing value is ever filled.**

## 2. Price series

| Feature | Series | Window (own valid bars, current life) |
|---|---|---|
| SMA50, SMA200, SMA200 slope, trend state, H6 | **split-adjusted close C** (RAW × split feed) | 221 bars (SMA200 now and 21 bars ago) |
| 12-1 momentum | **total-return close P** (RAW × split × dividend feed) | 253 bars: P[b−21] / P[b−252] − 1 |
| Volatility | **total-return log returns** | 61 bars: standard deviation of 60 daily log returns |
| Sector and market breadth | **split-adjusted close C** vs its SMA200 | 200 bars |
| SPY trend (regime) | **split-adjusted close C** | 221 bars |
| Execution (later) | RAW price, T+1 open | — |

- No total-return synthetic chart is used for price structure.
- No feature mixes series.
- **Security-life rule** (D167): more than 60 missing sessions between two bars starts a new life, and no window crosses it.

## 3. Score: 0–100, integers

| Category | Dimension | Points | Feature | Normalisation |
|---|---|---|---|---|
| **Technical Quality (40)** | Trend | **15** | Trend state on C: **strong** = close > SMA50 > SMA200 and SMA200 rising; **moderate** = close > SMA200 and SMA200 rising (not strong); **weak** = otherwise | Absolute state: strong 15 / moderate 8 / weak 0 |
| | Momentum | **15** | 12-1 total-return momentum | Quintile across the scorable set |
| | Risk | **10** | 60-day total-return volatility (lower is better) | Quintile across the scorable set |
| **Fundamental Quality (45)** | Profitability | **15** | GP / Assets = gross profit TTM / total assets | Quintile **within the FF12 sector** |
| | Cash conversion | **10** | (OCF TTM − net income TTM) / total assets (higher = earnings backed by cash; negative accruals) | Quintile across the scorable set |
| | Balance sheet | **10** | Equity / total assets | Quintile **within the FF12 sector** |
| | Growth | **10** | Revenue TTM ÷ revenue TTM recorded at the review 12 months earlier − 1 | Quintile across the scorable set |
| **Sector Context (15)** | Sector health | **15** | FF12 sector breadth − market breadth (breadth = share of eligible members above their own SMA200) | ≥ +0.10 supportive 15 / between neutral 8 / ≤ −0.10 weak 0; fewer than 10 members with a state → neutral 8 |

**Quintile points:**
- **Quintiles by average rank:** q = ⌊5 (r − 0.5) / n⌋ + 1.
- **Points:** round-half-up of max × {Q1 0, Q2 0, Q3 1/3, Q4 2/3, Q5 1}.
  - 15-point dimension: 0 / 0 / 5 / 10 / 15.
  - 10-point dimension: 0 / 0 / 3 / 7 / 10.
- **Sector scope:** within the FF12 group of the scorable set; a group with fewer than 10 scorable members is ranked across the whole set.

**Total** = Technical + Fundamental + Sector, 0–100. Each stock carries a human-readable breakdown (`explain`).

## 4. Fundamental inputs (approved fields only)

- **Fields:**
  - from the frozen PIT store (D108–D114): `revenue_ttm4q`, `gross_profit_ttm4q`, `net_income_ttm4q`, `operating_cash_flow_ttm4q`, `total_assets`, `stockholders_equity`;
  - `market_cap` (universe only).
- **Availability:**
  - filing date + 1 day, or period end + 90 days if the vendor date is estimated;
  - quarantine, restatement blocks, SEC timing holds and field releases apply;
  - **freshness:** the newest TTM quarter or snapshot report must be ≤ 200 days old.
- **Revenue baseline:** the revenue True TTM **recorded at the review 12 months earlier, as known then** (a ledger). Nothing is recomputed backwards.
- **H2 (missing / stale / invalid):** any input absent; total assets ≤ 0; revenue ≤ 0; baseline revenue ≤ 0.
- **Numerical stability:** every ratio divides by total assets or baseline revenue (positive by H2). All ranks are average-rank quintiles, so outliers cannot dominate.

## 5. Market regime (exposure only; never in a stock's score)

- **Inputs:**
  1. **SPY trend** on split-adjusted closes: up = close > SMA200 and SMA200 rising; down = close < SMA200 and SMA200 falling; otherwise mixed.
  2. **Market breadth:** the share of the **PIT eligible universe** (data-v1, financials included; securities with ≥ 200 bars in their current life and a fresh bar) above their own SMA200: high ≥ 0.60, low < 0.40, otherwise mid.

- **Regime table:**

  | SPY trend \ breadth | High | Mid | Low |
  |---|---|---|---|
  | **Up** | STRONG | NORMAL | WEAK |
  | **Mixed** | NORMAL | WEAK | WEAK |
  | **Down** | WEAK | WEAK | RISK_OFF |

- **Effect:** the regime caps the number of positions (exposure ceiling ÷ 10%). It never changes any stock's score or its order.
- **Exposure ceilings** per regime are **deferred** (section 10): ceiling(STRONG) ≥ ceiling(NORMAL) ≥ ceiling(WEAK) ≥ ceiling(RISK_OFF). The owner fixes them before any return is seen.

## 6. Corporate-event protection (H4)

Events, from QuantConnect's own feeds up to t:
- **(a) unverified split:** the split event's boundary is not confirmed by SCALED_RAW (`qr_xs_panel.split_multiplier`);
- **(b) large distribution:** a distribution of ≥ **10%** of its reference price (spin-off or special).

An event at row e contaminates a window of L bars ending at bar b if v[b−L+1] < e ≤ v[b].
- Unverified splits corrupt both series, so L = 253.
- Large distributions corrupt only the split-adjusted chart, so L = 221.

The stock is excluded (H4) until the event lies outside the window. **The duration is set mechanically by the lookback (`contamination` returns the bars until clean).** A **held** stock under H4 is **frozen**: kept, not score-evaluated and never the "weakest" for replacement. It stays subject to H1, H2, H5 and H7, while H6 (trend) is suspended, because its window is contaminated.

## 7. Review frequency and filing arrival

- **Scheduled review:** **monthly**, at the last session of each calendar month (from the session calendar), with orders at the next open. The score is recomputed on all data available at that close.
- **Between reviews:** at the last session of each week, **holdings only** are checked for **hard disqualifiers** (H1, H2, H5, H6, H7). There is no score-based exit and no entry. A disqualified holding is sold at the next open.
- **Filing arrival:** a new filing enters the score at the next monthly review. It can act sooner only through the weekly hard-disqualifier check (e.g. impairment, H7). One consistent model; no immediate rescoring.

## 8. Portfolio mechanics (structure frozen; numbers deferred)

**Constraints:**
- $100,000, long only, no leverage;
- **≤ 10% per position at entry** (target 10% of equity, less if cash is short; the D051 reserve rules apply);
- $7 per buy and per sell; 10 bps slippage per side.

**Each monthly review, in order** (`plan_review`):
1. **Sell** holdings that left the eligible universe, carry a hard disqualifier (except H4 → frozen), or score **< ExitThreshold**.
2. **Regime cap:** if holdings exceed min(MaxPositions, regime cap), sell the lowest-scoring non-frozen holdings. Ties go to the lower ADV20 first, then the smaller id.
3. **Enter** eligible candidates with score **≥ EntryThreshold**, best first (score, then ADV20, then id), into free slots.
4. **Replace:** when no slot is free, the best remaining candidate replaces the weakest non-frozen holding **only if** its score ≥ that holding's score + **ReplacementBuffer**. One candidate per replaced holding. Stop at the first candidate that fails.

**Invariants:**
- **ExitThreshold < EntryThreshold** (hysteresis; enforced in code).
- **No fixed holding period or time stop.** Winners are held while their score stays ≥ the exit threshold and no hard disqualifier appears.
- **Cash is allowed.** There is **no forced filling** and **no relaxation ladder in v1**. Any later ladder needs a separate pre-registration with a hard floor.
- **No trimming of winners** in v1; drift above 10% after entry is not traded. The owner may decide otherwise before any return test.

## 9. Constants (complete list)

| Type | Constants |
|---|---|
| **Windows** (7) | SMA 50, SMA 200, slope lag 21, momentum 252 and skip 21, volatility 60, revenue baseline 12 months |
| **Judgment constants** (7) | large distribution 10%, quintiles (5), minimum sector group 10, sector breadth band ±0.10, regime breadth 0.60 / 0.40, stale price 5 sessions |
| **Weights** (8) | 15, 15, 10 \| 15, 10, 10, 10 \| 15 |
| **Level tables** (3) | quintile fractions 0 / 0 / ⅓ / ⅔ / 1; trend 1 / ½ / 0; sector 1 / ½ / 0 |
| **Inherited infrastructure** (not new) | life gap 60; fundamental freshness 200 days; estimated-date +90 days; universe filters |
| **Hard disqualifiers** | 7 |
| **Feature definitions** | 8 (trend state, momentum, volatility, GP/A, cash conversion, equity/assets, revenue growth, sector breadth) + 2 regime inputs |

## 10. Deferred to P7-CP3 (availability / mechanics only, never returns)

**Deferred:** EntryThreshold, ExitThreshold, ReplacementBuffer, MaxPositions (6 / 8 / 10 / 12) and the regime exposure ceilings.

**Selection rules (pre-registered):**
- **EntryThreshold:** the strictest candidate meeting availability floors (fixed by the owner before P7-CP3 runs) on at least 80% of review dates in every year.
- **ExitThreshold / ReplacementBuffer:** the smallest E − X and buffer meeting a whipsaw-rate limit and a cost ceiling.
- **MaxPositions:** the smallest K with expected cash utilisation ≥ 80% within the 10% cap and the cost ceiling.

**CAGR, Sharpe, returns, IC, SPY comparisons or alpha are never consulted.**
