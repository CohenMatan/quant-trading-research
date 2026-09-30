# Phase 2: Technical trend + pullback + recovery. Research proposal (P2-CP0)

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **PROPOSAL ONLY. STOP.** Nothing is implemented, no strategy backtest has run, and no Validation, Walk-Forward or Holdout data was used. |
| Programme | **A new research programme ("Phase 2", P2)**, separate from C01–C03 (closed: No Production Candidate Found). It is not "C04". |
| Supporting work | `research/phase2/P2_literature_review.md` (external evidence, conventions and our own hypotheses kept apart); `research/phase2/P2_feasibility.py/.json` (costs vs holding period, DSR hurdles, statistical power; uses no new market data). |
| Draft hypothesis | `research/hypotheses/H014.md` (status: PROPOSED) |

## 0. Summary

- **One hypothesis (H014), with two exit variants.** Stocks in an established uptrend are bought only after a pullback **and** an objective recovery, then held for months.
- **Three controls isolate the claim that the entry timing adds value:**
  - the same uptrend stocks bought **without** waiting for a pullback;
  - the pullback bought **without** waiting for recovery;
  - **random** stocks from the same uptrend set.
- **Low turnover by design:** holds of about 63–126 sessions. The estimated cost is about 1.0–1.5% of equity a year at $100K with 12 positions. Holds of 40 sessions or fewer would break the target (about 2%).
- **The honest risk.**
  - With 8 years of development data, even a real improvement of 0.2–0.3 Sharpe over the trend-only control would be demonstrated only about 20–60% of the time.
  - If the old programme's 40 trials are carried into the DSR, the bar is about Sharpe 1.45 over 2010–2021, which is unlikely for any long-only 12-stock book. **The trial-count decision (§13) largely decides whether this programme can succeed at all.**

## 1. The hypothesis (H014)

> Among US common stocks with point-in-time market cap ≥ $2B that are in an established uptrend, buying after a temporary pullback **and** an objective recovery produces higher risk-adjusted returns, net of realistic costs, over the following months than:
>
> - (a) buying the same uptrend stocks without waiting for a pullback;
> - (b) buying at the pullback without waiting for recovery;
> - (c) random selection from the same uptrend stocks.

**The claim to test is the entry timing inside an uptrend**, not "uptrend stocks rise". Controls (a)–(c) make that separable (§9).

## 2. Economic and behavioural rationale

1. **Trend continuation.** Stocks with strong 3–12-month performance tend to keep outperforming for months (Jegadeesh & Titman 1993). The usual explanations are under-reaction and gradual diffusion of information. This is where the holding-period return is expected to come from.
2. **Temporary pullbacks.**
   - Short-term price pressure (liquidity-demanding selling, profit-taking) partially reverses (Jegadeesh 1990; Lehmann 1990).
   - Buying during such a dip, **inside** a still-intact long-term trend, may give a better entry price for the same continuation.
