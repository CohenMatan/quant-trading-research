# TT-CP1 — Technical Trading Research — Phase 1: Prior Research Audit and New System Architecture

- **Decision trail:** D292 is the owner direction (verbatim in `docs/owner/2026-10-23_technical_trading_programme_phase1.md`). This document is D293.
- **This is design and audit only.** No hypothesis registered (no H033), no strategy implemented, no backtest or performance calculation, no indicator or parameter search, no chart sampling, no Holdout access, no constraint change, no purchase, no trading or broker work.
- **Labels used throughout:**
  - **[F]** a fact demonstrated by our own records (repository reference given);
  - **[L]** external literature (author / year; not re-verified here);
  - **[A]** an assumption;
  - **[P]** a proposal, not approved.
- **Unchanged:** H018, H028 and H032 REJECTED / CLOSED; H031 parked; RR6 INCONCLUSIVE; Holdout sealed.

## 0. Short answer to the final research question

**A disciplined, price-and-volume trading system can be designed. Today it cannot be tested credibly.**
- **What remains open:**
  - Our records leave exactly one legitimate open question: the **holding / exit / portfolio architecture**. That means open-ended trend participation, no time cap, winners allowed to run, risk-budgeted sizing and an after-tax objective.
  - It has never been run [F]. Its **entry** family (trend, momentum, breakout) has been tested many times here and found no signal [F].
  - So it is "a new holding, exit and portfolio architecture paired with a previously tested entry family", not a new entry idea.
  - The same architecture was already designed in P4-CP1 and set aside for lack of statistical power [F].
- **Binding constraint: evidence, not ideas.**
  - 2010–2021 is spent.
  - The Holdout is one shot of 4.7 years.
  - A forward test needs a decade or more to separate a modest edge from luck.
  - The only possible extra historical evidence is **1999–2009**. It can only be used if a **price- and volume-defined universe** (no market caps exist before late 2009 on QuantConnect) passes an audit.
- **Phase 2 as specified is blocked.** Claude viewing historical charts built from QuantConnect data would send QuantConnect-derived images to an external AI, which the data licence and D151 forbid.
- **Recommendation:**
  - Do not start Phase 2 yet.
  - First approve a narrow **Phase 1b**: a 1999–2009 universe-feasibility audit (aggregate-only, no returns) plus the owner decisions in §11.
  - **If Phase 1b fails, stop the technical programme.** Without an independent window, only very large edges could ever be confirmed.

## 1. Prior technical research audit

### 1.1 Entries, holds and exits actually tested

All at ≥ $2B (except where noted), long-only, signal at the close and fill at the next open, $7 per order, 10 bps per side.

