# H020 threshold provenance (P5-CP2)

This table is the audit trail for every number in the H020 chart score (`src/qresearch/lean/qr_chart.py`, frozen with `research/phase5/H020_spec.md`).

> **Practitioner rules are hypotheses / frameworks, not proof of predictive alpha.** A threshold that a practitioner wrote down is a definition we borrow so that we do not invent (and tune) one ourselves. It is not evidence that the rule predicts returns. H020 exists to test that.

## Source types

| Code | Meaning |
|---|---|
| **A** | Practitioner explicit: the practitioner source states this threshold (or this exact concept with this number) |
| **B** | Derived from a practitioner rule: a mechanical translation, such as days → weeks, an index rule applied to a stock, or a buy-price rule applied to support |
| **C** | Academic: a peer-reviewed paper supports the concept (never the exact threshold, unless stated) |
| **D** | Engineering convention: needed to compute anything at all; chosen for robustness and computability, not for returns |
| **E** | Our design: chosen in P5-CP1/P5-CP2 from construction logic only. **No real chart or return was looked at.** |

**"Exact / interpreted"** says whether our formula is the source's own wording (exact) or our operationalisation of a verbal rule (interpreted).

**How the sources were verified.** Practitioner thresholds were checked on 2026-10-05 against secondary summaries of the books (search records listed in `research/phase5/P5_CP1_references.md` and below). The primary book texts were **not** accessed. Where only a secondary summary supports a number, the row says so.

**Secondary sources used for the numbers:**
- **O'Neil, *How to Make Money in Stocks*** (cup-with-handle, CAN SLIM, as summarised by IBD / Investor's Business Daily educational pages and book summaries):
  - cup-with-handle base length 7–65 weeks;
  - cup depth typically 12–15% up to about 33% in normal markets;
  - breakout volume at least 40–50% above average;
  - do not buy more than 5% above the pivot (buy point);
  - cut every loss at 7–8% below the purchase price.
- **Minervini, *Trade Like a Stock Market Wizard* (2013): trend template**, as summarised by chartmill and others:
  - price above the 150-day and 200-day MAs;
  - 150-day above the 200-day;
  - 200-day MA trending up for at least 1 month (preferably 4–5 months);
  - 50-day above the 150-day and 200-day;
  - price above the 50-day;
  - price at least 30% above the 52-week low;
  - price within 25% of the 52-week high;
  - RS rank ≥ 70.
- **Minervini: VCP.** Successive contractions get smaller, typically 2–4 (sometimes up to 6), and volume dries up. The contraction count is from a secondary summary.
- **Weinstein, *Secrets for Profiting in Bull and Bear Markets* (1988):**
  - the 30-week moving average;
  - Stage 2 = price above a rising 30-week MA after a base breakout, with increased volume. The book does not quantify the volume increase in the summaries.
- **IBD distribution day:**
  - a major index falls ≥ 0.2% on higher volume than the prior session;
  - 4–6 within about 4–5 weeks signals institutional selling;
  - a distribution day expires after 25 sessions.
  - It is an **index** rule.

## The 20 conditions

