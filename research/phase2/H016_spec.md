# Phase 2 development specification: H016 (gross profitability)

- **Status: DRAFT, complete except §6.3** (prerequisite 7: the minimum-position and cash-rule conflict, P2-CP9a). It is frozen and hash-pinned (`qresearch.p2h016.SPEC_SHA256`, `tests/test_p2h016.py`) once the owner decides §6.3, and **before** the canary and any H016 run.
- **Implements:**
  - the owner's approval "Approve H016 Pre-Registration and Authorize Development Execution" (2026-10-02);
  - the P2-CP8 proposal (part B), as approved and clarified.
- **Programme:** P2, hypothesis 2 of 3. Slot 2 is consumed by the first candidate run (E016-01), not before.
- **Data:** fundamental-data infrastructure v1 exactly as frozen (`research/phase2/data_freeze_v1.json`, combined SHA-256 `1e98a816c0c7214ad1b0b583380c60b08f7cf400df4a759fcf90b20d713bed09`). `tests/test_data_freeze.py` must pass before and after every run. If the fingerprint changes: STOP.

## 1. Data categories

- **Development:** 2010-01-04 → 2021-12-31 (split `DEV`).
- **History-only warm-up:** 2008-07-01 → the run start. It accumulates fundamental history only: no decision, order, equity or evaluation (D114).
- **Holdout and unseen data:** locked.

## 2. Hypothesis (research/hypotheses/H016.md)

Among H016-universe stocks (§3), the 20 with the highest gross profits-to-assets, chosen quarterly from historically available data, earn a better risk-adjusted return than the equal-weight portfolio of the same universe, net of costs.

H016 has **one candidate**. Not allowed:
- no alternative GP/A definition;
- no cash-flow, ROA or ROE candidate;
- no value or momentum combination;
- no technical filter.

## 3. Universe on decision date T (identical for every book)

1. **Harness eligibility** (frozen): US common stock, NYSE/Nasdaq/AMEX, point-in-time market cap ≥ $2B, price ≥ $5, 20-day ADV ≥ $5M, with the SEC correction layer (`universe.sec_corrections`, table v3.2).
2. **Not financial and not REIT:** `qr_industry.classify` / `excluded` at T. This uses the SEC-assigned SIC at the latest visible filing: 6798 is REIT; 6000–6999 is financial, which covers banks, credit, brokers, exchanges, asset managers, insurers including health insurers, and real estate including real-estate services. Where no SIC is visible, the filing-structure rule applies.
3. **GP/A computable at T** (§4).

**Reporting:** universe size at each rebalance, yearly coverage, and the residual missing-company counts.

**Caveat** (owner item 9, recorded verbatim in substance):
- Candidate, benchmark and controls use the same reconstructed universe, which substantially reduces comparability bias.
- The remaining non-random missingness may still influence the measured profitability premium.

## 4. Measure

  **GP/A(T) = gross_profit_ttm4q(T) / total_assets(T)** (`qr_h016.gpa`)

- **gross_profit_ttm4q:** the frozen True TTM (four latest visible consecutive quarters; Q4 validated).
- **total_assets:** the current point-in-time report.
  - It must be the **same fiscal quarter** as the newest TTM quarter, otherwise there is no value.
  - It must exist and be > 0.
- **Negative gross profit** is allowed.
- **Freshness:** the frozen 200-day rule. Perturbation P6 uses 120 days.

**Every input is available strictly before T:**
- unit tests (incl. truncation);
- canary check `pit_violations` = 0.

## 5. Schedule and common evaluation start

**Run dates:**
- **Every H016 configuration:** `start` 2010-03-01, `warmup_start` 2008-07-01, `end` 2021-12-31, $100,000 (E016-08: $200,000).
- **Equity:** every book's equity begins on 2010-03-01, in cash.
- **Rebalance:** at the close of the first trading session of **March, June, September and December** (`qr_h016.is_rebalance_day`), executed at the next open by the harness. The first decision is 2010-03-01 and the first fills are on 2010-03-02.

**Common evaluation window for every comparative metric** (G1–G4, controls, diagnostics): **2010-03-01 → 2021-12-31**, identical for:
- the candidate;
- EW-H016;
- the random controls;
- the perturbations;
- SPY (E900-07) and the broad EW reference (E901-07), sliced to the same dates.

## 6. Portfolio and holding rules

### 6.1 Books