| Test | Entry / selection | Holding and exit | Result | Records |
|---|---|---|---|---|
| H001 v1.0–v1.4 | RSI(2) < 10 / < 5, or 3-day return ≤ −6%, with close > SMA200; v1.3 SPY > SMA200 regime | close > SMA5, or 10-day time stop; v1.2 time stop only | CAGR −4.7% to 13.5%, Sharpe −0.45 to 0.69 vs EW 0.91 → **REJECTED** | `research/hypotheses/H001.md`; CP3 §6; D067 |
| H002 v1.0–v1.3 | Top 15 by 12-1 or 6-1 momentum; v1.2 regime filter | Monthly / 2-monthly rebalance, 25% band | Sharpe 0.38–0.56 → **REJECTED** | `H002.md`; CP3 §6 |
| H003 v1.0–v1.2 | 15 names nearest the 52-week high | Monthly / 10-day rebalance | Sharpe 0.14–0.74, about 49% invested → **REJECTED** | `H003.md`; CP3 §6 |
| H004 v1.0–v1.3 | Top-20% 126-day leaders after a 5% or 8% 5-day pullback | 10- or 20-day time exit | Sharpe 0.03–0.46, drawdown to −53% → **REJECTED** | `H004.md`; CP3 §6 |
| H005 | 15 lowest-volatility names | Monthly rebalance | Passed the in-sample screen; **failed Validation** 2018–2021 → **REJECTED** | CP4; D056, D060 |
| **H006 v1.0–v1.2** | Close > prior 55-day (or 252-day) high, volume ≥ 1.5× 50-day, close > SMA200 | **Chandelier trailing stop**: close < highest close since entry − 3 × ATR20; **60-session time stop**; 10 slots | Sharpe 0.74–0.90 vs EW 0.92; CAGR 9.8–12.3% vs 13.9% → **REJECTED** | `H006.md`; `CP3c_C02_final_report.md` |
| H007 v1.0–v1.2 | Volatility contraction then expansion (close > upper band, range and volume expansion) | Close < SMA20 (from day 5) or 40-session stop | v1.1 passed the screen (Sharpe 1.12 at 21% invested), **failed robustness** (5 of 8) → **REJECTED** | `H007.md`; CP3c |
| H008 | Residual (market-adjusted) momentum, top 10 | Monthly, keep band top 20, daily refill | Sharpe 0.57–0.69 → **REJECTED** | `H008.md`; CP3c |
| H009 | Volume shock with a small price move | Fixed 20 / 40 sessions | Sharpe 0.67–1.01, near miss by 0.01–0.02 → **REJECTED** | `H009.md`; CP3c |
| H010 | Gap ≥ 2% / 1.5 ATR held into the close, volume ≥ 2× | Gap-fill invalidation or 40 / 60-session stop | Sharpe 0.51–0.68 → **REJECTED** | `H010.md`; CP3c |
| H011 | Same-calendar-month seasonality | Monthly | **REJECTED** | `H011.md`; CP3c |
| H012 | Volatility-managed exposure | — | **REMOVED untested** (power) | D087 |
| H013 | Random entries excluding lottery stocks | Fixed 60 sessions | **REJECTED** (refuted) | CP3i |
| **H014** | Trend (close > MA200, MA50 > MA200) + pullback + recovery (RSI14 > 45, close > prior high); ranked by 12-1 momentum | **Close < MA200**, or 63 sessions (A, with horizon roll) / 126 sessions (B) | Sharpe 0.64 vs EW 0.80, SPY 0.91 → **REJECTED** | `H014.md`; `P2_CP1_H014_development_checkpoint.md` |
| **H015** | Close > SMA200 at monthly review, random fill | **Exit only at close ≤ SMA200; no time stop** | **NOT ADOPTED — never run** | `H015.md`; D104 |
| **H018** | 1,533 configurations: trend (T1–T3), momentum (M1–M3), breakout (B1), pullback (R1–R3) × confirmation × volatility filter | **Fixed 63 sessions**, 10 slots. Stage 2 (63 / 126, reversal exit, 3 × ATR14 trailing stop, regime overlay) **removed before the run** | T = 0.0127 vs τ 0.0284, p 0.31; walk-forward −6.8% vs SPY → **CLOSED: No Production Candidate Found** | `research/phase3/P3_spec.md` §4, §6; `P3_CP3_systematic_search_stage1_result.md`; D139 |
| P4-CP1 (design) | Weekly trend state + momentum ranking (240 configurations) | **Trend-state exit, no fixed horizon (weeks to over a year)** | **Never implemented**: 50% power needs a 6–8% a year edge (9–12% for the full chain) vs a plausible 0–3% | `P4_CP1_weekly_trend_momentum_architecture.md`; D140 |
| H019 | 12-1 momentum, smooth momentum, Han–Zhou–Zhu trend factor (signal test) | 1-month forward return | Top decile −2.2 / −1.2 / −2.9% a year; t ≤ 0.34 → **NO SIGNAL QUALIFIED** | `research/phase4/P4_xs_spec.md`; `P4_CP4_…results.md` |
| H020 | Deterministic chart score (swings, HH/HL, zones, bases, breakouts; `qr_chart`) | 4-week forward return | t_IC 0.27, High −0.38% a year → **REJECTED** | `research/phase5/H020_spec.md`; `P5_CP3_…results.md` |
| H021-A | Sector-ETF 6-month relative momentum, 2000–2017 | 1-month | t −0.35 → **REJECTED** | `P6_CP2_…result.md` |
| H026–H028 | Learned scores including technical features (MOM, LOWVOL, REV1M, HI52) | Monthly Top-15 | Edge explained by low-volatility exposure → **REJECTED** | P11–P13 checkpoints |

