# H026 — Learned Stock Score Portfolio: frozen pre-registration (v1)

Owner decision **D206** (`docs/owner/2026-10-11_p11cp1_h026_learned_score_portfolio.md`, verbatim). This file is
hash-pinned in `qresearch.p11h026` with the code that implements it, BEFORE any H026 model fit, null world or portfolio
result exists. Nothing in it changes after a result is seen; any change is H027 or later.

## 1. Status and periods

* H022, H023, H024 and H025 stay permanently closed exactly as tested.
* **2011–2021 = H026 DEVELOPMENT / MODEL-SELECTION DATA** (permanent disclosure: 2018–2021 is NOT untouched validation
  for H026; it was partly exposed by earlier unrelated work and is now part of H026 development).
* **2022-01-01 → 2026-08-31 = programme-wide FINAL HOLDOUT, still SEALED.** No 2022+ price, fundamental, SEC filing
  or benchmark value is read anywhere (cached SEC JSON snapshots are filtered by date before use).

## 2. Data v2.1 (infrastructure extension, D206 items 5–7)

* Reference table `qr_data_v21` = the frozen Data v2 builder with one parameter changed (cut-off 2021-12-31):
  `research/phase11/data_v21/build_data_v21.py`.
* Host X801 = the frozen X998 with five line-level changes only (table module, allowed end 2021-12-31, last-session
  cap, revenue-ledger cut-off `max(end year, 2017)`, header), asserted by `tests/test_p11_data_v21.py`.
* Integrity gate (before any H026 result): per period 2011–2017, 2018, 2019, 2020, 2021 — eligible stock-months,
  securities, survivor share, PIT audit, market-cap repair, identity coverage, fundamental coverage, feature coverage,
  corporate actions, deterministic rebuild, truncation / future invariance; 2011–2017 must reproduce the frozen
  H022 / H024 analysed population (H024 population digest `791a2d4c…`) or the difference must be explained by the
  extended SEC knowledge (restatement guard) and judged immaterial; otherwise STOP.
* Frozen manifest `research/phase11/data_v21/data_freeze_v21.json` pinned before any H026 learning result.

## 3. Population and features

* Monthly reviews = the Data v2 review calendar (last session of each month). **Decision reviews:** 2011-01-31 …
  2021-11-30 (131). No decision at the 2021-12-31 review (its holding period would reach 2022).
* Population at a review = the frozen H022 population (Data v2.1 eligible, Score v1 rows passing the frozen
  disqualifiers, `qr_p7_export.eligible_flag`) restricted to stocks with **all 11 H024 features valid** (the H024
  population rule). Feature formulas = `qr_h024.price_features / fund_features / feature_row` unchanged (MOM, LOWVOL,
  GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA), with the live total-assets ledger 12 months back (as S026).
* No future-fill, interpolation or return-informed imputation. Coverage is reported; if the all-valid rule removes a
  material fraction (> 25% of the H022 population in any year) STOP and report.
* **Transform:** within each review, each feature independently: average rank r (ties averaged), percentile
  p = (r − 1)/(n − 1), x = 2p − 1 ∈ [−1, +1]. No orientation; Ridge may learn either sign.

## 4. Target and label availability

