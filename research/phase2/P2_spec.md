# Phase 2 development specification: H014 (frozen)

- **Status:** FROZEN 2026-09-30, before any H014 backtest (owner authorisation "Phase 2 — Final Methodology Approval and H014 Development Authorization", D094).
- **Hash-pinned:** `qresearch.p2spec.SPEC_SHA256`, checked by `tests/test_p2_spec.py`. Any edit breaks the test. A change needs a written amendment approved by the owner **before** the result it could affect.
- **Implements:** P2-CP0 (proposal), P2-CP0b (methodology), P2-CP0c (amendment), as approved.
- **Programme:** P2, cycle label `P2C1`. This is not C04.

## 1. Data categories

| Category | Dates | Status in this stage |
|---|---|---|
| D: Development | 2010-01-04 → 2021-12-31 (split label `DEV`) | The only data used |
| H: Historical Holdout | 2022-01-01 → 2026-08-31 | Locked by code (`LAST_UNLOCKED_DATE`) |
| U: Additional unseen historical data | 2026-09-01 → the freeze timestamp | Locked |
| F: True forward data | After the complete freeze and explicit owner approval | Not started |

- Data before the freeze timestamp is **never** called forward testing.
- Indicator windows may read price history before 2010-01-04 (at most 259 sessions) to form signals from the first day. That data is only warm-up, as in every earlier cycle.

## 2. Hypothesis budget

- H014 is hypothesis 1 of at most 3 before the Holdout is consumed.
- Every hypothesis faces the same development margin: Sharpe(H) − Sharpe(EW) ≥ +0.25. There is no escalation.

## 3. H014 rules (S014)

All signals are computed from completed daily bars up to the close of day T, using split- and dividend-adjusted OHLC loaded point in time.

**Universe.** Unchanged:
- US common stock, NYSE/Nasdaq/AMEX;
- point-in-time market cap ≥ $2B;
- price ≥ $5;
- 20-day average dollar volume ≥ $5M.

A name is evaluated only if it has a real (not filled-forward) bar at T and at least **259 closes** in its window. This applies to every book, controls included: RSI14 needs 250 changes at each of T−8 … T, so the pre-declared 8-session window perturbation uses the same data requirement.

**Indicators**

| Name | Definition |
|---|---|
| MA_n(T) | Simple mean of the last n adjusted closes ending at T |
| RSI14(t) | Wilder's RSI over the **250 daily close changes ending at t**: seeded with the simple mean of gains and losses over the first 14 changes, then smoothed with avg = (13·avg + x)/14 over the remaining 236. The seed's weight at t is (13/14)^236 < 10⁻⁷, so this equals Wilder's RSI on full history to about 7 digits, while being a strict function of a fixed look-back. RSI = 100 if the average loss is 0 (50 if both averages are 0). |
| MOM(T) | 12-1 momentum = Close(T−21) / Close(T−252) − 1 |

**Entry signal at T (all must hold)**
- Trend U1: Close(T) > MA200(T).
- Trend U2: MA50(T) > MA200(T).
- Pullback P: min(RSI14(T−5), …, RSI14(T−1)) ≤ 40.
- Recovery R1: RSI14(T) > 45.
- Recovery R2: Close(T) > High(T−1).

**Execution and ranking**
- Execution: a market-on-open order at T+1 (the harness makes an earlier fill impossible).
- Ranking: MOM(T), highest first; ties by security id, ascending. Momentum ranks only; it is never a filter.

**Portfolio**
- 12 slots, $100,000, equal slot weight (harness `slot_weight`).
- D051 cash rules: settled cash only, 2% buffer, 15% gap reserve.
- $5,000 minimum new position; 10% maximum weight; no leverage.
- $7 per order; 10 bps slippage per side.
- Each close: exits are sold, and free slots are filled from that day's ranked signals. A position being sold still occupies its slot until the sale executes (D051).
- Re-entry only on a new signal.

## 4. Exits (the only two candidates)