3. **Recovery confirmation.** A dip can also be the start of a real trend break (new information).
   - Waiting until selling pressure visibly abates (RSI back above 45, and a close above the prior day's high) is meant to avoid "falling knives".
   - It sacrifices part of the bounce in exchange for fewer entries into genuine breakdowns.
   - **This is our own hypothesis, not an established finding.**
4. **What we should not expect.** Short-term reversal is weak in large, liquid stocks (Avramov, Chordia & Goyal 2006), and our own H001 confirmed it after costs. So the design does not rely on the bounce itself.

## 3. External research

See `P2_literature_review.md`. Three points matter most for the design:

- **Supported:** multi-month continuation in winners (pre-2010); the value of skipping the latest month in momentum measures.
- **Warned:**
  - technical-rule profits largely vanish after data-snooping correction (Sullivan, Timmermann & White 1999; Park & Irwin 2007);
  - high-turnover anomalies do not survive costs.
- **Conventions only, with no evidence for the specific values:** RSI(14), the 40/45 thresholds, the 5-day window, 50/200-day averages as a stock filter, "close above yesterday's high". These are fixed now, by convention, and **never optimised**.

## 4. Entry rules (deterministic; all computed from completed daily bars up to the close of day T)

**Universe.** Unchanged: US common stock, primary share class, NYSE/Nasdaq/AMEX, point-in-time market cap ≥ $2B, price ≥ $5, 20-day average dollar volume ≥ $5M.

**Trend filter (all conditions at T):**

- **U1:** Close(T) > MA200(T)
- **U2:** MA50(T) > MA200(T)

Both use simple moving averages of split- and dividend-adjusted closes.

**Pullback:**

- **P:** min RSI14 over sessions T−5 … T−1 ≤ 40

This is Wilder's RSI(14) on adjusted closes. The pullback must be recent (within the previous 5 sessions) and must precede the recovery day.

**Recovery on day T:**

- **R1:** RSI14(T) > 45
- **R2:** Close(T) > High(T−1), using adjusted OHLC
- The trend filter must still hold on day T.

**Signal and execution.** The signal is formed after the close of T. The order is a market-on-open order for T+1: never at T's close, and never earlier.

**Why each condition is there:**

| Condition | Economic role | Different from the others? | Evidence before our period | If removed |
|---|---|---|---|---|
| U1 Close > MA200 | The long-term trend is intact | Partly overlaps U2 | Brock et al. 1992; Faber 2007 (index level) | Admits stocks in long-term downtrends; changes the hypothesis |
| U2 MA50 > MA200 | The trend is established for months, not a fresh spike | Adds persistence beyond U1 (e.g. excludes a stock just popping above MA200 after a long decline) | Convention; Grinblatt & Moskowitz 2004 (consistency) | A slightly broader, less "established" trend. Acceptable, but it is the owner's stated concept. |
| P RSI ≤ 40 within 5 days | A temporary dip inside the trend | Distinct from U1/U2 (short horizon) | Convention (Wilder 1978, "range shift") | Becomes control (a), trend-only |
| R1 + R2 recovery | Selling pressure has abated | Distinct from P (it is the rebound) | Our own hypothesis | Becomes control (b), pullback-without-recovery |

**Medium-term momentum** is used **only as the ranking** (§7), not as another filter.

- As a filter, 12-1 momentum > 0 largely duplicates U1/U2 (both describe a 6–12-month uptrend), which would be indicator stacking.
- As a ranking it has the strongest pre-2010 evidence and a clear role: among simultaneous signals, prefer the strongest trends.
- **It does not reintroduce H002.** H002 held the top-momentum names continuously; here momentum only orders stocks that have produced a pullback-and-recovery signal. The trend-only control (a) **is** essentially an H002-like book, which makes the comparison explicit.

**Excluded:** Fibonacci retracements, trend lines, MA20, volume confirmation (reasons in the literature review §2). Volume is reported as a diagnostic only.

## 5. The recovery definition

Your worked example becomes this deterministic check at the close of day T:

- min(RSI14 over T−5 … T−1) ≤ 40 (e.g. 38 on T−3 and 36 on T−2);
- RSI14(T) > 45;
- Close(T) > High(T−1);
- U1 and U2 hold at T.

The signal is formed after T's close, and the buy executes at T+1's open. If the recovery comes more than 5 sessions after the last RSI ≤ 40, there is no signal. No subjective reading is involved.

## 6. Exit rules (two conceptually different variants)

**Both variants:**

- Exits are signals at T's close and execute at T+1's open.
- A position is also closed if the stock leaves the eligible universe or is delisted (existing harness handling).

**Variant A: fixed horizon with a trend-failure override** (primary).

- Exit after **63 sessions** (≈ 3 months, a standard Jegadeesh–Titman holding period). Exit earlier at the first close with **Close < MA200**, when the premise has failed.
- **Horizon-roll rule:** if at the 63-session exit the same stock would be bought again that day under the same entry rule, it is kept and its clock restarts. This avoids a sell-and-rebuy that only generates costs, and the same rule applies to every book.

**Variant B: pure trend-failure exit.**

- Exit at the first close with **Close < MA200**, or after **126 sessions** (≈ 6 months, also a standard momentum horizon) at the latest.

**Rules deliberately not included:**

- **No separate percentage stop-loss.** Close < MA200 is the premise-based protective exit. Kaminski & Lo (2014) show arbitrary stops cost return unless returns are serially dependent.
- **No exit on Close < MA50.** A pullback often takes the price to or below MA50, so that rule would sell right after entry. It conflicts with the hypothesis.

## 7. Portfolio construction

| Item | Proposal | Why |
|---|---|---|
| Positions | **12 slots**, equal weight (about 8.2% ≈ $8.2K at $100K) | Middle of your 10–15 range. Our diagnostics (C03 series) showed more names buy little diversification at this capital, while fewer names raise idiosyncratic noise. |
| Minimum position | $5K for new positions (unchanged) | Not binding at about $8.2K. Binds only after an equity drawdown of about 40%. |
| Maximum weight | 10% (unchanged) | |
| Cash rules | D051: buy only from settled cash; 2% buffer; 15% gap reserve (unchanged) | |
| Refill | Each close, free slots are filled from that day's signals | |
| Ranking | **12-1 momentum** (return from T−252 to T−21), highest first; ties by security id | One defensible ranking with the strongest prior evidence. It skips the latest month, so it is independent of the pullback itself. |
| Re-entry | A sold stock may re-enter only on a new signal (Variant A's horizon roll excepted) | |

$200K runs are a pre-declared **sensitivity only**, with the same rules and 12 slots (positions about $16K). They are never used for selection.

## 8. Turnover and costs (from `P2_feasibility.json`)

Model: 12 slots, 85% invested, $7 per order, 10 bps slippage per side, $100K equity.

| Average holding period | Round trips a year | Commission drag | Slippage drag | Total a year |
|---|---|---|---|---|
| 20 sessions | 129 | 1.8% | 2.1% | 3.9% |
| 40 | 64 | 0.9% | 1.1% | 2.0% |
| **60** | **43** | **0.6%** | **0.7%** | **1.3%** |
| **80** | **32** | **0.45%** | **0.54%** | **1.0%** |
| 120 | 21 | 0.3% | 0.36% | 0.7% |

- **Model check.** The same model predicts the no-skill hold-60 run E962-22 at 0.71% slippage; the measured value was 0.72%. The model's commission estimate (0.75%) is higher than measured (0.56%), because equity grew over the period. So the model is conservative.
- **Implication.** The 1.0–1.5% target requires an **average** holding period of about ≥ 55–60 sessions.
  - Variant A's 63-session horizon gives about 1.3% if few positions exit early. Early MA200 exits would push it towards about 1.5–2%.
  - Variant B's long cap gives about 0.7–1.3%, depending on how often the trend breaks.
- **Structural risk.** Whipsaw exits (many early Close < MA200 exits) would raise costs. I propose the realised cost drag as a **screen item: ≤ 1.5% a year** (§11). It is checked, not assumed.

## 9. Benchmarks and controls

All controls use the same universe, costs, cash rules, 12 slots, ranking and exit variant as the strategy book. Each isolates one part of the claim.

| Book | Entry | Question it answers |
|---|---|---|
| **EW benchmark** (existing E901-07) | Hold the eligible universe, equal weight | Does it beat the market it trades? |
| **SPY** (existing E900-07) | — | A familiar reference |
| **C1: trend-only** | Buy uptrend stocks (U1 + U2) immediately, top 12-1 momentum first; **no pullback or recovery required** | Does waiting for a pullback + recovery add value, or does "holding uptrend stocks" explain everything? (Essential.) |
| **C2: pullback without recovery** | U1 + U2, and RSI14(T) ≤ 40 today; buy at T+1 | Does waiting for the recovery add value over buying the dip? |
| **R: random uptrend** (3 seeds) | Random order over the uptrend stocks (X962 method), same exits | Does any selection skill exist beyond "uptrend + structure"? Seeds handle random-draw noise (about ±0.1–0.2 Sharpe per C03). |

Controls C1, C2 and R are run for **each** exit variant, so the comparisons are exactly paired.

## 10. Variants and why only two

| Candidate | Entry | Exit |
|---|---|---|
| **H014 v1.0** | U1 + U2 + P + R | A: 63 sessions, or earlier at Close < MA200 (horizon roll) |
| **H014 v1.1** | same | B: Close < MA200, or 126 sessions at the latest |

- The two exits are **economically different**: a fixed momentum horizon versus holding while the trend lasts. They are not parameter tweaks.
- Everything else is a **control**, not a candidate.
- Variations of the pullback depth, the window, the averages or the horizon appear **only** as pre-declared robustness perturbations of the one chosen candidate (§11). They never compete for selection.

**Considered and rejected as extra candidates:**

- a 12-1 momentum > 0 trend definition (duplicates U1/U2);
- a volume-confirmed recovery (ambiguous evidence);
- separate stop-loss levels (no evidence; a grid).

## 11. Statistical evaluation (proposed; changes need your approval)

**IS screen at $100K.** C01–C03 items kept, plus one new item:

- **Kept unchanged:**
  - Sharpe ≥ 0.50;
  - Sharpe ≥ EW + 0.10;
  - max drawdown ≥ −35% and no worse than EW;
  - the 3 IS stress episodes;
  - positive in ≥ 5 of 8 years;
  - no year above 40% of total profit;
  - Sharpe ≥ 0.40 at 2× slippage.
- **Trade-level items:** a 63–126-session strategy with 12 slots makes about 150–350 closed trades over 8 years, so the **≥ 100 closed trades** item stays meaningful and is kept.
  - Profit factor ≥ 1.2 and "expectancy without the best 5%" are kept. They guard against profit concentrated in a few trades.
  - **The expectancy confidence interval** is currently an i.i.d. bootstrap over trades. Trades overlap in time and share market moves, so that interval is too narrow. **Proposed replacement:** a stationary block bootstrap (mean block 63 days) of the book's daily excess return over EW, with the lower 2.5% bound > 0. This is the same method whose calibration we checked in C03.
- **New design check:** realised cost drag ≤ 1.5% a year (§8).

**Attribution: the hypothesis itself.** Proposed gates:

- Sharpe(H014) > Sharpe(C1)
- Sharpe(H014) > Sharpe(C2)
- Sharpe(H014) > Sharpe(R), for **each** of the 3 seeds

All are point estimates on IS. The paired block-bootstrap confidence interval of each difference is reported, not gated.

Why not gate on the confidence interval:

- The power to show a true improvement of 0.2–0.3 Sharpe over C1 is only about 20–60% in 8 years (`P2_feasibility.json`: SE of a Sharpe difference 0.16–0.27, depending on correlation).
- A confidence-interval gate would reject a real effect most of the time. The DSR (below) provides the multiple-testing protection instead.

**Robustness (unchanged criteria) for the chosen candidate only.** Plateau test: at least 80% of perturbations keep at least 70% of the base Sharpe. The 6 perturbations are:

- pullback RSI threshold 35 / 45;
- pullback window 3 / 8 sessions;
- horizon 42 / 84 sessions (Variant A) or cap 84 / 168 sessions (Variant B).

Plus Sharpe > 0 at 4× costs (6× reported only), and every IS third with Sharpe > 0.

**DSR:** see §13. The DSR is computed on IS + VAL daily returns, per the frozen method (D082 §3), after Validation.

**PBO:** diagnostic only. It is not meaningful with 2 candidates.

**Validation (one shot, after separate approval):**

- The unchanged Validation gates: VAL Sharpe ≥ 0.4 and ≥ 0.5 × IS; above EW; max drawdown ≥ −35%; ≥ 50 trades; the 2020 episode check.
- Plus Sharpe(H014) > Sharpe(C1) in VAL. This needs C1 and one R seed run in VAL.

## 12. Historical periods and data

What we already know from C01–C03:

- **2010–2017 (IS):** 40 candidates were tested on it, and we learned **general** facts about it:
  - EW Sharpe 0.92;
  - momentum books had Sharpe 0.4–0.6 (H002);
  - short-hold pullback strategies were destroyed by costs (H001, H004);
  - random portfolios reached 0.72–0.90.

  We learned nothing about this specific rule set.
- **2018–2021 (VAL):** used once (S005 v1.2). Its report showed the EW benchmark's VAL Sharpe (about 0.65) and S005's results. No trend-pullback rule was ever evaluated there.
- **2022–2026 (Holdout):** locked and untouched.

**Options:**

| Option | Development | Out of sample | Assessment |
|---|---|---|---|
| **P-A (recommended)** | IS 2010–2017, used only to screen the 2 pre-declared candidates | VAL 2018–2021 one-shot; Holdout at a final CP5 | The only period with the approved point-in-time ≥ $2B universe. IS contamination is general (we know the market's behaviour, not this rule's), and it is disclosed. VAL is nearly clean for this programme. |
| P-B | 1999–2009 as development | 2010–2021 | **Not available.** The point-in-time market-cap universe starts in 2010 (D033). 1999–2009 is allowed only as a finalist stress test (D035). |
| P-C | No separate development: 2010–2021 walk-forward as a single evaluation of pre-fixed rules | — | Uses more data for the one evaluation, but loses a clean confirmation step (VAL). Consider it only if you want to avoid IS reuse altogether. |
| P-D | Use the Holdout now | — | Not allowed before CP5. |

**Recommendation: P-A**, plus the optional D035 1999–2009 stress test for a finalist. It includes 2008–09, a natural test of the Close < MA200 exit, on the imperfect pre-2010 universe, and is never used for selection.

- All indicators use point-in-time adjusted data (the existing harness windows).
- No fundamental data is used beyond the existing universe filter.

## 13. Multiple testing: the decisive choice

**The quantities (Sharpe dispersion frozen from programme 1: V[SR] = 0.00095; IS + VAL = 3,020 days):**

| N counted | Observed Sharpe needed over 2010–2021 for DSR ≥ 0.90 |
|---|---|
| 2 (P2 candidates only) | 0.62 |
| 14 (P2 conservative: 2 selection + 8 robustness + about 4 Validation/2× slippage) | 1.22 |
| 42 (programme 1's 40 + P2's 2) | 1.45 |

**Options:**

- **D-1 (recommended):** a **separate P2 trial registry**. The DSR gate applies at **both** the P2 official N (selection candidates, 2) and the P2 conservative N (about 14), as in C03's dual-count rule. **N = 42 is reported as a programme-wide sensitivity.**
  - The effective bar is about Sharpe 1.2 over 2010–2021.
  - **Why:** DSR corrects for picking the best of the candidates compared. Programme 1's candidates were different hypotheses, are closed, and cannot be selected.
  - **Limits:** the choice of this idea was made after programme 1. That is a researcher degree of freedom DSR cannot measure, which is why VAL and the Holdout remain essential.
- **D-2:** inherit programme 1 (official N = 42).
  - The bar is about Sharpe 1.45 for a long-only 12-stock book. EW's IS Sharpe was 0.92, and no programme 1 candidate came close after its stages.
  - **The programme would almost certainly fail regardless of merit.** It is stricter, but largely uninformative.
- **Sharpe dispersion:** 2 candidates cannot estimate it, so the programme 1 value is frozen, as above.

## 14. Main overfitting risks

1. **Convention values (40/45/5/50/200) might look chosen with hindsight.** They are fixed now; no grid is run; perturbations are robustness checks only.
2. **Rediscovering H001/H004 under another name.** Mitigated by the multi-month holding period, the recovery requirement, and controls C1 and C2, which directly test whether entry timing matters.
3. **"Trend works" being mistaken for "pullback works".** Control C1 exists for exactly this.
4. **Researcher degrees of freedom after programme 1.** Everything is pre-registered in this document and a frozen specification before any run. VAL is used once.
5. **Few, correlated trades and regimes.** 8 years with about 3 corrections; power is limited, and this is disclosed.
6. **Cost drift through whipsaw exits.** Guarded by the cost-drag screen item.

## 15. Expected QuantConnect runs

| Class | Runs | Notes |
|---|---|---|
| Canaries (operational budget) | 2 | Indicator windows (MA, RSI, OHLC) against fresh history; the recovery signal timeline; next-open execution; ranking determinism; horizon roll. Non-candidate parameters. |
| Selection ($100K) | 2 | H014 v1.0 and v1.1 |
| Controls ($100K) | 10 | For each exit variant: C1, C2 and R × 3 seeds |
| $200K sensitivity | 2 | The two candidates |
| **Committed total** | **14 research + 2 canaries** | |
| Conditional: 2× slippage | ≤ 2 | Only for candidates passing the base screen |
| Conditional: robustness | ≤ 8 | Chosen candidate only: 6 perturbations + 4×/6× costs |
| Conditional: Validation | ≤ 3 | The candidate, C1 and one R seed (after separate approval) |
| **Maximum research runs** | **27** | Plus canaries |

## 16. Runtime and cost

- **Runtime:** about 7–10 minutes per IS run (12 slots, 260-bar windows on about 1,000 names).
  - Committed runs: about 2–3 hours of node time.
  - Everything including conditional runs: about 4–5 hours.
- **Money:** the existing $24 a month QuantConnect subscription, for about 1–2 months: **$24–48**. No new data or services are needed.
- **Effort:**
  - implementation of S014 (one strategy with an entry-mode switch for the controls), the canaries and tests: about 1–2 working sessions;
  - then the runs, and a checkpoint after the IS stage.

## 17. Owner decisions required before implementation

1. **Approve H014** as stated: the trend filter U1 + U2, pullback P, recovery R1 + R2, ranking by 12-1 momentum, and **2 candidates** with exits A and B.
2. **Scope change.**
   - CLAUDE.md's mission says "several days to several weeks". This programme holds for **weeks to several months** (63–126 sessions). It needs your explicit approval, and I will update CLAUDE.md for Phase 2 accordingly.
   - Programme naming: IDs continue globally (H014, S014, E014-xx) to keep one registry. Configs carry `programme: "P2"`.
3. **Controls:** C1, C2 and R (3 seeds) for each exit variant (10 runs).
4. **Portfolio:** 12 slots, $5K minimum unchanged, $200K as sensitivity only.
5. **Statistical changes:**
   - (a) replace the i.i.d. expectancy confidence interval with the block-bootstrap excess-return bound;
   - (b) add the cost-drag ≤ 1.5% screen item;
   - (c) the attribution gates, as point estimates against C1, C2 and each R seed;
   - (d) PBO diagnostic only.
6. **Multiple testing:** D-1 (recommended: a separate P2 registry, dual-count DSR, N = 42 as sensitivity) or D-2 (inherit N = 42).
7. **Periods:** P-A (recommended), or P-C.
8. **Budget:** at most 27 research runs plus about 2 canaries; $24–48 of subscription time.

After approval:

1. Freeze the specification (hash-pinned, as for D082).
2. Implement with tests: look-ahead truncation, timing, the horizon roll, the controls.
3. Run the canaries.
4. Run the committed runs.
5. Stop at the IS checkpoint.

## 18. How this differs from C01–C03, and why it is not a re-run of a rejected idea

| C01–C03 lesson | How P2 responds |
|---|---|
| Turnover and costs destroyed short-hold strategies. H001 had 28–60 turnovers a year and 6–14% costs; H004 had 22–41 turnovers and 4–8% costs. | Holding horizon of 63–126 sessions. Expected costs about 1.0–1.5% a year, **checked** as a screen item. |
| H001: oversold dips in uptrends, 10-day holds; failed. | Different return source: **multi-month trend continuation**, entered after a **confirmed recovery**, not a 10-day bounce. The timing claim is tested directly against control C2 (buy the dip without confirmation). |
| H004: pullbacks in momentum leaders, 10–20-day holds; failed on costs. | Same family of idea, but at a fundamentally different horizon and cost profile. H014 also isolates the entry-timing value with controls, which H004 lacked. |
| H002: momentum; failed (Sharpe 0.38–0.56). | Momentum is used only for ranking. The H002-like book is now **control C1**. H014 must **beat** it, not repeat it. |
| Portfolio structure trails EW, even with random selection. | The random-uptrend control (R, 3 seeds) measures skill beyond structure and the trend filter. The screen still requires Sharpe ≥ EW + 0.10. |
| The statistics limit what can be shown. | Two candidates only; DSR choice made explicit up front (§13); power disclosed (§11). |
| Stops, grids and data snooping are the usual failure of technical analysis. | No stop grid, no Fibonacci, no trend lines, no indicator stacking. Parameters fixed by convention; perturbations used only for robustness. |

**Honest overlap.** H014 belongs to the same broad family as H001, H002 and H004 (trend and pullback in large caps), so the prior failures are informative. What is new is:

- the holding horizon and cost profile (the proven cause of failure);
- the confirmed-recovery entry;
- the explicit controls, which let the programme answer a narrow, useful question: does pullback-and-recovery timing add value to holding uptrend stocks, after costs?

A **negative answer would still be informative.**