| Rule | Formula (at decision close t; bars ≤ t only) | TF | History | Threshold | Source | Type | Exact / interpreted | Notes |
|---|---|---|---|---|---|---|---|---|
| **W1** | weekly close > SMA30(weekly closes) | W | 30 weeks | 30-week MA | Weinstein stage analysis (30-week MA; Stage 2 above it) | **A** (MA length) / B (close-above test) | interpreted | Weekly close of the decision week |
| **W2** | SMA40w(t) > SMA40w(t − 4 weeks) | W | 44 weeks | rising over 4 weeks | Minervini: 200-day MA trending up ≥ 1 month | **B** | interpreted (200 d ≈ 40 w; 1 month ≈ 4 w) | Minimum period of the rule, not the preferred 4–5 months |
| **W3** | SMA10w > SMA30w | W | 30 weeks | — | Minervini: 50-day MA above the 150-day MA | **B** | interpreted (50 d ≈ 10 w, 150 d ≈ 30 w) | |
| **W4** | weekly structure state ∈ {strong_uptrend, uptrend} (confirmed weekly swing points: HH/HL; break above the last swing high) | W | ≥ 2 weekly swing highs and lows within 104 weeks | swing definition: k = 3, prominence 1 ATR(10w), tolerance 0.5 ATR | Dow-theory concept "higher highs and higher lows" (classical, unquantified) | concept A; **all numbers D/E** | interpreted | State table in the spec §6 |
| **W5** | close ≥ 0.75 × 52-week high (max daily high, last 252 sessions incl. t) | D | 252 sessions | 25% | Minervini: within 25% of the 52-week high | **A** | exact | Academic context: George & Hwang (2004), nearness to the 52-week high predicts returns (**C**, concept only, not this cut-off; already tested here as H003) |
| **B1** | a valid base exists: anchor = the most recent confirmed weekly swing high that is the highest weekly high of the prior 26 weeks; length L = weeks since the anchor; 7 ≤ L ≤ 65 | W | anchor ≤ 104 weeks back | 7–65 weeks | O'Neil: cup-with-handle 7–65 weeks | **A** (range) / **E** (anchor rule, 26-week window) | interpreted | O'Neil's range is for the cup-with-handle; we apply it to every base type |
| **B2** | valid base AND depth = 1 − (lowest weekly low since the anchor / anchor high) ≤ 0.33 | W | base | 33% | O'Neil: cup depth up to about 33% in normal markets | **A** | interpreted (upper normal bound used as a hard cap; O'Neil allows deeper bases in bear markets — we do not) | |
| **B3** | valid base AND mean true range (t−14 … t−5) / mean true range (t−64 … t−15) ≤ 0.80 | D | 65 sessions | 0.80; windows 10 / 50 sessions | Minervini VCP: volatility contracts into the pivot | concept **A**; threshold and windows **E** | interpreted | Excludes the last 4 sessions so the trigger day does not cancel the contraction |
| **B4** | valid base AND mean volume (t−14 … t−5) / mean volume (t−64 … t−15) ≤ 0.80 | D | 65 sessions | 0.80; windows as B3 | O'Neil / Minervini: volume dries up in the base | concept **A**; threshold and windows **E** | interpreted | Volume role 1 of 3 (spec §11) |
| **B5** | valid base AND ≥ 2 pullbacks inside the base (weekly swing high → next weekly swing low), each strictly smaller than the previous | W | base | ≥ 2 contractions, strictly decreasing | Minervini VCP: each contraction smaller, typically 2–4 | **A** (concept) / **B** (≥ 2 = lower end of "typically 2–4") | interpreted | |
| **T1** | fresh breakout: close > base pivot P (= anchor high); the current run of closes above P began within the last 5 sessions and after the anchor week | D | base | 5 sessions | O'Neil: buy as the stock breaks above the pivot | concept **A**; pivot = anchor high and 5-session freshness **E** | interpreted | O'Neil's pivot is the handle high; ours is the left-side base high (one definition, no handle detection) |
| **T2** | T1 AND close ≤ 1.05 × P | D | — | 5% | O'Neil: do not buy more than 5% above the pivot | **A** | exact (measured at the decision close) | |
| **T3** | T1 AND volume on the first breakout day ≥ 1.40 × mean volume of the 50 prior sessions | D | 50 sessions | +40%; 50-session average | O'Neil: breakout volume ≥ 40–50% above average | **A** (40%, lower end) / **B** (50-day average as "average volume", the usual IBD convention) | interpreted | Volume role 2 of 3 |
| **T4** | T1 AND close location of the first breakout day (close − low)/(high − low) ≥ 0.5 | D | — | 0.5 | Practitioner prose "close near the high of the day" is not quantified | **E** | — | |
| **T5** | close > SMA50(daily closes) | D | 50 sessions | 50-day MA | Minervini: price above the 50-day MA | **A** | exact | |
| **R1** | risk = 1 − support / close ≤ 0.08, support = the highest of: nearest daily support-zone top, the support trendline value below the close, a broken base pivot P below the close, the most recent confirmed daily swing low below the close | D | 252 sessions | 8% | O'Neil: cut losses at 7–8% below the purchase price | **B** | interpreted (the loss rule applied to distance to support) | The support set is **E** |
| **R2** | risk ≤ 2.5 × ATR(20)% | D | 20 sessions | 2.5 ATR | ATR-based stop distances are common practice (Wilder's ATR concept); the multiple is not from a specific source | **E** | — | |
| **R3** | (close / SMA20 − 1) / ATR(20)% ≤ 2.0 | D | 20 sessions | 2 ATR | Practitioners warn against "extended" entries; not quantified | **E** | — | |
| **R4** | distribution days ≤ 4 in the last 25 sessions (day return ≤ −0.2% on higher volume than the prior day) | D | 26 sessions | −0.2%, ≤ 4, 25 sessions | IBD distribution-day rule (index) | **B** | interpreted (index rule applied to the stock; fails at 5, inside IBD's "4–6") | Volume role 3 of 3 |
| **R5** | daily structure state ∈ {strong_uptrend, uptrend, range} | D | ≥ 2 daily swing highs and lows within 300 sessions | swing k = 5, prominence 1 ATR(20), tolerance 0.5 ATR | Dow-theory concept (unquantified) | concept A; **numbers D/E** | interpreted | |

## Hard disqualifiers

| Rule | Formula | TF | Threshold | Source | Type | Reason |
|---|---|---|---|---|---|---|
| **D1** | weekly close < SMA40w | W | 40-week MA | Minervini: price above the 200-day MA (200 d ≈ 40 w) | **B** | A stock in a long-term decline is not a long setup in any of the frameworks |
| **D2** | weekly structure state = downtrend (LH + LL) | W | swing definition as W4 | Dow-theory concept | concept A, numbers **E** | Confirmed lower highs and lower lows |
| **D3** | close > 1.25 × SMA50 | D | 25% | Practitioner warnings about extended stocks; not quantified at this level | **E** | Late, extended entries |
| **D4** | no support exists below the close (empty support set) | D | — | — | **E** | Entry risk cannot be defined |
| **D5** | any open ≤ 0.85 × prior close within the last 10 sessions | D | −15% gap, 10 sessions | — | **E** | Event shock (earnings / news) — the chart reflects an event, not a pattern; no news is used, only the price gap |

## Engineering conventions and universe

| Item | Value | Type | Reason |
|---|---|---|---|
| Swing confirmation | k = 5 sessions daily, k = 3 weeks weekly, each side | **D** | Common fractal-pivot practice uses small symmetric k; the values balance noise against delay. Unchanged from P5-CP1 |
| Swing prominence | ≥ 1 × ATR over a local window of 2k bars | **D** | Removes micro-swings. A local window makes pivots independent of where the history starts |
| ATR | simple mean of true range, 20 sessions / 10 weeks | **D** | Wilder's ATR concept with a simple mean (deterministic, no seed) |
| Equal-level tolerance | 0.5 × ATR (log) | **D** | Price-scale free |
| Zones | anchored clustering (members within 2 tol of the lowest member; zone = members ± tol, so width ≤ 4 tol), ≥ 2 touches, pivots of the last 252 sessions (daily) / 104 weeks (weekly) | **D** | No chaining; a fixed look-back |
| Trendlines | 2 anchors ≥ 10 sessions apart within 252 sessions; permanently invalid once any close is beyond tol | **D** | One definition |
| History window | the snapshot reads the last 756 sessions | **D** | Every look-back fits (tested identical to full history) |
| **Universe minimum history** | ≥ 504 sessions of the stock's own bars | **D** | Every condition computable: MA40w + 4-week slope (44 weeks), the 52-week high, weekly swing points |
| Universe (other) | US common stock, point-in-time market cap ≥ $2B, close ≥ $5, ADV20 ≥ $5M | programme rules (D034 / H019) | No technical pre-screen |
| Score groups | G0 = disqualified; G1 0–5; G2 6–10; G3 11–15; G4 16–20 | **E** | Equal-width bands of the 0–20 score, fixed before any real score exists |
| Economic floor | High group (G3 + G4) ≥ +3%/yr over the cross-sectional average | **E** | Same floor as H019 (P1) |
| Monotonicity | Spearman(group index, group mean) ≥ 0.90 | **E** | Same as H019 (P2) |
| α | 1%, per statistic, intersection-union | **E** | Same α as H019 |

## What is not claimed

- No row above says that a threshold is "from Weinstein / O'Neil / Minervini" unless the cited summary gives that number for that concept. Where we translated (days → weeks, index → stock, purchase price → support), the type is **B**. Where the practitioner gives only a concept, the number is **E**.
- None of these sources shows that the rule predicts returns in ≥ $2B US stocks in 2010–2017. The academic rows (C) support concepts only.
