# P7-CP2 — Multi-Factor Conviction Score Architecture and Pre-Registration

- **Date:** 2026-10-06.
- **Owner direction:** `docs/owner/2026-10-06_p7cp2_score_architecture.md` (D169).
- **Decisions:** D169, D170.
- **Frozen-candidate pre-registration:** `research/phase7/P7_score_spec.md` v1, hash-pinned in `qresearch.p7score` together with the score code `src/qresearch/lean/qr_p7_score.py` and `qr_p7.py`.
- **Tests:** `tests/test_p7_score.py` (20 synthetic sanity tests), `tests/test_p7_score_spec.py` (pins).
- **Design aid:** `research/phase7/P7_score_difficulty.py` / `.json` (synthetic only).
- **Scope:** architecture and pre-registration **only**. No future return, no IC / CAGR / SPY comparison, no backtest. The score was **not** run on 2011–2017 market data. No 2018–2021 data, Holdout locked, no purchase.

## Summary for the owner

**One 0–100 score of whole points, built from eight economically distinct dimensions:**

| Category | Points | Dimensions |
|---|---|---|
| **Technical Quality** | **40** | Trend 15, Momentum 15, Risk 10 |
| **Fundamental Quality** | **45** | Profitability 15, Cash conversion 10, Balance sheet 10, Growth 10 |
| **Sector Context** | **15** | Sector health 15 |

- Every dimension uses **coarse bands**: quintiles, or three trend / sector states. A stock's score is therefore readable line by line.
- **Seven hard disqualifiers** remove stocks we cannot trust or do not want regardless of points:
  - no or financial / REIT sector;
  - missing or stale fundamentals;
  - too little history;
  - corporate-event contamination;
  - stale price;
  - broken long-term trend;
  - financial impairment.
- **Market Regime** has two inputs (SPY trend, market breadth) and four states. It **only caps how many positions may be held**, and never changes a stock's score.
- **Review:** monthly, with a weekly hard-disqualifier check on holdings only.
- **Entry ≠ holding:** high entry threshold, lower exit threshold, replacement buffer. There is no time stop and no forced filling; cash is fine.
- **All numbers that would otherwise be tempting to fit to returns** (entry, exit, buffer, maximum positions, regime exposure ceilings) are **deferred** to P7-CP3, which may use only candidate availability, persistence, turnover and cost.
- **Difficulty (synthetic, using the feature correlations measured in P7-CP1):**
  - median score about 43;
  - of 600 scorable stocks, roughly 8–18 would reach 80, 3–8 would reach 85 and 1–3 would reach 90.

  A high score needs agreement across dimensions.

**Recommendation: READY FOR AVAILABILITY / MECHANICS STUDY** (P7-CP3), after the owner decisions in item 49.

## 1. P7-CP1 accepted

P7-CP1 (Data & Fidelity Readiness Audit; READY TO DESIGN SCORE) is accepted by the owner (D169). Its restrictions are adopted in items 2–9.

## 2. Development window

**2011-01 → 2017-12**, with monthly reviews at the last session of each month: 84 review dates. It was chosen mechanically from data availability (P7-CP1 item 24): sector context and year-over-year fundamentals both start in 2011.

## 3. Eligible company types

US common stocks (data-v1 universe):
- NYSE / Nasdaq;
- PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M;
- SEC correction layer;
- non-financial and non-REIT;
- one share class per company;
- passing the hard disqualifiers.

## 4. Financial / REIT exclusion

**H1:** a stock is excluded when, at t, **no SEC SIC is visible** or the visible SIC is **6000–6999**.

- **Rule:** the SIC carried by the latest periodic filing, effective the day after that filing (D113, `qr_industry.SICHistory`).
- **Covers:** banks, brokers, insurers including health insurers (6324), real estate, REITs (6798) and holding / investment offices.
- **No technical-only route** for excluded names.
- REIT conversions and de-REITings are dated by the SEC's own code change.
- A stock without a visible SIC has no PIT sector. It is excluded as unscorable, not classified by guess.

## 5. Missing-data rules

- **A stock missing any input of the full score is not eligible on that date** (H2 fundamentals, H3 history, H5 price, H1 sector).
- **No value is filled.**
- **Same-universe rule:** every future comparison / control book is drawn from the same scorable set with the same disqualifiers.
- P7-CP1 showed missing fundamentals are non-random: new listings, repaired names, Energy, more later exits.

## 6. Corporate-event rules (H4)