### 1.2 Answers to the owner's seven questions

1. **Entry rules tested** [F]: everything in §1.1, with no other technical families:
   - short-term reversal / oversold;
   - pullbacks in leaders;
   - 12-1, 6-1, residual and smooth momentum;
   - 52-week-high proximity and new-high breakouts (with and without volume);
   - volatility contraction / expansion;
   - volume shocks; gaps;
   - moving-average trend states and crosses, MACD / ADX / RSI confirmations;
   - trend factor, chart-geometry score, sector momentum, seasonality, low volatility.
2. **Holding and exit mechanisms used** [F]:
   - fixed time exits (10, 20, 40, 60, 63, 126 sessions);
   - mean-reversion exits (close > SMA5, close < SMA20);
   - one trailing stop (H006: 3 × ATR20 chandelier, capped at 60 sessions);
   - invalidation exits (gap fill, close < MA200), always with a time cap;
   - periodic rank rebalancing (monthly / 2-monthly / 10-day, with bands);
   - signal-level tests at 1-month or 4-week horizons.
3. **Never tested** [F]:
   - any exit **without a time cap** (H015 and P4-CP1 designed it, never ran it);
   - a trailing stop without a time cap;
   - swing-structure exits (break of the last confirmed higher low);
   - letting winners grow, or adding to them;
   - variable position counts and risk-budgeted (volatility-aware) sizing (all books used equal slots);
   - SPY for idle capital (SYS-1 platform-blocked);
   - after-tax evaluation;
   - any pre-2010 stock-level test.
4. **Rejected vs inconclusive** [F]:
   - Every tested technical entry is formally **rejected**, except H019 ("no signal qualified", no separate owner closure).
   - H012 was removed and H015 never adopted; both are **untested**, not rejected.
   - Almost all tests were **underpowered for modest edges** (detectable edges of about 4–15% a year), so "rejected" means "no large edge", not "no edge".
5. **Configurations especially vulnerable to overfitting** [F]:
   - H018's apparent winners: best fold-median score +5.5% a year for SMA50 > SMA200 with close within 10% of the 252-day high; PBO 0.61;
   - H007 v1.1 (21% invested, robustness 5 of 8);
   - H005 (PBO 0.71, failed Validation);
   - H014's A / B choice by halves.
   - **None may be reused as a candidate.**
6. **What the H018 null teaches** [F] (`P3_CP3…` §15):
   - In **every one of 500 no-edge worlds**, the optimizer's best configuration beat SPY over 2010–2017, by a median **+6.8% a year** (wealth 1.57× SPY's).
   - 98.8% of fake worlds contained an "apparently robust" cluster.
   - The real search sat at the null's 69th percentile.
   - **Lesson:** a historical trend / breakout winner in this market carries no evidence by itself. Only a single pre-registered rule, judged against a null that reproduces the search, is evidence.
7. **Genuinely different open questions**:
   - (a) open-ended holding and exit architecture with right-tail capture;
   - (b) portfolio construction: variable count, risk-budget sizing, SPY for idle capital;
   - (c) evidence from a different regime (1999–2009, with two deep bear markets);
   - (d) after-tax wealth as the objective.
   - **Not different:** any new combination or parameter of the trend / momentum / breakout / pullback / oscillator entries already tested.

### 1.3 How to classify any future proposal (owner's categories)

