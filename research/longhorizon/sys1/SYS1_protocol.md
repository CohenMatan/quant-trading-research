# SYS-1 — defensive sleeve + SPY, single-account development experiment — PROTOCOL (FROZEN, owner D252)

**Owner decisions:**
- D251: design (`docs/checkpoints/OC_CP6_oc2_closure_corrected_sys1_design.md`; draft `SYS1_protocol_PROPOSED.md`).
- D252: approval of the experiment (`docs/owner/2026-10-19_sys1_controlled_development_experiment.md`).

This file finalises the PROPOSED draft. It records the approved options OD-1 to OD-7 and resolves the five mandatory pre-freeze clarifications.

**Freeze:**
- The SHA-256 of this file, of the engine `src/qresearch/lean/qr_sys1.py`, of the host `strategies/S032_sys1_account/main.py` and of the offline rules `SYS1_canary.py` / `SYS1_eval.py` is pinned in `qresearch.sys1`.
- All of these are committed before E032-01 runs.
- No result of any SYS-1 arm existed when this file was frozen.

**Scope:**
- SYS-1 only. Nothing here amends a programme rule, an earlier experiment or H028.
- H028 stays **REJECTED** (D220 / D240): a Frozen Defensive Research Reference, never production.
- The Holdout 2022-01-01 → 2026-08-31 stays sealed. Nothing after 2021-12-31 is requested.

## 1. Question and interpretation

**Question.** In one investable account with costs, does a fixed allocation of a defensive stock sleeve plus SPY give an economically meaningful benefit over SPY buy-and-hold?
- **Q1:** risk / downside behaviour (descriptive).
- **Q2:** enough wealth to justify the complexity (FS-2, FS-3, FS-6).

**Known history (owner clarification 5).**
- 2015–2021 has been examined extensively (H026–H028, LV15, SPY). The expected terminal-wealth comparison is already partly known: OC-CP6 §11 predicts A1 from known components.
- The test is about:
  - account-level feasibility;
  - value beyond market exposure (BM-X);
  - costs;
  - stability;
  - comparison with transparent defensive alternatives (LV15, SPLV).
- It does **not** validate H028 and establishes no stock-selection alpha.
- **Permitted classifications** (owner OD-6): NOT EXECUTABLE, NOT SUPPORTED, NOT FALSIFIED — DEVELOPMENT-CONSISTENT.
- Never used: QUALIFIED, VALIDATED, "proof of persistent alpha".
- A failure applies to the tested architecture only. A pass does not authorise the Holdout, live trading or a D051 production model.

## 2. Account and capital (OD-2)

- **One account, $200,000.** SYS-1 only; the programme baseline stays $100,000. Results at $200,000 are never presented as achievable at $100,000, where the stock-sleeve systems are infeasible (OC-CP6 §5).
- Long only. No leverage, no borrowing, no margin. Cash is never negative.
- Cash earns 0% in every arm (disclosed; T-bill yields were 0–2.4% in 2015–2021).

## 3. Execution model E1 (OD-3)

E1 is the frozen H028 shadow-book convention (`qr_h026.simulate`), applied to every arm. It is classified as an **idealised research execution model, not a validated real-world implementation.**

**Mechanics:**
- **Decision:** the frozen H028 month-end review (84 decisions, 2014-12-31 → 2021-11-30; outer years 2015–2021).
- **Execution:** at the next session's open (entry row e = k + 1).
- **Orders:** notional, fractional, at the open price.
- **Costs:**
  - buys at open × (1 + s), sells at open × (1 − s);
  - s = 0.10% (main) and 0.20% (robustness), with the same selections and no refit;
  - $7 per executed order (stock or ETF).
- **Valuation:** every holding (stocks and ETFs) is valued on its total-return index (§9).
- **Delisted or halted stocks** (frozen convention): valued at the last real close; they become cash at the next review at no cost.
- **Final liquidation** at the 2021-12-31 close: stocks and ETFs sold after costs. A stock without a final close stays at its last close value at no cost (frozen convention).

