# Owner message 2026-10-06: "Phase 6 — Authorise H021-A Sector Relative-Momentum Falsification Test"

This is a recorded summary; the full message is in the session transcript. Decision id: **D160**.

## Decisions

1. **H020 is CLOSED** as Rejected / No Production Candidate Found, preserved exactly as tested (P5-CP3).
2. **Limited GO** for one bounded falsification experiment, **H021-A**, and nothing else.
3. This is **not** a broad Phase 6 search: no optimizer, no grid, no alternative lookbacks, no absolute-trend overlay.

## Research question

"Do US equity sectors with stronger 6-month total-return relative momentum subsequently earn higher sector-relative total returns over the next month?"

## D035 amendment (Phase 6 only)

- 2000-01 → 2017-11 may be used as **development data for H021-A**.
- It applies **only** to the nine original Select Sector SPDRs and **only** to Phase 6.
- It does **not** reopen 1999–2009 for the stock-level research programme.

## Frozen design

- **Universe (fixed for the whole experiment):** XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY.
  - No XLRE, no XLC, no other ETF family.
  - The XLF real-estate change in 2016 is disclosed and handled in total-return accounting. It does not change the universe or the hypothesis.
- **Signal:** the trailing 6-month total shareholder return at month-end t, including distributions, with no skip month. No other lookback, no weekly version, no price-only version, no blend.
- **Frequency:** monthly, decided at the last tradable session of each month.
- **Primary response:** the next-month total shareholder return of each sector minus the equal-weight average of the nine.
- **Primary statistic:** the mean monthly Spearman rank IC between the signal and the response, under the P6-CP1 inference framework.
- **Gates (all required):**

  | Gate | Rule |
  |---|---|
  | P1 | t_IC > c, where c is the 1% empirical null threshold, pinned before the real result |
  | P2 | Top 3 vs the 9-sector average ≥ +3.0% a year |
  | P3 | Top 3 > Middle 3 > Bottom 3 |
  | P4 | First-half IC > 0 and second-half IC > 0, and no 6-year block (2000–05, 2006–11, 2012–17) supplies more than 50% of the total IC sum |

- **Null:** identity-tethered derangement, R = 5,000 worlds. Each world uses one fixed derangement of the nine identities, so each sector receives another sector's entire signal history. Everything else is preserved.
- **NON-GATING diagnostics** (they can neither rescue nor veto the result): the 2010–2017 result, the 2005–2017 result, the 3-month response, the 6-month response, and the sector average vs SPY.

## Mandatory sequence

1. Canary / fidelity check. If a real fidelity defect appears, STOP before the null calibration. Technical fixes are allowed only if they leave the hypothesis and the gates unchanged.
2. Run the 5,000 null worlds.
3. Compute c.
4. Commit c, the null outputs and their hashes.
5. Verify a clean tree.
6. Run ONE real H021-A evaluation.

c is immutable once pinned.

## Not authorised, even if H021-A passes

- **No portfolio:** no top-3 rotation, $100K wealth, SPY wealth, CAGR, turnover, commissions, slippage or drawdown.
- **No variants:** no H021-B, absolute trend, cash or T-bill comparison; no breadth, RSI, MACD, ADX, Bollinger, breakout, volatility, moving-average or regime filter.
- **No other universe:** no iShares, Vanguard, Fama-French or synthetic SEC-SIC sectors; no XLC or XLRE.
- **No locked data:** 2018-01-01 → 2021-12-31 for no purpose; the Holdout (2022-01-01 → 2026-08-31) for no purpose.
- **No spending:** no paid data.
- **No rescue after the result:** no 3-month, 12-month, weekly, top-2, trend or cash filter.

## Frozen wording

- **Failure:** "No sector-relative momentum edge large and robust enough to meet the project's pre-registered statistical and economic requirements was detected. The study has only about 50% power around a +3.3%/yr top-3 edge. A small real edge may therefore remain undetectable."
- **Success:** "6-month sector relative momentum demonstrated sufficiently strong cross-sectional predictive information over the frozen 2000–2017 development period to qualify for portfolio-design research."
- **Final verdict:** exactly "H021-A QUALIFIED FOR PORTFOLIO-DESIGN RESEARCH" or "H021-A DID NOT QUALIFY".

## Checkpoint

The checkpoint is P6-CP2, "H021-A Sector Relative-Momentum Falsification Result", with 40 required items. STOP after it is committed.