| Category | Example | Status |
|---|---|---|
| Genuinely new architecture | None available from price / volume alone in our records | — |
| New exit mechanism with a previously tested entry | Open-ended trend participation (§10) | The only legitimate candidate; must say so openly |
| Parameter variation of a rejected strategy | H006 with K = 4, H014 with MA150, any H018 grid cell | Not allowed |
| Same hypothesis renamed | "Momentum leaders with trend filter", "52-week breakout system" | Not allowed |

## 2. Remaining research opportunities

| Question | Why it is different | Prior | Testable? |
|---|---|---|---|
| **Q1: Open-ended trend participation** (enter on trend, hold while the trend holds, no time cap, winners run) | Exit / hold / portfolio architecture never run [F]. Targets the right tail of long-horizon stock returns, where a few stocks create most wealth (Bessembinder 2018 [L]), rather than next-month predictability, which we rejected | **Low–moderate**: trend and momentum show no signal here at 1 month [F]; trend following works across asset classes (Hurst, Ooi & Pedersen 2017 [L]); stock-level evidence is mostly practitioner [L] | Only with an independent window (§9) |
| Q2: Risk-budgeted, variable-count sizing | Never run [F] | Changes risk and cost, not information (P4-CP1 [F]) | As a pre-specified decomposition inside Q1 only |
| Q3: SPY for idle capital | Never run (SYS-1 blocked) [F] | Removes cash drag; adds no alpha (SA-CP1 [F]) | Mechanical; decided on economics (§7) |
| Q4: Structure-based exits (swing lows, bases) | Vocabulary exists in `qr_chart` (synthetic-tested) [F]; never used as an exit | Unknown | Inside Q1 as one pre-specified rule, not a search |

## 3. Chart analysis methodology (for any future Phase 2)

**Blocker** [F]: a chart reproduces raw OHLCV.
- QuantConnect's licence forbids exporting it.
- The owner's D151 rule forbids sending QuantConnect- or OHLCV-derived images to an external AI.
- P5-CP1 also notes that current Claude models offer no temperature control and are retired over time, so visual judgements are not reproducible.
- **Claude may not view historical charts built from our QuantConnect data.**

**Options (owner decision O2):**

| Option | What it is | Cost / caveat |
|---|---|---|
| **V1 (recommended)** | No historical-chart viewing. The vocabulary comes from the literature and the deterministic definitions already implemented in `qr_chart`. Claude reviews **synthetic** charts (`qr_chart_render`, byte-deterministic) to check that each definition behaves as intended | $0; no licence issue; no outcome leakage |
| V2 | Charts from a source whose terms permit AI analysis, sampled by a frozen procedure | Licence check needed; free sources usually lack delisted names (survivorship); any purchase is a separate decision |
| V3 | The owner views charts on their own broker platform and gives written observations | Not reproducible; vocabulary input only |

**Rules if any historical chart is ever viewed (V2 / V3)** [P]:
- **Sample frozen before viewing:** stratified random draw by year, liquidity bucket, sector, prior-12-month return quintile, and outcome-unknown status. It includes delisted and acquired names, failed setups and bear-market dates. The seed and list are committed first.
- **Blindness:** bars only up to the decision date; no ticker, date or later candles shown.
- **Outcome-blind labelling:** labels recorded and committed before any outcome is revealed.
- **Exploratory only:** anything seen defines vocabulary. It is never test evidence, and the viewed dates and stocks are excluded from any later evaluation of the same rule.

## 4. Technical vocabulary (measurable definitions) [P]