**Disclosed limitations:**
- fractional notional execution (no whole shares);
- dividends reinvested inside the position on the ex-date at no cost;
- the delisting convention above;
- no gap reserve and no cash buffer;
- open fills with fixed proportional slippage.

A later real-money implementation would need a separate approval and a whole-share / cash-reserve feasibility validation.

## 4. Position rules (OD-1)

- **Stocks:**
  - at most **15** (frozen H028 / LV15 Top-15, FF12 sector cap 3, frozen `qr_h026.pick`);
  - minimum new stock position **$5,000**;
  - **initial weight ≤ 10%** of account equity at entry (by construction a new stock is about 3.3%).
- **ETFs (SPY, SPLV, USMV)** under OD-1:
  - not counted in the 15-position limit;
  - exempt from the 10% single-position cap;
  - subject to every cash, cost and execution rule.
- **Account-rule violations counted in every arm:**
  - negative cash;
  - more than 15 stocks;
  - a new stock ticket below $5,000;
  - a new stock ticket above 10% of equity.

  Any violation fails FS-1.

## 5. Allocation (OD-5) and the cash ledger (owner clarification 2)

**Stock buys (OD-5):**
- At each monthly review, every **new** stock (in the frozen Top-15 and not held) is bought with ticket **t = 0.5 × E / 15**.
- E is the account equity at the entry open after step 1 below: cash + stocks + ETFs at that open's values.
- Held stocks are kept: not trimmed and not topped up (frozen H028 rule).
- The stock share floats between reviews and is **not** an exact 50 / 50. Actual stock / SPY / cash allocations are reported.

**Deterministic order at every review (one ledger, one cash balance):**

1. **Stock sales.** Every held stock not in the new Top-15 is sold at open × (1 − s) − $7, in the frozen order. Proceeds go to cash.

2. **Stock buys.**
   - If t < $5,000, **every** new buy of this review is skipped (counted). The slots stay empty until the next review, and the cash is handled by step 5.
   - Otherwise the cash needed is n × (t × (1 + s) + $7).
   - If that exceeds cash, the **absorbing ETF (SPY) is sold first**, by exactly the shortfall plus its own $7, grossed up for slippage: x = (need − cash + 7) / (1 − s), capped at the SPY value.
   - If cash is still short (only possible once SPY is exhausted), the tickets are **scaled down equally** (frozen `qr_h026.simulate` rule): a = (cash − 7n) / (n (1 + s)), floored at 0. If 0 < a < $5,000, every new buy is skipped (counted).
   - Commission and slippage are deducted in the same arithmetic that determines cash: no buy is executed against cash that is not there.

3. **Target-ETF sales** (A3, D2, D3, BM-X). Each target ETF is traded to w × E′, where E′ is the equity after steps 1–2. A sale is executed when it is at least $1,000.

4. **Target-ETF buys.**
   - Executed when they are at least $1,000.
   - A buy short of cash first sells the absorbing ETF (as in step 2).
   - If there is no absorber or it is exhausted, the buy is reduced to (cash − 7) / (1 + s).

5. **Residual cash.** The absorbing ETF (SPY in A0–A3 and D3) buys all remaining cash: y = (cash − 7) / (1 + s), so cash becomes exactly 0. This happens when cash ≥ $1,000; a smaller residual stays as cash at 0% until the next review.

   Arms without an absorber (BM-X, D2) keep their residual as cash.

**Guarantees:**
- **No borrowing.** Every buy is sized from cash on hand after the costs of the trades that funded it. Cash below −$0.000001 is a violation.
- **No hidden financing.** A zero-return world loses exactly its commissions and slippage (canary C5, tests).
- The $1,000 ETF minimum trade avoids $7 orders on rounding-size drifts. It applies identically to every ETF in every arm. Below it, a target-weight drift stays.

## 6. Arms (one evaluation run; fixed list; no selection among arms)