**Events counted:**
- an **unverified split** (its boundary is not confirmed by QuantConnect's own SCALED_RAW);
- a **distribution ≥ 10%** of its reference price (spin-off or special).

**Mechanical rule:** an event at row e contaminates a feature window of L bars ending at bar b if v[b−L+1] < e ≤ v[b]. The stock is excluded until the event leaves the window.

| Event | Series affected | Window L |
|---|---|---|
| Unverified split | both split-adjusted C and total-return P | **253 bars** (all features) |
| Large distribution | only the split-adjusted chart C | **221 bars** (trend features) |

`contamination()` returns the exact number of bars until clean; a test checks it at the boundary. **There is no fixed "3 months".**

A **held** stock under H4 is **frozen**:
- kept, not score-evaluated, never treated as the "weakest" for replacement;
- still subject to H1, H2, H5 and H7;
- H6 is suspended, because its window is contaminated.

## 7. Security-life / re-used id rule

`qr_p7.LIFE_GAP = 60` (D167) is preserved. More than 60 missing sessions between two bars starts a new life, and no window crosses it. Bars are counted in the current life (`test_security_life_rule_resets_history`). Earlier phases are unchanged.

## 8. One share class per company

- **Company key:** the SEC CIK of the latest periodic filing visible at t (PIT; the same rows as the SIC).
- **Choice:** the class with the **highest PIT ADV20**; ties go to the lexicographically smallest security id (`select_share_classes`, tested: GOOG / GOOGL → GOOGL; BRK.A / BRK.B tie → BRKA).
- The choice is made **before** scoring, from liquidity only, never from returns. Morningstar's company id is not used (blank for many delisted firms, P7-CP1).

## 9. Price-series rule for every technical feature

| Feature | Series |
|---|---|
| SMA50, SMA200, SMA200 slope, trend state, broken trend (H6) | **Split-adjusted close** (RAW × split feed) |
| 12-1 momentum | **Total-return close** (RAW × split × dividend feed) |
| 60-day volatility | **Total-return daily log returns** |
| Sector breadth, market breadth | **Split-adjusted close** vs its SMA200 |
| SPY trend | **Split-adjusted close** |
| Execution (later) | **RAW** price at the T+1 open |

- Highs, lows, ATR and price structure are **not used in v1** (item 11). If added later, they use split-adjusted OHLC.
- No total-return synthetic chart is used for structure. No feature mixes series.

## 10. Technical Quality dimensions

**Trend (15), Momentum (15), Risk (10).** Price structure is not a separate dimension (item 11).

## 11. Technical features

| Dimension | Exact definition | Points | Why |
|---|---|---|---|
| **Trend** | State on split-adjusted closes in the current life: **strong** = close > SMA50 > SMA200 and SMA200(t) > SMA200(t − 21 bars); **moderate** = close > SMA200 and SMA200 rising (not strong); **weak** = otherwise | 15 / 8 / 0 (absolute state) | One ordinal state replaces price > MA200, the SMA50 / 200 cross, MA slope, MACD and the multi-MA trend score: all one phenomenon (P7-CP1 ρ 0.72–0.90) |
| **Momentum** | 12-1 total-return momentum P[b−21] / P[b−252] − 1 | Quintile across the scorable set: 0 / 0 / 5 / 10 / 15 | The only Tier-A technical evidence (P4-CP2). It is only partly redundant with trend (ρ 0.60). Weight kept modest because H019 did not reproduce it in our universe |
| **Risk** | Standard deviation of 60 daily total-return log returns (lower is better) | Quintile across the scorable set: 0 / 0 / 3 / 7 / 10 | Distinct from trend and momentum (ρ ≈ 0). Prefers stable price action; low-volatility evidence (Ang et al. 2006; Frazzini & Pedersen 2014) |

**Not used, with reasons:**
- **52-week-high proximity:** ρ 0.73 with the SMA200 ratio, so redundant with trend.
- **ATR:** ρ 0.83 with volatility, so redundant.
- **MACD, RSI, Bollinger, ADX, volume confirmation:** Tier D (P4-CP2), redundant.
- **H020 chart structure:** rejected as a score; trend ρ 0.75.
- **Severe deterioration** is handled by the H6 disqualifier, not by points.

## 12. Fundamental Quality dimensions

**Profitability (15), Cash conversion (10), Balance sheet (10), Growth (10).**

They were chosen as the most **mutually independent** set the approved fields allow. P7-CP1 feature-feature ρ:

| Pair | ρ |
|---|---|
| GP/A vs cash conversion | 0.07 |
| GP/A vs equity/assets | 0.23 |
| GP/A vs revenue growth | 0.17 |
| Cash conversion vs equity/assets | −0.01 |
| Cash conversion vs revenue growth | −0.01 |
| Equity/assets vs revenue growth | 0.19 |

## 13. Fundamental features and formulas

All inputs come from the frozen PIT store. True TTM flows; snapshots ≤ 200 days old.

| Dimension | Formula | Normalisation | Why this normalisation |
|---|---|---|---|
| **Profitability** | **GP/A** = gross profit TTM ÷ total assets | **Quintile within the FF12 sector** (cross-sectional if fewer than 10 scorable members) | Novy-Marx (2013): the cleanest profitability measure. Asset intensity and gross margins differ structurally by industry (retail vs utilities), so sector-relative ranking compares like with like |
| **Cash conversion** | **(OCF TTM − net income TTM) ÷ total assets** (= −accruals; higher = earnings backed by cash) | Quintile across the scorable set | Sloan (1996) accruals; Ball et al. (2016). Scale-free and comparable across industries. Nearly orthogonal to GP/A (ρ 0.07) |
| **Balance sheet** | **Equity ÷ total assets** | **Quintile within the FF12 sector** | Leverage norms are industry-specific (utilities vs software). Debt data is unsafe, so equity/assets is the only defensible strength measure. Negative equity is a hard disqualifier |
| **Growth** | **Revenue TTM ÷ revenue TTM recorded at the review 12 months earlier − 1** | Quintile across the scorable set | Revenue is the most robust growth base: always positive, no sign changes, best coverage. Gross-profit and OCF growth are redundant (with revenue) or unstable (OCF sign changes), so they are not used |

**Why percentiles, not absolute thresholds:**
- Quintiles avoid arbitrary cut-offs such as "growth > 17.3%".
- They are robust to outliers (ranks).
- The points distribution does not drift when the market or economy is unusually strong or weak.
- The only absolute rules are economic hard lines: impairment (equity ≤ 0, or both NI and OCF ≤ 0) and the trend state.

**Not used:**
- NI/A, OCF/A and ROE: redundant with GP/A (ρ 0.58–0.69).
- Valuation (E/P, B/M): inversely related to quality (B/M vs GP/A −0.53), so it would cancel quality points. It may be a separate future question.
- Debt, operating income, FCF, share counts: unsafe.

## 14. Sector Context dimension

**Sector health (15):** the stock's FF12 sector's **breadth** relative to the **market's** breadth.

This is participation, not H021's 6-month return ranking. It is deliberately **not** sector momentum: H021-A found no sector-momentum edge, so the failed rotation experiment is not recreated inside every score.

## 15. Sector feature

**Sector breadth** = the share of the sector's PIT-eligible members (data-v1, with ≥ 200 current-life bars and a fresh bar) whose split-adjusted close > their SMA200. **Market breadth** = the same over all eligible stocks.

| Condition | State | Points |
|---|---|---|
| sector − market ≥ +0.10 | supportive | **15** |
| sector − market ≤ −0.10 | weak | **0** |
| otherwise, or fewer than 10 members with a state | neutral | **8** |

**Effect, as the owner asked:**
- A strong stock in a supportive sector gains up to +7 over neutral.
- In a weak sector it loses 8.
- A weak stock can collect at most 15 sector points, so the sector cannot rescue it (test: a weak stock + supportive sector ≤ 23).

**Not used:** stock-vs-sector relative strength (overlaps stock momentum) and sector momentum (H021-A).

## 16. Information-overlap map

| Phenomenon | Measures that encode it | Kept (once) | Dropped as redundant |
|---|---|---|---|
| Trend | close / SMA200, SMA50 / SMA200, SMA200 slope, MACD, multi-MA score, 52-week-high proximity (ρ 0.57–0.90) | Trend state (one ordinal) | All others |
| Momentum | 12-1, 6-1 (ρ 0.90 with SMA50 / SMA200), relative strength vs SPY | 12-1 total return | 6-1, RS vs SPY |
| Risk | 60-day volatility, ATR (ρ 0.83), beta, range | 60-day volatility | ATR, range |
| Structure | 52-week high / low, breakouts, bases (H020) | — (H6 disqualifier only) | All |
| Profitability | GP/A, NI/A, OCF/A, ROE (ρ 0.58–0.69) | GP/A (sector-relative) | NI/A, OCF/A, ROE |
| Earnings quality | accruals, OCF/NI | Cash conversion (−accruals) | OCF/NI (unstable near NI = 0) |
| Growth | revenue, GP, NI, OCF growth (ρ ≈ 0.35 revenue growth vs ΔNI/A) | Revenue growth | Others |
| Balance sheet | equity/assets (debt unsafe) | Equity/assets (sector-relative) | — |
| Valuation | E/P, CF/P, S/P, B/M (ρ 0.29–0.53; opposed to quality) | — (not in v1) | All |
| Sector | sector momentum, breadth, stock vs sector | Sector breadth vs market | Momentum (H021-A), stock vs sector |
| Market | SPY trend, breadth, VIX | SPY trend + breadth (Regime only) | VIX (fidelity pending; overlaps) |

**Cross-domain overlap** (trend / momentum vs profitability) was not measured in P7-CP1. Any residual correlation only makes high scores somewhat more common (difficulty study, cross-correlation 0.2 sensitivity).

## 17. Stock-score architecture

```
STOCK CONVICTION SCORE (0–100)            MARKET REGIME (separate)
  A. Technical Quality   40                 SPY trend  x  market breadth
       Trend 15 · Momentum 15 · Risk 10       -> STRONG / NORMAL / WEAK / RISK_OFF
  B. Fundamental Quality 45                 -> caps the number of positions only
       GP/A 15 · Cash conversion 10 ·
       Equity/assets 10 · Revenue growth 10
  C. Sector Context      15
       Sector breadth vs market 15
  + 7 hard disqualifiers (H1–H7)
```

## 18. Total score scale

**0–100, integers.** Points per dimension are whole numbers from coarse bands, so there are no decimals: 82 vs 83 differ by one band step somewhere, never by an invisible fraction.

## 19. Category maximum points

**Technical 40, Fundamental 45, Sector 15.**

## 20. Exact point allocation

| Dimension | Max | Levels (points) |
|---|---|---|
| Trend | 15 | strong 15, moderate 8, weak 0 |
| Momentum | 15 | quintile 1–2: 0, 3: 5, 4: 10, 5: 15 |
| Risk | 10 | lowest-volatility quintile 10, next 7, middle 3, top two 0 |
| Profitability (GP/A) | 15 | 0 / 0 / 5 / 10 / 15 |
| Cash conversion | 10 | 0 / 0 / 3 / 7 / 10 |
| Equity / assets | 10 | 0 / 0 / 3 / 7 / 10 |
| Revenue growth | 10 | 0 / 0 / 3 / 7 / 10 |
| Sector | 15 | supportive 15, neutral 8, weak 0 |

**Why 40 / 45 / 15** (one primary architecture; no alternative weightings will be compared):

- **Evidence strength.**
  - **Profitability / quality** has the most robust published evidence (Novy-Marx 2013; Sloan 1996; Asness et al. QMJ, pre-2017). It is slow-moving, which suits long holdings.
  - **Technical evidence** in this project was negative: H018 no edge, H019 momentum not reproduced, H020 chart score null. Technical therefore confirms rather than dominates.
  - **Sector:** H021-A null, so modest.
- **Independence.** Fundamentals offer four nearly orthogonal dimensions (|ρ| ≤ 0.23); technical offers three (trend and momentum overlap at 0.60). Points follow the number of independent ideas.
- **Data quality.** Technical data is the cleaner layer (98% coverage, 380 / 380 verified), but fundamentals are also verified (0 / 268 early). This argued against giving fundamentals even more.
- **Technical influence is larger than 40 points suggests:** the broken-trend disqualifier (H6) gives technical a veto. A strong company in a long-term downtrend can never be bought.
- **Prior failures.** H016 (GP/A alone) also failed. No single factor dominates: the largest dimension is 15 points.

## 21. Thresholds internal to components

| Threshold | Value | Where |
|---|---|---|
| Trend state | close vs SMA50 / SMA200; SMA200 vs its value 21 bars earlier | Trend dimension, H6 |
| Quintile cut-offs | average-rank fifths | All percentile dimensions |
| Sector breadth band | ±0.10 vs the market | Sector dimension |
| Minimum group | 10 members | Sector scope and sector state |
| Large distribution | ≥ 10% | H4 |
| Stale price | > 5 sessions | H5 |
| Minimum history | 253 bars (mechanical: the longest window) | H3 |
| Fundamental freshness | 200 days (inherited, D108) | H2 |
| Regime breadth | ≥ 0.60 high, < 0.40 low | Regime |

## 22. Number of tunable constants

| Group | Count | Contents |
|---|---|---|
| Feature definitions | **8** (+ 2 regime inputs) | trend state, 12-1 momentum, 60-day volatility, GP/A, cash conversion, equity/assets, revenue growth, sector breadth; SPY trend, market breadth |
| Window lengths | **7** | 50, 200, 21, 252, skip 21, 60, 12 months. Standard conventions, never varied |
| Judgment constants | **7** | 10% distribution, 5 bands, minimum group 10, ±0.10 sector band, 0.60 and 0.40 regime breadth, 5-session staleness |
| Weights | **8** | dimension maxima; the 3 category totals follow from them |
| Level tables | **3** | quintile, trend and sector fractions |
| Hard disqualifiers | **7** | H1–H7 |
| Deferred (P7-CP3, no returns) | **5** | entry, exit, buffer, maximum positions, regime ceilings |

None of these will be searched or tuned against returns. A search over the 7 judgment constants is forbidden by the spec.

## 23. Exact hard disqualifiers

| Code | Rule |
|---|---|
| H1 | No PIT SEC SIC, or SIC 6000–6999 |
| H2 | A required fundamental input is missing, stale (> 200 days) or invalid (assets ≤ 0, revenue ≤ 0, baseline revenue ≤ 0) |
| H3 | Fewer than 253 valid bars in the current security life |
| H4 | Corporate-event contamination (item 6) |
| H5 | Last price bar older than 5 sessions |
| H6 | Broken long-term trend: split-adjusted close < SMA200 **and** SMA200 falling over 21 bars |
| H7 | Financial impairment: equity ≤ 0, or (net income TTM ≤ 0 **and** OCF TTM ≤ 0) |

H1–H5 define the data-scorable ranking population. H6–H7 make a scored stock ineligible.

## 24. Why each disqualifier is hard rather than scored

| Code | Reason |
|---|---|
| H1 | The fundamental definitions are not economically comparable for banks, insurers and REITs. A score would be meaningless, not merely low |
| H2 / H3 / H5 | **We cannot compute the score honestly.** Filling would invent information; P7-CP1 showed the missingness is non-random |
| H4 | **We do not trust the measured inputs.** A spin-off or broken split adjustment produces fake 30–60% chart moves (P7-CP1: 31 on eligible days) |
| H6 | **We do not want it regardless of business quality.** Buying a stock below a falling 200-day average contradicts the strategy's premise (technical confirmation). As points it could be outvoted by fundamentals |
| H7 | **We do not want it regardless.** Negative equity, or losing money on both earnings and cash flow, is not "quality". Percentile points could still rank such a company in a middle quintile of a weak cross-section |

**Deliberately NOT hard:**
- high volatility (the risk points handle it);
- a weak sector (sector points);
- low momentum (momentum points);
- valuation.

These are "mildly unattractive", not untrustworthy.

## 25. Missing / stale fundamentals

- **Missing:** any of the six True TTM / snapshot inputs or the 12-month revenue baseline absent → H2.
- **Stale:** the PIT store already refuses a TTM whose newest quarter is older than 200 days, or a snapshot report older than 200 days → H2.
- **Never filled, never carried forward beyond the store's rules.**
- **The 12-month baseline** is the value **recorded 12 months earlier**, so a newly eligible stock needs a recorded TTM from a year earlier. This is the main reason young listings stay unscorable.

## 26. Market Regime architecture

- **Two independent market-level inputs** (item 27) feed a fixed 3 × 3 table (item 28) giving four regimes.
- The regime's **only** role is to cap the number of positions.
- `score_date` takes no regime input. A test shows the regime changes how many names are bought, never their order.

## 27. Market / breadth inputs

1. **SPY trend** on split-adjusted closes:
   - up = close > SMA200 and SMA200 rising (21 bars);
   - down = close < SMA200 and SMA200 falling;
   - otherwise mixed.
2. **Market breadth:** the share of the **PIT eligible universe** (data-v1, financials included; ≥ 200 current-life bars; fresh bar) above its own SMA200.
   - The denominator is the historical eligible set at t, **never survivors** (P7-CP1 survivorship protections preserved).
   - **Levels:** high ≥ 0.60; low < 0.40; otherwise mid.

**VIX is not used in v1:**
- its gap / fidelity check is pending;
- it overlaps SPY trend and breadth in stress;
- two inputs suffice.

## 28. Market-regime categories

| SPY trend \ breadth | High (≥ 60%) | Mid | Low (< 40%) |
|---|---|---|---|
| Up | **STRONG** | NORMAL | WEAK |
| Mixed | NORMAL | WEAK | WEAK |
| Down | WEAK | WEAK | **RISK_OFF** |

Tests:
- broad uptrend + broad participation → STRONG;
- index up but breadth deteriorating (0.50) → NORMAL, weaker than STRONG;
- broad downtrend + low breadth → RISK_OFF.

## 29. Exposure percentages

**Deferred, not frozen.** The only frozen part is the ordering: ceiling(STRONG) ≥ ceiling(NORMAL) ≥ ceiling(WEAK) ≥ ceiling(RISK_OFF).

The ceilings cannot be chosen from mechanics alone without returns, so they must be **fixed by the owner as a policy choice before any return is seen**. Illustrative policy: 100 / 80 / 50 / 20%. P7-CP3 will report how often each regime occurs and the resulting position caps; it will not choose the ceilings.

## 30. Score recalculation frequency

**Monthly**, at the last session of each calendar month (from the session calendar, P7-CP1 E11), with orders at the next open.

**Why monthly:**
- the inputs are slow (12-1 momentum, 200-day trend, quarterly fundamentals);
- the intended holdings last months or longer;
- weekly scoring would multiply threshold crossings and turnover for no new fundamental information.

**Plus a weekly check (last session of the week) of holdings only, for hard disqualifiers** (H1, H2, H5, H6, H7). It sells at the next open. There is no entry and no score-based exit.

## 31. Filing-arrival behaviour

**One model:**
- a new filing enters the **score** at the next monthly review;
- it can act sooner **only** through the weekly **hard-disqualifier** check (e.g. a filing showing negative equity → H7 → exit);
- there is no immediate rescoring and no entry between reviews.

## 32. Entry / holding / exit philosophy

- **Entry:** demanding: score ≥ EntryThreshold, best first, only into free slots.
- **Holding:** tolerant: kept while score ≥ ExitThreshold (< EntryThreshold) and no hard disqualifier applies.
- **Exit:** only when:
  - the score falls below ExitThreshold;
  - a hard disqualifier applies;
  - the stock leaves the eligible universe;
  - the regime cap requires it (weakest first);
  - a candidate clears the replacement buffer.

## 33. Hysteresis architecture

```
BUY  at a monthly review if Score >= EntryThreshold (and a slot is free, or via replacement)
HOLD while Score >= ExitThreshold and no hard disqualifier
SELL at a monthly review if Score < ExitThreshold; at any weekly check on a hard disqualifier
ExitThreshold < EntryThreshold   (enforced in code: plan_review raises otherwise)
```

## 34. Replacement-buffer architecture

When no slot is free:
1. take candidates in score order;
2. the best remaining candidate replaces the **weakest non-frozen** holding only if candidate score ≥ holding score + ReplacementBuffer;
3. each holding is replaced at most once per review;
4. the process stops at the first candidate that fails (the rest are lower).

Tested: 81 does not replace 72 with a buffer of 10; 85 does.

## 35. No fixed holding-period exit

**Confirmed.** No 30 / 60 / 90-day exit, no time stop and no minimum holding period. Winners stay while their conviction persists.

## 36. Cash allowed

**Confirmed.** Each position is ≤ 10% at entry. With five qualifying stocks the book is 50% invested and 50% cash.

## 37. No forced portfolio filling

**Confirmed.**
- Free slots stay empty unless a candidate reaches EntryThreshold (tested: a 79 is not bought against an 80 entry).
- v1 has **no relaxation ladder**.
- Any future ladder needs its own pre-registration with a hard floor.

## 38. Design of the P7-CP3 availability-only study

**Host:**
- one QuantConnect host combining the X991 fundamentals pipeline and the X992 price / breadth pipeline;
- the frozen data-v1 universe and the frozen score code;
- 84 monthly reviews (2011-01 → 2017-12), plus the weekly hard-disqualifier states for the mechanics;
- **no return of any kind is computed or exported.**

**Exported per review** (derived data only):
- the score table: id, date, total, category subtotals, dimension points, disqualifier codes, ADV20, FF12;
- the regime state; scorable and eligible counts.

**Measured (offline, from the table):**

| Group | Metrics |
|---|---|
| Score distribution | Per review: histogram in 5-point bins; median, 90th and 99th percentiles |
| Candidates per threshold | Count per review: median, 10th / 90th percentiles; dates with 0, 1–5, 6–10, > 10 candidates; by year |
| Persistence | For a stock ≥ θ at review m: the probability it is still ≥ θ − g at m + k (g = 5, 10, 15, 20; k = 1, 3, 6, 12); the median run length above each exit level |
| Crossing frequency | Entries and exits per review across each threshold pair |
| Concentration | Candidates by FF12 sector (largest share; dates where one sector > 50%) and by year |
| Disqualifiers | Counts by code per review (how much each removes) |
| Regime | Frequency of each state per year (exposure ceilings stay the owner's) |

## 39. Threshold candidates for P7-CP3

| Parameter | Candidates |
|---|---|
| **EntryThreshold** | 70, 75, 80, 85, 90 (very high = 90 / 85, high = 80, moderately high = 75 / 70) |
| **Exit gap** (Entry − Exit) | 5, 10, 15, 20 |
| **ReplacementBuffer** | 5, 10, 15 |
| **MaxPositions** | 6, 8, 10, 12 |
| **Review** | monthly (fixed; not compared) |

The synthetic estimate (item 43) suggests about 1–18 names ≥ 80–90 per 600 scorable. The real counts are measured, not assumed.

## 40. Design of the portfolio-size mechanics study

**Shadow book from scores only:**
- the item 33–34 rules for each K ∈ {6, 8, 10, 12}, crossed with the chosen entry / exit / buffer;
- **constant notional**: equity fixed at $100K; each position min(10%, 100% / K) of $100K at entry. No price is used, so no returns exist.

**Metrics:**
- average and median number of holdings; cash utilisation;
- position size;
- orders a year;
- $7 × orders + 10 bps × traded notional as % of capital;
- maximum sector weight;
- score dilution: the median score of the K-th holding vs the 1st.

**Proposed rule (owner to approve before the run):** the **largest K whose mean cash utilisation ≥ 80%** in every year, subject to the cost ceiling. This favours diversification only while slots are actually filled by qualifying stocks.

## 41. Design of the churn / hysteresis mechanics study

**Grid:** entry × exit gap × buffer (item 39) on the same score-only shadow book, monthly reviews plus weekly disqualifier exits.

**Metrics:**
- median and 25th-percentile holding duration;
- round trips a year;
- exits by cause (exit threshold / disqualifier / replacement / regime cap / universe);
- **whipsaw rate** (an exit re-entered within 3 reviews);
- replacement count;
- annual order count and cost.

**Proposed selection rules** (pre-registered; owner to approve the floors before P7-CP3 runs):
1. **Entry:** the strictest θ with median candidates ≥ 10 and ≤ 10% of review dates with zero candidates, **in every year** 2011–2017.
2. **Exit gap and buffer:** among grid points with whipsaw ≤ 10% and annual cost ≤ 1.0% of capital, the **smallest** exit gap, then the smallest buffer.
3. **K:** item 40.

**Never consulted:** CAGR, Sharpe, returns, IC, SPY.

## 42. Estimated runtime / resources

| Run | Estimate |
|---|---|
| P7-CP3 host (fundamentals from 2008-07 warm-up + daily price panel 2007–2017 + monthly scoring) | ≈ 15–20 min wall, ≈ 4 GB peak; fits one B2-8 node (E991 / E992 took 8 min each, 3.4 GB) |
| Score table export (~84 × 700 rows, compressed) | ≈ 0.5–1 MB of summary statistics (X984 exported 2.3 MB) |
| Mechanics grid (5 × 4 × 3 × 4 = 240 shadow books × 84 reviews) | Offline, seconds |
| Cost | Within the existing $24/month |

## 43. Unit / sanity test results

**`tests/test_p7_score.py`, 20 tests, all pass** (synthetic / mock companies; no market data):

| Test | Result |
|---|---|
| **A** strong everywhere | **100 / 100**, eligible; readable breakdown |
| **B** strong chart, weak fundamentals | **55** (40 + 0 + 15): not exceptional |
| **C** strong fundamentals, severe downtrend | **H6, ineligible**; technical ≤ 10 |
| **D** strong company, weak sector | **85**, still investable; a supportive sector adds exactly 15 more |
| Weak stock, supportive sector | ≤ 23: sector cannot rescue |
| **E** missing / untrusted data | H2 (missing baseline), H5 (stale price), H3 (short history), H1 (REIT SIC 6798; no SIC), H4 (contamination): all ineligible with no score |
| Impairment | H7 |
| Score properties | integer 0–100; category maxima 40 / 45 / 15 |
| Quintiles | ties shared; small sector groups fall back to market ranks |
| Market level | momentum points invariant to a market-wide +50% |
| Declared series | SMAs from split-adjusted closes, momentum / volatility from total-return closes (exact) |
| Security-life rule | resets history |
| Corporate events | exclusion ends exactly when the event leaves the 253-bar (split) / 221-bar (distribution) window; a 5% distribution never triggers |
| Fundamental formulas | missing / invalid denominators rejected |
| Share class | one per company, deterministic tie |
| **Regime** | STRONG / NORMAL / RISK_OFF cases; the regime never changes buying order |
| **Hysteresis / replacement / no forced filling / regime cap / frozen holdings / weekly disqualifier-only checks** | all pass |
| Difficulty | with independent dimensions: < 2% of stocks ≥ 80, < 0.2% ≥ 90, median < 50 |
| Constant count | pinned |

**Pins:** `tests/test_p7_score_spec.py` (3 tests) pins the spec and code hashes, constants, weights and disqualifiers.

**Synthetic difficulty study** (`P7_score_difficulty.json`; P7-CP1 feature-feature correlations; 600 scorable names × 200 synthetic dates):

| Cross-domain ρ | Median | p90 | p99 | ≥ 70 | ≥ 75 | ≥ 80 | ≥ 85 | ≥ 90 |
|---|---|---|---|---|---|---|---|---|
| 0 | 43 | 65 | 80 | 6.3% (38) | 3.1% (19) | 1.4% (8) | 0.5% (3) | 0.15% (1) |
| 0.2 | 43 | 70 | 86 | 10.0% (60) | 5.9% (35) | 3.0% (18) | 1.4% (8) | 0.6% (3) |

**Full suite:** passes (item 47).

## 44. No future return calculated

**Confirmed.** No return after any decision date, no IC, CAGR, Sharpe, SPY comparison or bucket return, even as a diagnostic. The score was never applied to historical market data.

## 45. 2018–2021 untouched

**Confirmed.** No data of any kind was requested in P7-CP2 (no QuantConnect run).

## 46. Holdout untouched

**Confirmed.** `HOLDOUT_UNLOCK.md` is absent.

## 47. Nothing purchased

**Confirmed.** The subscription is unchanged ($24/month).

## Answers to the owner's questions A–J

**A. Minimum independent dimensions?**
- **Eight:**
  - trend state, 12-1 momentum, volatility (technical);
  - sector-relative GP/A, cash conversion, sector-relative equity/assets, revenue growth (fundamental);
  - sector breadth vs market (context).
- Each is economically distinct and, where measured, nearly orthogonal to the others in its layer. The exception is trend vs momentum (ρ 0.60), deliberately kept as confirmation plus relative strength.

**B. Weights?**
- **Technical 40, Fundamental 45, Sector 15.**
- Fundamentals get the most because they offer the most independent, best-documented, slow-moving information, suited to long holdings.
- Technical confirms (and vetoes through H6) because our own technical tests failed.
- Sector stays contextual because H021-A was null.

**C. Technical features that survive?**
- **Kept:** the **trend state** (close vs SMA50 / SMA200 and SMA200 slope on split-adjusted closes); **12-1 total-return momentum**; **60-day total-return volatility**.
- **Dropped:** 52-week high, ATR, MACD, RSI, Bollinger, volume confirmation and chart structure (redundant, or Tier D / failed in H020).

**D. Fundamental ratios / changes safely derived from the seven fields?**
- **GP / total assets**;
- **(OCF − net income) / total assets**;
- **equity / total assets**;
- **revenue TTM / revenue TTM recorded 12 months earlier − 1**.

Impairment (equity ≤ 0, or NI ≤ 0 and OCF ≤ 0) is a disqualifier. Market cap is used only for the universe in v1; valuation is deliberately not used.

**E. Hard disqualifiers rather than negative points?**
- H1 financial / REIT / no sector;
- H2 missing or stale fundamentals;
- H3 insufficient history;
- H4 corporate-event contamination;
- H5 stale price;
- H6 broken long-term trend;
- H7 financial impairment.

These cover untrustworthy, incomparable or fundamentally unwanted stocks. Merely unattractive traits stay as points.

**F. How is a high score made genuinely difficult?**
- Only the **top two quintiles** earn percentile points, and only the top quintile earns full points.
- Full trend points need a strong uptrend.
- Sector support needs breadth clearly above the market.
- No dimension exceeds 15 points, so ≥ 80 requires strong agreement across at least six of eight dimensions.
- **Synthetic expectation:** median ≈ 43; ≈ 1–3% of scorable stocks ≥ 80; ≈ 0.15–0.6% ≥ 90.

**G. How does Market Regime control exposure without contaminating the ranking?**
- It is computed from market-level inputs only (SPY trend, PIT breadth).
- It is **not an input** to any stock's score.
- It only sets a **maximum number of positions** (ceiling ÷ 10%).
- When the cap falls, the lowest-scoring holdings leave first.
- Test: the regime changes how many are bought, never which order.

**H. Review frequency?**
- **Monthly scoring and trading**, plus a **weekly hard-disqualifier check on holdings only**.
- Filings feed the score at the next monthly review; the weekly check catches impairment or stale data sooner.

**I. Hysteresis and replacement?**
- Buy at ≥ Entry; hold while ≥ Exit (Exit < Entry); sell below Exit or on a disqualifier.
- When full, a candidate replaces the weakest holding only if it beats it by the Replacement Buffer.
- No time stop, no forced filling.

**J. Next experiment?**
- **P7-CP3:** apply the frozen score to the 84 monthly reviews of 2011–2017 and export only score tables.
- Measure candidate counts, persistence, crossings, concentration and disqualifier counts.
- Run score-only shadow books (constant notional, no prices) over Entry {70–90} × Exit gap {5–20} × Buffer {5–15} × K {6–12}.
- Choose thresholds by the pre-registered availability / whipsaw / cost / utilisation rules (items 40–41).
- Never by returns.

## 48. Recommendation

# READY FOR AVAILABILITY / MECHANICS STUDY

The score, disqualifiers, regime, review cycle and mechanics structure are fully specified, hash-pinned and tested on synthetic companies, before any historical score or return exists. Every number that could be tempting to tune is deferred to a returns-blind study with selection rules written in advance.

## 49. Owner decisions required next

1. **Approve the frozen-candidate score v1:**
   - the eight dimensions;
   - weights 40 / 45 / 15 and the point tables;
   - H1–H7;
   - the sector-health definition;
   - the market regime (SPY trend × breadth).

   It becomes FROZEN v1 on approval. Nothing changes afterwards except by a recorded decision taken before any return is seen.
2. **Review cycle:** monthly scoring and trading, plus a weekly hard-disqualifier check on holdings.
3. **Exposure ceilings per regime:** fix them now as a policy (e.g. 100 / 80 / 50 / 20%), or let P7-CP3 report regime frequencies first (they will still be fixed before any return).
4. **P7-CP3 selection rules and floors** (items 40–41):
   - median candidates ≥ 10 and ≤ 10% zero-candidate dates per year (entry);
   - whipsaw ≤ 10% and cost ≤ 1.0%/yr (exit gap / buffer);
   - the largest K with ≥ 80% utilisation.
5. **Winner drift:** no trimming above 10% after entry (v1), or a fixed trim rule.
6. **Authorise P7-CP3:** one QuantConnect host run plus offline mechanics. Score tables only; no returns.

**STOP.** Not done:
- no return-based validation and no backtest;
- no thresholds or weights chosen by profit;
- no score-vs-return relationship;
- no portfolio size chosen;
- no 2018–2021; no Holdout.

---

**Programme totals:**
- 19 hypotheses tested (H001–H021). Phase 7 has no hypothesis id yet; one is assigned when a strategy is authorised.
- 63 strategy / infrastructure ids.
- No new runs in P7-CP2.
