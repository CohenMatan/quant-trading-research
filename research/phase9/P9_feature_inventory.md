# P9 — Score v1 feature inventory (H024 step 1)

**Owner decision:** D201. **Written:** 2026-10-11, before any H024 feature value, null world or return was computed.

**Sources read** (the frozen implementation, not descriptions):
- `src/qresearch/lean/qr_p7_score.py`, pinned by `qresearch.p7score`: `technical_inputs`, `fundamental_inputs`, `score_date`, `scoped_quintiles`, `sector_state`, `POINTS`, `BAND_FRACTION`, `RANK_SCOPE`, `HIGHER_IS_BETTER`;
- `src/qresearch/lean/qr_p7_export.py`: `fund_values`, `fund_inputs`, `RevenueLedger`, `tech_at`;
- the frozen Data v2 host `strategies/X998_data_v2_export/main.py`: `_ledger`, `_month_end`, `_row_for`;
- the H022 / Data v2 host `strategies/S024_h022_data_v2/main.py`.

## Common facts (all features)

| Item | Frozen value |
|---|---|
| Decision rows | the last session of each month, 2011-01 → 2017-11 (83 decisions). Prices are read through the close of the review session. |
| Fundamental timing | Data v2 M2 timing: a report is used from the day after its SEC filing, as known on the universe-selection day that reflects the review session. True TTM is built from up to seven quarters in the frozen PIT store; records older than 200 days are stale. |
| Price series | C = split-adjusted close (trend features); P = total-return close (RAW × split × dividend multipliers; momentum and volatility); RAW is execution only. Every window uses the security's own valid bars inside its current life (`qr_p7.LIFE_GAP` = 60 sessions). |
| Ranking population (Score v1) | the data-scorable stocks with no hard disqualifier H1–H5 (H1 financial / no SIC; H2 fundamentals missing or stale; H3 < 253 bars of history; H4 corporate-event contamination; H5 last bar > 5 sessions old). H6 (broken trend) and H7 (equity ≤ 0, or NI ≤ 0 and OCF ≤ 0) make a stock ineligible after ranking. |
| Transformation | quintile by average rank: `q = floor(5 (r − 0.5) / n) + 1`; band points `BAND_FRACTION = (0, 0, 1/3, 2/3, 1)` × the dimension maximum, rounded half up |
| Data v2 coverage | every Score v1 input is valid for every row of the H022 population (34,863 stock-months, 163–585 a month), because missing inputs trigger H2 / H3 |

## The eight Score v1 features

### V1-1 Trend state (Technical, 15 points)

- **Formula.** With C = split-adjusted closes on the current life's valid bars, b = last bar ≤ t:
  - SMA50 = mean(C[b−49..b]);
  - SMA200 = mean(C[b−199..b]);
  - SMA200_lag = SMA200 of 21 bars earlier;
  - rising = SMA200 > SMA200_lag.
- **States:**
  - **strong** if close > SMA50 > SMA200 and rising;
  - **moderate** if close > SMA200 and rising;
  - otherwise **weak**.
- **Points:** 15 / 8 / 0.
- **Source and lookback:** RAW bars × split factors; 221 bars.
- **Transformation:** categorical (3 levels).
- **Related rules:** H6 (broken trend: close < SMA200 and SMA200 falling) is a disqualifier.

### V1-2 Momentum 12-1 (Technical, 15 points)

- **Formula:** `P[b−21] / P[b−252] − 1` (total-return closes, skipping the last month).
- **Direction:** higher is better.
- **Ranking:** market-wide quintiles.
- **Points:** 0 / 0 / 5 / 10 / 15.
- **Lookback:** 253 bars.

### V1-3 Risk: 60-day volatility (Technical, 10 points)

- **Formula:** population SD (ddof 0) of the last 60 daily log total-return returns.
- **Direction:** **lower is better**.
- **Ranking:** market-wide quintiles.
- **Points:** 0 / 0 / 3 / 7 / 10.
- **Lookback:** 61 bars.