| id | arm | role |
|---|---|---|
| A0 | SPY buy-and-hold, $200,000 | main wealth benchmark |
| A1 | frozen H028 sleeve (S030 real path, λ = 100, Top-15) + SPY absorber, stock tickets 0.5 E / 15 | **primary system** |
| A2 | frozen LV15 sleeve (`qr_h027.lv15_scores`) + SPY absorber, same rules | transparent stock-defensive comparator |
| A3 | SPLV traded to 50% of equity each review + SPY absorber | transparent ETF-defensive comparator (OD-4, gating) |
| BM-X(A1), BM-X(A2), BM-X(A3) | SPY at the ex-ante beta weight of the system (§7) + cash | exposure-matched control per system |
| D1 | H028 alone, $100,000 (frozen replay of E030-05) | historical reference |
| D2 | SPY traded to 90% each review + 10% cash | non-gating diagnostic |
| D3 | USMV traded to 50% + SPY absorber | non-gating diagnostic, only if USMV passes C4 |

- Every arm is computed at 0.10% and 0.20% slippage.
- A0 is the SPY reference of the same slippage.
- QQQ is excluded (D251). There is no $100,000 stock-sleeve arm.
- **Two-account reference** (descriptive, OC-CP6 §11): D1 + SPY B&H at $100,000.

## 7. BM-X — prospective exposure-matched control (owner clarification 3)

**Betas:**
- **Estimate.** At review t (session row k), each security's beta is the OLS slope of its daily total returns on SPY's daily total returns. It uses the 252 return pairs ending at the review-session close (price rows k − 252 … k). Only data at or before the review close is used, before the execution open k + 1.
- **Insufficient data.** At least 189 finite pairs (75%) are required. Otherwise the beta is **insufficient** and set to 1.0 (the market value). Counts are reported.
  - Rows inside an unverified-split window are blanked (frozen `unverified_rows`).
- **Blume adjustment.** Every estimated beta (stocks, SPLV, USMV) is Blume-adjusted: 0.67 β + 0.33. SPY's beta is 1 by identity. Individual adjusted betas are used as estimated (not clipped). Counts of raw and adjusted betas below 0 and above 1 are reported.