All definitions use daily bars ≤ t, total-return adjusted (RAW × QuantConnect's split and dividend feeds, as verified in E985-05 [F]) and ISO-weekly aggregation. Most are already implemented and leakage-tested on synthetic data in `qr_chart` / `qr_p3_features` [F].

| Concept | Measurable definition |
|---|---|
| Trend state | Close > SMA200 and SMA50 > SMA200; slope = SMA200(t) / SMA200(t − 21) − 1 > 0 |
| Market structure | Confirmed fractal swing highs / lows (k bars each side, ATR prominence); **uptrend structure** = last two confirmed swing lows rising and last swing high exceeded (`qr_chart` HH / HL states) |
| Trend continuation | Structure still up and close above the last confirmed higher low |
| Relative strength | RS line = stock total return / SPY total return; RS(K) = RS change over K sessions; RS at a K-session high |
| Volatility | ATR(n) / close; realised 63-day volatility; contraction ratio ATR10 / ATR100 |
| Breakout | Close > highest close of the prior N sessions (or a `qr_chart` base high) by ≥ x × ATR |
| Volume confirmation | Volume / 50-day average volume ≥ v |
| Extension | (close − SMA50) / ATR |
| Invalidation | Close below the base low or the last confirmed swing low |
| Exits | Chandelier: close < highest close since entry − K × ATR; structure exit: close < last confirmed higher low; trend-state exit: weekly close < SMA200 |

**Execution:** every exit is decided at a close and filled at the next open. **No intraday stop price is ever assumed;** gaps are taken at the open.

## 5. Portfolio construction (principles fixed before any return) [P]

1. **One primary rule set, chosen on economics and implementation limits, never on returns.** Any alternative is a single pre-declared decomposition comparison, never a grid.
2. **Position count variable**, set by valid signals within [0, N_max].
   - N_max follows from cost and breadth. At $100,000 with $7 per side, a $5,000 position costs 0.28% round trip, so N_max ≈ 20 at full investment.
   - About 20 names remove most diversifiable risk (Statman 1987 [L]) and widen the chance of holding a rare long-run winner (Bessembinder 2018 [L]).
3. **Sizing: equal initial risk.**
   - Shares = r × equity / (K × ATR), so a stop-out loses about r of equity.
   - Bounded by a $5,000 minimum and an initial maximum of about 8–10% of equity.
   - Rationale: volatile names do not dominate risk. One equal-weight decomposition comparison is pre-declared.
4. **Winners may grow.** No trimming below a hard concentration ceiling of about 20% of equity (ruin control). Trimming realises taxable gains (§8), so the ceiling is high and the only one.
5. **Concentration:** at most about 35% of equity in one FF12 sector **at entry** (no forced sales). Correlation is controlled through the sector cap and the breadth of N_max.
6. **Capital allocation:**
   - When signals exceed capacity, a pre-declared priority applies (e.g. relative strength) with ties by identifier.
   - New positions are funded from cash or the SPY sleeve only.
   - **No replacement of healthy holdings** (churn and tax); holdings leave only through their exit rule.
7. **Gap and liquidity risk:** next-open fills; order ≤ 1% of ADV20 (non-binding at $100,000 for ≥ $2B names).
8. **Forced events:** splits, dividends, acquisitions, delistings and stale data handled as in the verified harness (D054, D059, D062) [F].

## 6. Universe feasibility

- **Current ≥ $2B universe (2010–2021):** usable but imperfect [F].
  - The vendor-cap view passed RR3.
  - The 2010–2015 survivorship audit failed (3.5–6.1% of names missing; RR5).
  - The SEC repair left it INCONCLUSIVE (RR6).
  - **It cannot be extended before late 2009** (no point-in-time market caps; U-B invalid; RR3 W0 FAIL).
- **A price- and volume-defined universe** [P] would be fully point-in-time from prices and volume alone. Example: US common stocks, price ≥ $5, top N by 63-day median dollar volume.
  - It is consistent with a price-and-volume-only programme.
  - It is the **only way to reach 1999–2009**.
  - **Open issues** (audit, not assumption):
    - (a) common-stock classification before 2009: names without fundamentals are unclassifiable (ETFs, ADRs, closed-end funds, preferreds) — RR3 [F];
    - (b) completeness of delisted coverage before 2009 (RR3 shows exits exist [F], completeness unknown);
    - (c) the overlap with the ≥ $2B universe after 2010.
  - Any change needs owner approval; it must not be judged on returns.
- **Smaller caps:** not recommended. Wider spreads and worse survivorship; no economic reason specific to this architecture.

## 7. Market exposure: cash vs SPY for idle capital

| | A. Cash | B. SPY |
|---|---|---|
| Economics | Few signals → large cash share. Becomes implicit market timing: cash drag ≈ idle share × equity premium, compounding over decades [A] | Full market exposure at all times; the stock book is an active overlay on SPY. Removes cash drag; adds no alpha |
| Drawdowns | Lower in bear markets (trend exits push to cash) | About SPY's; the defensive feature of trend systems is given up unless SPY itself has an exit rule |
| Taxes | Cash earns little; no forced realisation | Selling SPY to fund entries **realises SPY gains** (tax drag) |
| Evidence | Market timing: no support in our records [F] | SA-CP1 [F]: the evidence ratio of the active part is unchanged by the core |

**Recommendation [P]:**
- **B for a terminal-wealth objective.** The owner explicitly rejects defensive designs that sacrifice wealth, and nothing in our evidence supports market timing.
- Fund entries from SPY lots with the highest cost basis first, to limit realised gains.
- **Owner decisions needed (O6):**
  - SPY as a holding (ETF scope);
  - its exemption from position-count and 10% limits (OD-1 precedent, SYS-1 only);
  - whether a SPY trend exit is tested as **one pre-declared diagnostic** (not recommended as the primary).

## 8. Cost and tax framework

**Costs** [F / P]:
- $7 per buy and per sell, as in all prior work.
- 10 bps per side for ≥ $2B names; a spread model is needed if liquidity floors change.
- Stop exits at the next open, including gaps.
- No fractional shares.

**Taxes — illustration of why holding period matters** [A, arithmetic only]:
- Assume SPY earns 10% a year, deferred 30 years and taxed 25% at liquidation. The after-tax multiple is about 13.3×.
- A strategy realising all gains every year at 25% must earn about **12.0% pre-tax** to match.
- **A high-turnover strategy therefore needs about 2 points a year more pre-tax just to break even after tax.** Low turnover and long holds are an economic requirement, not a preference.

**To confirm before any after-tax result is final** (owner decision O7):
1. The tax rate on realised gains (25% preliminary) and whether real (inflation-adjusted) or nominal gains are taxed.
2. The currency of computation (USD vs ILS) and FX treatment.
3. Loss offsets: same-year netting, carry-forward rules, and whether losses offset dividends.
4. Dividend tax and US withholding / treaty credit.
5. Account type and whether the broker applies a tax shield automatically.
6. The terminal-liquidation convention (both strategy and SPY liquidated and taxed at the end).

**Reporting:** pre-tax and after-tax wealth, CAGR, costs, tax drag and turnover, against SPY under identical assumptions.

## 9. Validation architecture

| Evidence source | Status | What it can show |
|---|---|---|
| 2010–2021 | Spent (D261; H018 searched trend / breakout rules on 2010–2017) [F] | Mechanics and fidelity only |
| **1999–2009** | Unused for stock selection internally [F]; needs the §6 universe audit and a D035 amendment | Two bear markets: the most informative regime for an exit architecture |
| Holdout 2022-01 → 2026-08 | Sealed; one candidate programme-wide (D267) [F] | One confirmatory look |
| Forward paper trading | After a freeze | True out-of-sample, but slow |

**Power** [A, illustration]: with tracking error 8% and true edge α, t ≈ α√T / 8%.

| True edge α | 11 years (1999–2009) | 11 years + Holdout (15.7 years) |
|---|---|---|
| 3% a year | t ≈ 1.24 | t ≈ 1.48 |
| 5% a year | t ≈ 2.07 | t ≈ 2.47 |

- **Only edges of about 5% a year or more are confirmable** even in the best case.
- Without 1999–2009, nothing below about 7–8% a year is confirmable (Holdout alone, t ≈ 2) before the forward test matures.

**Pre-specified decomposition** (one comparison each, no searches):
- strategy vs SPY;
- entries vs matched random entries with identical holds, exits and sizing (the entry's value);
- exit rule vs one pre-declared reference exit (the exit's value);
- risk-budget vs equal sizing;
- beta and sector attribution.

**Stop conditions:**
1. The §6 audit fails (no credible 1999–2009 universe) → stop the programme. Forward-only research could not confirm a realistic edge within a reasonable horizon.
2. The power analysis at Phase 4 shows < 50% power at the pre-declared effect size → stop.
3. Any integrity, point-in-time or corporate-action failure → stop and report.

## 10. One preliminary research direction (if the owner continues)

**TP-1 — Open-ended trend participation with right-tail capture [P]:**
- **Entry:** one pre-declared trend-continuation trigger, for example a new N-session high close in an established uptrend with positive relative strength. **Honestly classified as a previously tested family.**
- **Hold:** while the trend structure holds. No time cap.
- **Exit:** one structural / volatility exit, for example a chandelier stop or a break of the last higher low, at the next open.
- **Sizing:** risk-budget, variable count ≤ about 20.
- **Idle capital:** SPY, if approved.
- **Objective:** after-tax wealth.

**Economic rationale:**
- Long-horizon single-stock returns are extremely right-skewed [L].
- Under-reaction and slow information diffusion keep trends alive (Jegadeesh & Titman 1993; George & Hwang 2004 [L]).
- The disposition effect makes investors sell winners early (Frazzini 2006 [L]); a system that never caps winners may harvest the right tail that equal-weight monthly rebalancing and 63-session exits cut off.
- Long holds also minimise tax drag (§8).

**Against:**
- Its entry family failed here at every short horizon [F].
- P4-CP1 found its search version underpowered [F].
- Momentum crashes (Daniel & Moskowitz 2016 [L]).
- 2010–2021 mega-cap trends flatter it in hindsight, which is why that period is not evidence.

**Prior: low to moderate.** It is the only architecture in our records that is untested and economically coherent with a 20–30-year after-tax objective.

## 11. Owner decisions required before Phase 2

| # | Decision | Recommendation |
|---|---|---|
| O1 | Continue with TP-1 as the single direction, or stop | Continue only through Phase 1b (O3); stop if it fails |
| O2 | Chart-analysis source | V1: no historical charts; synthetic charts and deterministic definitions only |
| O3 | Approve **Phase 1b**: one aggregate-only QuantConnect audit of a price / volume-defined universe 1999–2021 (classification, delisted coverage, counts; no returns), with a pre-registered pass rule | Approve |
| O4 | In principle: a price / volume-defined universe for the technical programme, and a D035 amendment making 1999–2009 its confirmatory window if O3 passes | Decide after O3 |
| O5 | Scope: holding periods of months to years (beyond D094) for this programme | Approve in principle |
| O6 | SPY for idle capital (ETF scope, exemption from position-count / 10% limits) | Approve in principle, decided before Phase 3 |
| O7 | Tax facts (§8 items 1–6) | Provide; until then results reported pre-tax plus a clearly labelled 25% illustration |
| O8 | Governance: one primary specification, pre-declared decomposition, no searches, Holdout once, forward paper trading with separate model / approved-trade records | Approve |

**Not proposed now:** recommendation format, approval workflow, expiry of delayed approvals and broker integration (Phase 6 topics; nothing built).

## 12. Totals and status

- **Hypotheses:** no hypothesis registered (31 registered; H031 parked).
- **Records:** 588 experiments logged; no production candidate.
- **Nothing was run, built, searched, viewed or bought.**

**STOP:** awaiting the owner.