| Book | Positions | Selection at a rebalance |
|---|---|---|
| **Candidate** (`book` gpa) | 20 | The top 20 by GP/A, highest first; ties by security id |
| **Random control** (`book` random) | 20 | The top 20 by a **fixed seeded random key** per security (`qr_h016.random_key`: SHA-256 of "seed\|security id"). The same universe, schedule, rules and costs as the candidate; **only the ranking differs**. Seeds **1, 2, 3, 4, 5**, frozen now. |
| **EW-H016** (`book` ew) | Every universe member | Weight (1 − 2% buffer) / n on the first session of each month, 25% band, liquidate non-members. These are the approved B901 benchmark mechanics on the H016 universe, with a $10M paper notional. |

### 6.2 Trading rules (candidate and random controls)

- **Exits:** at a rebalance, every holding outside the new selection is sold, including those that left the universe or lost GP/A.
- **Entries:** selected names not held are bought in rank order at the equal slot weight (harness `slot_weight`, about 4.9% at $100K).
- **Funding:** D051 settled cash only, so entries not funded on the rebalance day are retried at each following close until the next rebalance.
- **Continuing holdings:** kept and not resized for drift.
- **Between rebalances:**
  - no exit for price, profitability or technical reasons;
  - delistings, acquisitions and untradeable holdings are handled by the frozen harness;
  - leaving the universe is acted on at the next rebalance.
- **Holding horizon:** unlimited. A name may stay held for longer than a year while it remains selected (owner item 5).
- **Costs:** $7 per order; 10 bps slippage per side.

### 6.3 Position-size and cash rule — OPEN (owner decision required, P2-CP9a)

**The approved combination cannot form the portfolio.** The combination is: 20 slots at $100K, a $4,500 minimum new position, and D051's 2% buffer and **15% gap reserve**.
- Every first entry of about $4,900 is scaled by the reserve to about $4,250.
- That is below $4,500, so it is skipped: **no position is ever opened** (`research/phase2/H016_position_rule_check.py`).

The owner chooses one option; the frozen version will record it here.
- **A** (recommended): the minimum new position is $4,000 and the 15% gap reserve is kept. A new position is **built** to its slot value from settled cash: it is topped up at following closes while below 90% of its slot value at entry, then never resized. Simulated: 20 positions, about 97.5% invested.
- **B:** a 5% gap reserve for H016 and a $4,500 minimum; no building. Simulated: 20 positions, about 93% invested.
- **C:** the approved rules unchanged, but only entries that settled cash funds at full size are submitted. Simulated: **19** positions, about 93% invested.

The chosen rule applies identically to the candidate, the random controls, the $200K sensitivity and the perturbations.

## 7. Committed and conditional runs (no others)

| ID | Kind | Book | Notes |
|---|---|---|---|
| E980-01 | infrastructure | **Canary (X980)**: S016 code, `book` random, **seed 0** (not a control seed), with canary checks | Verifies: universe, PIT timing (`pit_violations` = 0), no financial/REIT in the universe, the quarterly dates, 20 positions formed and the minimum-position rule, the common start (equity from 2010-03-01, first fills 2010-03-02), warm-up, the freeze test. It **never computes candidate (GP/A-ranked) performance**. |
| E016-01 | research | Candidate, $100K | **Consumes Phase 2 slot 2** |
| E016-02 | benchmark | EW-H016 | |
| E016-03 … E016-07 | benchmark | Random, seeds 1 … 5 | |
| E016-08 | sizing | Candidate, $200K | Sensitivity only: never decides, never rescues |
| E016-09 / 10 / 11 | research | Candidate, 2× / 4× / 6× slippage | Conditional (§9) |
| E016-12 … E016-17 | research | Perturbations P1–P6 | Conditional (§9) |

**Perturbations** (pre-declared; every other rule unchanged):

| ID | Perturbation |
|---|---|
| P1 | 15 slots |
| P2 | 25 slots, with the minimum new position scaled by 20/25 (needed for 25 slots to be fundable) |
| P3 | Rebalance months Jan/Apr/Jul/Oct (first decision 2010-04-01; cash before) |
| P4 | Rebalance months Feb/May/Aug/Nov (first decision 2010-05-03) |
| P5 | Semiannual, Mar/Sep |
| P6 | GP/A freshness 120 days |

All perturbations are evaluated on the common window against EW-H016 (E016-02).

## 8. Development gates (candidate E016-01, $100K, common window; all must pass)