**Exposure and weight:**
- **Exposure.** b_t = Σ (post-trade weight of each holding of the system at the review's entry open) × its beta. Cash has beta 0.
- The weights are the system's executed holdings at the same open at which BM-X trades: known at execution, with no later return.
- **Weight.** w_t = min(max(b_t, 0), 1):
  - b_t < 0 → 0 (all cash);
  - b_t > 1 → 1 (100% SPY).

  BM-X therefore stays long-only and unleveraged. Clamp counts are reported.

**The control:**
- BM-X holds w_t × E in SPY and the rest in cash at 0%.
- SPY is traded to that target at each review's entry open (≥ $1,000), with the same costs.
- It starts at $200,000 and is liquidated at the final close.

**Nothing else enters the weight:**
- no 2015–2021 outcome;
- no future return;
- never H028's realised full-period beta (0.764).

**Realised mismatch (reported, never used):**
- realised monthly beta of Ai and of BM-X(Ai) against A0;
- their difference;
- the mean ex-ante weight.

**Canary C7:** the betas are unchanged when re-estimated from history requested only up to the review session.

## 8. Reproduction versus combined-account behaviour (owner clarification 1)

**Standalone (exact):** canary C1 requires the engine at sleeve 1, without ETF or $5,000 overlay, at $100,000 to reproduce E030-05 **exactly**:
- wealth $328,294.90847351257;
- commissions $5,789;
- 416 buys and 411 sells;
- slippage $8,330.209577810972;
- 84 pick lists and the daily path, identical to the frozen `qr_h026.simulate`.

**Combined account (disclosed and quantified, not claimed to reproduce H028):** for A1 (and A2) against the standalone frozen book on the same scores, at $200,000 and at $100,000:
- months whose held set differs, and the Jaccard overlap;
- buys skipped by the $5,000 overlay;
- scaled (cash-constrained) buys;
- SPY funding sales and SPY absorption buys;
- ticket sizes (dynamic account equity);
- the stock-share path;
- correlation and mean (absolute) difference of the monthly sleeve returns;
- the sleeve's log growth against the standalone book's;
- stock and SPY contributions;
- A1 against the two-account reference.

The combined sleeve **is not** the frozen H028 equity curve.

## 9. ETF and corporate-action accounting (owner clarification 4)

**Total-return construction:**
- Every holding's value follows its total-return index: RAW close × split multiplier × dividend multiplier.
  - The dividend multiplier is QuantConnect's dividend feed with its reference-price convention, as already used for SPY in E028-05 / E029-05 / E030-05.
- **Stocks:** the frozen per-security S028 construction (RAW + SCALED_RAW split multiplier).
- **ETFs:** the frozen SPY construction (split events + distributions).

**No double counting:**
- Dividends are reinvested inside the position on the ex-date.
- **No cash dividend is ever credited** to the ledger.
- No adjusted price is combined with a cash distribution.

**Disclosed conventions and limitations:**
- Distributions are rounded to the cent by the feed (≤ $0.005 per distribution, D162).
- ETF expense ratios are embedded in the prices; nothing is added.
- The frozen delisting convention (§3) applies to stocks.
- ETFs need complete bars (C4).

## 10. Data (canary C4)

**Data used:**
- **Already verified:** SPY, the frozen Data v2.1 universe and features (panel digests pinned), LV15 picks.
- **SPLV** (QuantConnect id SPLV UWBCA8CFMB1H, gating) and **USMV** (USMV V0WRDXSSH205, diagnostic):
  - RAW history requested **without a subscription** (D166);
  - aggregates only (no data export, D185).

**C4 passes for an ETF only if all of these hold:**
- every calendar row from 252 sessions before the first outer review (2014-12-31) through 2021-12-31 has a valid RAW open and close;
- no row after 2021-12-31 and no off-calendar row;
- at least one distribution;
- no daily total return beyond ±20%;
- the symbol id equals the id above.

Split events are counted.

**If SPLV fails C4: STOP before the evaluation** (OD-4). Do not remove the comparator, do not substitute USMV and do not relax FS-6. If USMV fails, D3 is not computed and that is reported.

## 11. Canary E032-01 (all mandatory checks must pass; otherwise STOP)

The canary computes **no SYS-1 arm result** (no QRSY block). It recomputes only the frozen references and runs rule checks on seeded random scores.

| check | requirement |
|---|---|
| C0 | Panel equivalence: feature and response digests equal the pinned H026 digests (S029 gate; the host stops otherwise) |
| C1 | Standalone engine = E030-05 exactly (§8) |
| C2 | SPY-only account = `spy_simulate` exactly at $100,000 and $200,000; = $262,325.455801514 and $524,676.2761604529 (the frozen $200,000 diagnostic) |
| C3 | LV15 at sleeve 1, $100,000 = `qr_h027.lv15` exactly = $220,156.03484878788 |
| C4 | SPLV passes §10; SPY has every bar of the same window, no late / off-calendar row and no daily total return beyond ±20% (its dividends and total return are verified exactly by C2); USMV reported, not mandatory |
| C5 | Account rules on 3 seeded random score sets × 2 slippages and on SPLV 30% + SPY × 2 slippages: zero violations, minimum cash ≥ 0, ≤ 15 stocks, allocations sum to 1, commissions = $7 × orders. Zero-return copies of the real months (3 configurations): wealth = capital − commissions − slippage within $10⁻⁶ |
| C6 | Two toy reviews recomputed by hand = engine within 10⁻⁹ |
| C7 | Betas of 3 reviews × 8 stocks + SPLV + USMV re-estimated from history requested only up to the review session = stored betas within 10⁻⁹ |
| C8 | Run completes within the node memory (peak reported); uploaded project files ≤ 50, each ≤ 64,000 characters; every uploaded frozen module byte-identical to its pin; code hash = provenance |
| C9 | QuantConnect compliance: compile accepted, backtest completed, no rejection (D185) |

- The evaluation E032-02 runs **only** if C0–C9 all pass.
- The canary's committed assessment digest is pinned as `CANARY_RESULT_SHA256` before E032-02.
- E032-02 re-checks C0–C4 in-run and stops before computing any arm if the frozen reproduction or SPLV fails.

## 12. Falsification screens (frozen; for A1, reported for A2 / A3; OD-6)

| screen | criterion |
|---|---|
| FS-1 | Canary passed; E032-02 completed; in-run integrity C0–C4 passed; **zero** account-rule violations in every arm at both slippages |
| FS-2 | Terminal wealth Ai > BM-X(Ai), at 0.10% |
| FS-3 | Terminal wealth Ai ≥ A0, at 0.10% |
| FS-4 | FS-2 and FS-3 hold at 0.20% (each arm against its own 0.20% BM-X and A0) |
| FS-5 | Versus BM-X(Ai) at 0.10%. Yearly log-relatives LR_y = ln(1 + r_Ai,y) − ln(1 + r_BMX,y), with frozen `qr_h026.year_returns` (calendar-year close marks; 2015 from the starting capital). Passes iff Σ LR > 0, max_y LR_y ≤ 0.50 × Σ LR, Σ 2015–2017 > 0 and Σ 2018–2021 > 0 |
| FS-6 (A1 only) | Terminal wealth A1 > A2 and A1 > A3, at 0.10% |

**Classification of A1:**
- **NOT EXECUTABLE** if FS-1 fails.
- **NOT SUPPORTED** if any of FS-2 to FS-6 fails.
- Otherwise **NOT FALSIFIED — DEVELOPMENT-CONSISTENT**.

A2 and A3 are classified the same way with FS-1 to FS-5. This is descriptive only and changes nothing about A1.

## 13. Reported outputs (descriptive, every arm, both slippages)

- **Path:** terminal wealth, CAGR, volatility, Sharpe, MaxDD, under-water share and longest spell.
- **Market behaviour:** beta, up- and down-capture (P11-CP2 definitions), strong-up capture (SPY month ≥ +5%).
- **Relative performance:**
  - yearly log-relatives versus A0 and versus the arm's BM-X;
  - 2015–2017 and 2018–2021 sums;
  - the sums without 2018 and 2020;
  - rolling 36-month share of windows ahead (versus A0 and BM-X).
- **Trading:** commissions, slippage, orders, turnover; skipped and scaled buys; funding and absorption trades.
- **Allocations:** actual stock / SPY / SPLV / USMV / cash allocations after each review (minimum, median, mean, maximum).
- **BM-X:** weights, clamp counts, insufficient-beta counts, realised beta mismatch.
- **Look-through overlap proxy:**
  - per review, Σ over held stocks of (PIT market cap / Σ PIT market cap of the eligible ≥ $2B universe) × the SPY weight;
  - a proxy, since SPY constituent weights are not available; diagnostic only, no netting.
- **Sleeve comparison:** §8.
- **Double-slippage robustness:** every arm at 0.20%.

## 14. Runs and stop conditions (OD-7)

- **Runs:** one canary **E032-01**. One evaluation **E032-02**, only after every mandatory canary check passes.
- **Retries:**
  - at most **two** documented infrastructure retries in total, ids **E032-03** and **E032-04**, in that order;
  - identical code and scientific settings to the run being retried (only the experiment id and description differ);
  - permitted only for a failure before any result was produced: compile / upload / QuantConnect outage / download.
- **Never:**
  - a rerun after a result;
  - tuning;
  - a weight, K, cap, slippage, arm or rule change;
  - an additional arm, variation or optimisation.
- **Stops:**
  - a canary failure → STOP and report;
  - a clarification needing a substantive change → STOP for a new owner decision.
- **Cost:** within the existing $24 a month QuantConnect plan. No purchase, no new dataset.

## 15. Explicit limitations

- In-sample, examined data. 84 months. No significance claim.
- H028's edge is unvalidated: its p-value is structurally suspect (D238) and the repair was not validated (D239).
- H028 is Top-K fragile and has high turnover. Its advantage came from SPY-down months concentrated in 2018 and 2020.
- E1 is idealised (§3). Cash yield is 0%. The look-through overlap is a proxy.
- Results at $200,000 do not carry over to $100,000.