Exit signals form at T's close and execute at T+1's open. `held` = trading sessions since the entry fill (0 on the entry day; harness `qr_sessions_held`).

| Candidate | Version | Exit rule |
|---|---|---|
| **A (primary)** | S014 v1.0 | Exit at the first close with Close < MA200, or when held ≥ 63. **Horizon roll:** when held ≥ 63 and the stock is an entry candidate at that close (eligible universe, real bar, 259 closes) satisfying the book's own entry signal, it is kept and its clock restarts (held = 0 at that close). |
| **B** | S014 v1.1 | Exit at the first close with Close < MA200, or when held ≥ 126. No roll. |

- There are no other exits: no stop-loss, no MA50 exit, and no exit on leaving the universe.
- The harness's delisting and D059 untradeable-holding handling is unchanged. That is data handling, not a strategy exit.

## 5. Controls (benchmark kind, never candidates, never promotable)

Every control uses the same code (S014), universe, data requirement, 12 slots, cash rules, costs, exit variant (A or B, including the horizon roll against the control's own entry rule) and $100K. Only the entry rule and the ranking differ.

| Control | Entry signal at T | Order |
|---|---|---|
| C1: trend-only | U1 and U2 | MOM, highest first |
| C2: pullback without recovery | U1 and U2 and RSI14(T) ≤ 40 | MOM, highest first |
| R: random uptrend, seeds 1, 2, 3 | U1 and U2 | Seeded random order over the qualifying ids (X962 `pick_order` with the seed and session) |

Reported for every book, to show the economic comparability:
- exposure (invested share);
- turnover;
- slot usage (mean number of positions / 12);
- mean and minimum cash share;
- order count;
- cost drag.

## 6. Committed development runs (DEV, 2010-01-04 → 2021-12-31)

| ID | Kind | Book |
|---|---|---|
| E014-01 | research | Candidate A (v1.0) |
| E014-02 | research | Candidate B (v1.1) |
| E014-03 | benchmark | C1, exit A |
| E014-04 | benchmark | C2, exit A |
| E014-05, E014-06, E014-07 | benchmark | R, exit A, seeds 1, 2, 3 |
| E014-08 | benchmark | C1, exit B |
| E014-09 | benchmark | C2, exit B |
| E014-10, E014-11, E014-12 | benchmark | R, exit B, seeds 1, 2, 3 |
| E014-13 | sizing | $200K sensitivity of E014-01 (12 slots) |
| E014-14 | sizing | $200K sensitivity of E014-02 (12 slots) |

- **Benchmarks:** EW = E901-07; SPY = E900-07. Both are existing runs over 2010-01-04 → 2021-12-31.
- **Canaries** (X965, infrastructure, non-candidate parameters) run before any of the above.

## 7. Candidate selection (frozen metric)

For each candidate X, over the daily returns of its DEV run, compute

  **D_X(half) = Sharpe(X, half) − Sharpe(EW, half)**

- Sharpe = mean / standard deviation (ddof 1) of the daily simple returns dated inside the half, × √252.
- The halves are 2010-01-04 → 2015-12-31 and 2016-01-01 → 2021-12-31.
- The candidates come from the single DEV runs, not from separate runs.

**B replaces A if and only if D_B(first half) > D_A(first half) and D_B(second half) > D_A(second half).** Otherwise A is chosen.
- Full-period point estimates play no role in the choice.
- The Holdout is never used.

## 8. Development gates (2010–2021, $100K, the chosen candidate; all must pass)

Sharpe is defined as in §7, over the whole DEV period.
- CAGR is from the equity curve.
- Max drawdown is the largest peak-to-trough fall, as a negative fraction.
- Calmar = CAGR / |max drawdown|.

**G1 (all four must hold)**
- **G1.1:** Sharpe(H) − Sharpe(EW) ≥ +0.25 **and** Sharpe(H) − Sharpe(SPY) ≥ +0.10.
- **G1.2:** CAGR(H) ≥ CAGR(EW) − 0.02.
- **G1.3:** Calmar(H) ≥ Calmar(EW).
- **G1.4:** MaxDD(H) ≥ MaxDD(EW) − 0.05, i.e. at most 5 percentage points deeper.

**G2:** with the same exit variant as H, Sharpe(H) must be strictly greater than:
- Sharpe(C1);
- Sharpe(C2);
- the median Sharpe of the three R seeds.

**G3: consistency across six two-year blocks** (2010–11, 2012–13, 2014–15, 2016–17, 2018–19, 2020–21).
- Requirement 1: Sharpe(H, block) − Sharpe(EW, block) > 0 in at least 4 of the 6 blocks.
- Requirement 2: no block contributes more than half of the total excess return.
  - Excess return of a block = the sum of the daily (r_H − r_EW) dated in the block.
  - The total must be > 0, and max(block excess) / total ≤ 0.50.

**G4: robustness and costs**
- **(a)** At least 5 of the 6 perturbations (§9) keep Sharpe − Sharpe(EW) ≥ +0.10.
- **(b)** At 2× slippage, Sharpe(H) − Sharpe(EW) ≥ +0.10.
- **(c)** Realised cost drag ≤ 1.5% a year at base costs.
  - Cost drag = (commissions + slippage) / mean equity / years.
  - Slippage = traded notional × the run's slippage rate.

No weighted score. A gate that could not be evaluated fails.

## 9. Conditional robustness procedure (pre-declared; no other runs)

- **Trigger:** the robustness runs are made if and only if the chosen candidate passes G1, G2 and G3 on its base run. Otherwise G4(a) and G4(b) are "not run: candidate already failed". G4(c) is always evaluated.
- **Run IDs** are fixed here, whichever candidate is chosen:

| ID | Change from the chosen candidate |
|---|---|
| E014-15 | 2× slippage (G4b) |
| E014-16 | 4× slippage (reported) |
| E014-17 | 6× slippage (reported) |
| E014-18 | RSI pullback threshold 35 |
| E014-19 | RSI pullback threshold 45 |
| E014-20 | Pullback window 3 sessions |
| E014-21 | Pullback window 8 sessions |
| E014-22 | Horizon 42 (A) or cap 84 (B) |
| E014-23 | Horizon 84 (A) or cap 168 (B) |

- No new perturbations may be added after results.
- The controls are never re-run with perturbations.

## 10. Diagnostics (reported, never gates)

**DSR** (frozen D082 formula, `stats.deflated_sharpe`) of the chosen candidate's DEV daily returns.
- The dispersion is the programme-1 frozen V[SR] = 0.0009463432771146249.
- Views:
  - (i) **P2 candidates** N = Phase 2 selection configurations (2);
  - (ii) **P2 broad** N = Phase 2 selection + robustness configurations;
  - (iii) **cumulative** N = all selection candidates in the registry (40 + Phase 2's).
- A DSR below 0.90 is printed as a warning.

**PBO** (CSCV, 16 blocks):
- over the two candidates;
- and, if run, over the chosen candidate's base plus its 6 perturbations.

**Other diagnostics**
- Paired stationary block-bootstrap intervals (mean block 63 days, seed 20261004) for the Sharpe difference against EW, SPY, C1, C2 and each R seed.
- Per-year and per-block tables.
- Trade statistics.
- $200K sensitivity.
- 4× and 6× costs.
- Evidence that the pullback/recovery mechanism adds value beyond the trend filter: the paired differences to C1 and C2 by block.

## 11. Classifications in the report

| Class | Condition |
|---|---|
| **Profitable** | CAGR > 0 net of costs |
| **Benchmark-beating** | G1 passes |
| **Control-beating** | G2 passes |
| **Development-qualified** | G1–G4 all pass. Only then may the owner be asked for Holdout access. |

## 12. Prohibitions

- No new RSI, MA or recovery thresholds.
- No added indicators.
- No expansion of the candidate set.
- No choice of seeds or subperiods.
- No change to controls or gates after results.
- No access to H, U or F.
- Every run and failure is kept in `experiments/INDEX.csv`.
- Stop after the development checkpoint.