* Response of stock i at review t (session row k): total shareholder return from the OPEN of row k+1 (next session)
  to the CLOSE of row k+63 (the 63rd session), with the frozen corporate-action conventions (`qr_h025.tsr` =
  `qr_p7_pred.response`: first valid open in the window; last real close if the stock stops trading, cash afterwards;
  unverified split → not evaluable), minus SPY TSR (RAW open/close with SPY's split × dividend multiplier) bought at
  the stock's entry row and held to the planned exit row. Not evaluable → excluded from training that month.
* Label = cross-sectional percentile of that excess among the population stocks with an evaluable response:
  y = 2p − 1, p = (r − 1)/(n − 1).
* **Label availability:** a model trained at cutoff T (a review date) uses an observation (t, i) only if its label
  exit date (row k+63) is strictly before T. No partially realised label. Tested explicitly.

## 5. Weighted Ridge

* Minimise Σ_t Σ_i w_ti (y_ti − β0 − x_ti·β)² + λ Σ_j β_j², w_ti = 1/N_t (N_t = training rows of review t), so every
  review month has equal total weight; the intercept is not penalised (closed form on weighted-centred data).
* All 11 features always in the model; no subset selection.
* **λ ∈ {0.01, 0.1, 1, 10, 100}** exactly.

## 6. Walk-forward

* A test year Y consists of the 12 decision reviews whose entry session lies in calendar year Y (the December review of
  Y − 1 through the November review of Y). Coefficients for year Y are fitted ONCE at the cutoff T_Y = the December
  review of Y − 1 (labels with exit before T_Y) and frozen for the whole year.
* **Outer test years:** 2015, 2016, 2017, 2018, 2019, 2020, 2021.
* **Inner validation for outer year Y:** inner test years k = 2013 … Y − 1 (first inner year 2013, so every inner fit
  has ≥ 20 training months); for each λ, fit at T_k, simulate the year-k Top-15 portfolio from $100,000 cash at the
  first entry open of year k, liquidated at the close of year k's last session after costs, against SPY bought and
  sold on the same days with the same costs; inner objective L(λ) = Σ_k ln(W_k(λ) / SPY_k).
* **λ_Y** = argmax L(λ); ties: (1) larger worst inner-year ln(W/SPY), (2) larger λ, (3) numeric order. Then the year-Y
  coefficients = the fit at T_Y with λ_Y. (The inner fit for year k with λ is the same function as the outer fit for
  year k; the outer test year is never used for its own λ.)

## 7. Score and portfolio

* Score_H026 = within-review percentile of x·β (× 100); β0 does not affect ranks.
* $100,000 start; long only; no leverage; **K = 15**; FF12 sector cap 3; monthly review; orders at the next session
  open (no intraday).
* **Target list** at each decision review: walk down the score ranking (ties: security id) taking a stock unless its
  FF12 sector already has 3, or it has no valid open on the entry session; stop at 15. Fewer than 15 → cash.
* **Rebalance (frozen):** positions not in the new list are sold at the entry open; positions in the list that are
  already held are KEPT without trimming or topping-up (no rebalancing to equal weight; no trimming, as D171); each new
  position is bought with target value = equity at the open / 15 (≤ 10% initial weight); if cash after sells cannot
  fund all new targets, each new buy is scaled down equally. No thresholds, buffers, stops or manual holds.
* A held stock that stops trading is valued at its last real close and becomes cash at the next rebalance (no cost).
* **Costs:** $7 per executed buy and per executed sell; slippage 0.10% per side on traded value (buys at open × 1.001,
  sells at open × 0.999). Fractional shares. No borrowing. Primary capital $100,000; $200,000 diagnostic.
* **Outer portfolio:** continuous from the first entry open of 2015 (the 2014-12-31 review) to the close of
  2021-12-31, then liquidated after costs. **SPY:** bought at the same first entry open with the same capital
  (commission + slippage), total return (dividends reinvested through its multiplier), sold at the 2021-12-31 close
  after costs.

## 8. Statistics and metrics

* **S_WEALTH = ln(terminal wealth H026 / terminal wealth SPY)** after all costs.
* Daily equity marked at each session close (holdings at close, cash). CAGR over calendar time (365.25-day years);
  annualised volatility = SD of daily simple returns × √252; Sharpe = mean / SD of daily returns × √252 (rf = 0);
  Max Drawdown on daily equity; time underwater = share of sessions below the running peak and the longest such
  spell; year return = year-end close mark / previous year-end mark (2015 from the starting capital); yearly
  log-relative L_Y = ln((1 + r_H) / (1 + r_SPY)).
* Turnover = traded value (buys + sells) / equity at the rebalance open; monthly mean and annual sum.

## 9. Null (before the real result)

* 5,000 worlds, seeds 1–5,000; in each world the frozen identity tether (`qr_p7_pred.Tether`, persistent, no
  self-matching) reassigns every stock the COMPLETE 11-feature vector of a partner stock at every review, in date
  order; responses, prices, sectors and the universe stay with the stock.
* Every world reruns the complete procedure: inner λ selection, annual fits, scores, Top-15 portfolio, costs, SPY
  comparison. Recorded: S_WEALTH, excess CAGR, MaxDD, volatility, years beating SPY.
* **c_WEALTH = the 50th largest S_WEALTH of 5,000** (empirical one-sided 99th percentile; `qr_xs.critical_value`
  convention). Determinism: seeds 1–25 rerun independently must reproduce exactly. Pinned before the real run:
  c_WEALTH, null result hash, feature-panel digest, portfolio / model engine hashes, seeds.

## 10. Gates (all required)

| Gate | Requirement |
|---|---|
| D1 | S_WEALTH > c_WEALTH and S_WEALTH > 0 |
| D2 | terminal wealth H026 ≥ 1.15 × SPY and CAGR(H026) − CAGR(SPY) ≥ +2.0 points / year |
| D3 | L_Y > 0 in ≥ 5 of the 7 outer years; Σ L_Y 2015–2017 > 0 and Σ L_Y 2018–2021 > 0; the largest positive L_Y ≤ 50% of the sum of positive L_Y |
| D4 | \|MaxDD(H026)\| ≤ 1.25 × \|MaxDD(SPY)\| and vol(H026) ≤ 1.25 × vol(SPY) |
| D5 | the same selections (no retraining) with slippage 0.20% per side: terminal wealth H026 > SPY (also 0.20%) |

Result: all pass → DEVELOPMENT CANDIDATE (final λ / coefficients fitted on 2011–2021 with the same inner procedure,
labels exiting by 2021-12-31; formula frozen; Holdout NOT run); else REJECTED.

## 11. Non-gating diagnostics (after the primary result; never rescue)

$200,000 capital; Top-10 and Top-20 with the same frozen yearly coefficients; sector-neutral relative performance
(holdings' monthly returns minus the equal-weight return of their FF12 sector in the population); market-regime
performance (monthly relative return by SPY above / below its 200-day average at the review); coefficient stability
(sign, magnitude, mean, SD, sign flips, adjacent-year correlation).

## 12. Final model (only if D1–D5 pass)

λ_final by the same inner procedure with inner years 2013–2021; β fitted at the cutoff 2021-12-31 using every
observation whose label exits before 2021-12-31; formula = λ, β0, 11 β; frozen with every hash; Holdout sealed.

## 13. Not allowed

Other λ values, features, transformations, interactions, targets (21/42/84/126), K, sector caps, model classes
(ElasticNet, trees, boosting, networks, AutoML, …), mechanics optimisation, opening the Holdout.