Definitions are unchanged from `P2_spec.md` §7–§8: Sharpe = mean/std (ddof 1) of daily returns × √252; CAGR; max drawdown; Calmar.

- **G1:**
  - **G1.1:** Sharpe(H) − Sharpe(EW-H016) ≥ +0.25 **and** Sharpe(H) − Sharpe(SPY) ≥ +0.10;
  - **G1.2:** CAGR(H) ≥ CAGR(EW-H016) − 0.02;
  - **G1.3:** Calmar(H) ≥ Calmar(EW-H016);
  - **G1.4:** MaxDD(H) ≥ MaxDD(EW-H016) − 0.05.
- **G2:** Sharpe(H) > the **median Sharpe of the five random controls**. All five are reported individually, with their dispersion; they are never averaged into one stream.
- **G3:** the six two-year blocks (2010–11 starts 2010-03-01). Sharpe(H) − Sharpe(EW-H016) > 0 in at least 4 blocks; no block > 50% of the total excess return; total > 0.
- **G4:**
  - **(a)** at least 5 of 6 perturbations keep Sharpe − Sharpe(EW-H016) ≥ +0.10;
  - **(b)** at 2× slippage, Sharpe − Sharpe(EW-H016) ≥ +0.10;
  - **(c)** realised cost drag ≤ 1.5% a year at base costs.

A gate that cannot be evaluated fails. Thresholds are unchanged and are never weakened.

## 9. Conditional robustness

E016-09 … E016-17 are run **if and only if** the candidate passes G1, G2 and G3 on its base run. Otherwise G4(a) and G4(b) are "not run: candidate already failed". G4(c) is always evaluated.

## 10. Diagnostics (reported, never gates)

**Survivorship sensitivity** (owner item 10; frozen in `qresearch.p2h016`, inputs from the completed data audit only):
- **S1 (penalty):** each day of year y, the candidate's return is charged with penalty_y / 252, where penalty_y = max(0, measured availability bias_y) + 100 × (SEC-side unresolved share_y) × 0.397. Here 0.397 is the D043-measured return gap of later-distressed missing names, as a worst case that every unresolved company was a distressed name the candidate held. Sharpe(H′) − Sharpe(EW-H016) and G3's block view are then recomputed.
  - The yearly penalties are 0.24, 1.19, 0.42, 0.21, 1.31, 0.99, 0.54, 0.75, 1.85, 0.93, 0.20 and 4.36 points (2010 … 2021).
- **S2 (low-coverage years):** Sharpe(H) − Sharpe(EW-H016) from 2012-01-01. In 2010–2011, repaired companies are mostly unusable (XBRL phase-in).
- **Reading:** the conclusion is called fragile if S1 or S2 falls below the +0.25 margin while the base passes.

**DSR** (frozen D082 formula, programme-1 V[SR]) of E016-01's daily returns, with these N values:
- **P2 candidates:** N = 3 (H014 A, H014 B, H016);
- **P2 broad:** N = 3 + the robustness configurations run;
- **cumulative:** N = 43.

**PBO** (CSCV, 16 blocks):
- over the base run plus the six perturbations, if they were run;
- otherwise "not computable: single candidate".

**Other diagnostics:**
- paired block-bootstrap intervals (mean block 63, seed 20261004) for Sharpe(H) − Sharpe(X), with X = EW-H016, SPY and each random seed;
- per-year and per-block tables;
- turnover, exposure (invested share), mean and minimum cash, slot usage, orders and cost drag for every book;
- 4× and 6× costs;
- the $200K sensitivity;
- the broad EW (E901-07) reference;
- universe coverage per rebalance;
- **whether the ranking adds value:** candidate vs the random median and each seed, by block.

## 11. Classifications in the report

| Class | Condition |
|---|---|
| **Profitable** | CAGR > 0 net of costs |
| **Benchmark-beating** | G1 passes |
| **Random-control-beating** | G2 passes |
| **Development-qualified** | G1–G4 all pass. Only then may Holdout access be requested. |

## 12. Prohibitions

- No change to GP/A, the universe, the schedule, the portfolio rules, the controls, the seeds, the gates or the diagnostics after any H016 result.
- No other metric, factor or filter.
- No runs outside §7.
- No Holdout, unseen or forward data.
- The data infrastructure v1 stays unchanged. A genuine bug means: stop, document, preserve the affected runs, and ask the owner.
- Every run and failure is kept in `experiments/INDEX.csv`.
- Stop after the development checkpoint.