### V1-4 Profitability: GP/A (Fundamental, 15 points)

- **Formula:** `gross_profit True TTM / total_assets` (latest PIT record).
- **Direction:** higher is better.
- **Ranking:** quintiles **within FF12 sector** (market-wide for groups of fewer than 10).
- **Points:** 0 / 0 / 5 / 10 / 15.

### V1-5 Cash conversion (Fundamental, 10 points)

- **Formula:** `(operating cash flow TTM − net income TTM) / total_assets`, which is negative accruals.
- **Direction:** higher is better.
- **Ranking:** market-wide quintiles.
- **Points:** 0 / 0 / 3 / 7 / 10.

### V1-6 Balance sheet: equity / assets (Fundamental, 10 points)

- **Formula:** `stockholders_equity / total_assets` (latest PIT record).
- **Direction:** higher is better.
- **Ranking:** quintiles **within FF12 sector**.
- **Points:** 0 / 0 / 3 / 7 / 10.

### V1-7 Revenue growth (Fundamental, 10 points)

- **Formula:** `revenue True TTM / revenue True TTM recorded live at the review 12 months earlier − 1`. The baseline comes from the store-wide revenue ledger (owner D173: same security life, same SEC registrant, chronology checked).
- **Direction:** higher is better in Score v1.
- **Ranking:** market-wide quintiles.
- **Points:** 0 / 0 / 3 / 7 / 10.

### V1-8 Sector context (Sector, 15 points)

- **Formula:** d = FF12 sector breadth − market breadth, where breadth is the share of eligible members above their own SMA200 (PIT denominator).
- **States:** supportive (15) if d ≥ +0.10; weak (0) if d ≤ −0.10; otherwise neutral (8). A group with fewer than 10 members having a state is neutral.
- **Transformation:** categorical (3 levels).

## Redundancy and prior research

| Feature | Family | Prior project research on the same idea | Cross-sectional rank correlation |
|---|---|---|---|
| V1-1 Trend state | momentum / trend | H018 (Phase 3 grammar of MA / trend states: no edge); H019 S3 (Han-Zhou-Zhu MA trend factor: IC t 0.12); H020 (chart trend structure: no edge) | measured in canary E026-01 (no returns) |
| V1-2 Momentum 12-1 | momentum | H019 S1 (12-1 momentum, 2011-01 → 2017-11, ≥ $2B: top-decile −2.18%/yr, IC t 0.22); earlier H002 / H003 / H008 momentum hypotheses | E026-01 |
| V1-3 60-day volatility | risk | never tested alone as a cross-sectional ranking (volatility appeared only as a filter in the H018 grammar) | E026-01 |
| V1-4 GP/A | profitability | H016 (GP/A top-20 quarterly portfolio: rejected, Sharpe 0.69 vs EW 0.85) | E026-01 |
| V1-5 Cash conversion | accruals / cash-flow quality | never tested alone | E026-01 |
| V1-6 Equity / assets | balance sheet / leverage | never tested alone | E026-01 |
| V1-7 Revenue growth | growth | never tested alone | E026-01 |
| V1-8 Sector context | sector-relative | H021-A tested sector **ETF relative momentum** (failed), a related but different idea; sector breadth was never tested alone | E026-01 |

All eight were tested only as parts of combinations: H022 (Score v1, Rejected) and H023 (layer weights, no robust candidate). Those results are records, not reasons to remove any feature from H024.

The H024 library (`research/phase9/H024_spec.md`) takes each retained Score v1 feature's **underlying input**: the continuous measure, or the 3-level state for the categorical ones. Its frozen formula, direction and rank scope are kept unchanged. The quintile bands and points are replaced by the H024 percentile transform. The canary output appends correlations and coverage to this inventory (`research/phase9/cp1/P9_CP1_canary_E026-01.json`).
