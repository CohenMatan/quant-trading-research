# Phase 4 literature review: Weekly trend / momentum stock selection (P4-CP1, 2026-10-04)

- **Purpose:** decide, **before** any Weekly return is computed, whether a low-turnover Weekly trend/momentum stock-selection architecture rests on a rationale distinct from the failed daily Phase 3 search.
- **Citations:** from memory, with year and venue. **Verify before quoting any magnitude.** Where I am unsure, I state the direction only.
- **Rows are tagged** **[A]** academic (peer-reviewed or widely cited working paper), **[P]** practitioner convention, **[I]** our inference.
- **Not used:** no project Weekly result (none exists); no 2018–2021 candidate data; no Holdout knowledge. Phase 3's result is used only as a **methodological** lesson (fake winners), never to choose parameters.

## 1. Medium-term momentum and trend persistence in stocks

| Tag | Source | Finding | Consequence for Phase 4 |
|---|---|---|---|
| [A] | Jegadeesh & Titman (1993), JF; (2001), JF | Winners over 3–12 months outperform losers over the next 3–12 months; the profit **reverses** in years 2–5 | Horizons of 3–12 months are the evidence base. **Holding beyond ~12 months has no momentum support (reversal risk)** |
| [A] | Novy-Marx (2012), JFE, "Is momentum really momentum?" | Intermediate past returns (months 7–12) drive most of the momentum profit | Lookbacks of 26–52 weeks rather than 13 |
| [A] | Hong, Lim & Stein (2000), JF | Momentum is weaker in large, well-covered stocks (slow information diffusion in small ones) | **Our ≥ $2B universe is where momentum is weakest** |
| [A] | Daniel & Moskowitz (2016), JFE; Barroso & Santa-Clara (2015), JFE | Momentum crashes after market rebounds; volatility scaling helps | Long-only and trend-filtered books avoid some of the crash (the short leg drives most of it), but not all |
| [A] | George & Hwang (2004), JF | Nearness to the 52-week high predicts returns and partly subsumes momentum; it reverses less in the long run | A distinct **range-position** family, admitted as a confirmation |
| [A] | McLean & Pontiff (2016), JF | Published anomalies lose ≈ a third or more of their return after publication | Expect post-2010 effects to be smaller than in-sample published numbers |
| [I] | Phase 1 of this project | H002 (momentum), H003 (52-week high), H006 (breakout) and H008 (residual relative strength) all failed the screen with daily decisions and fixed or rule-based exits | **The same information families have already failed here in other wrappers.** Phase 4 differs in the exit and holding architecture, not in the information used |

## 2. Moving-average / time-series trend rules

| Tag | Source | Finding | Consequence |
|---|---|---|---|
| [A] | Brock, Lakonishok & LeBaron (1992), JF | MA and breakout rules predicted Dow index returns 1897–1986 | Classic families; index-level evidence |
| [A] | Faber (2007), J. Wealth Management; Zhu & Zhou (2009), JFE | A 10-month (≈ 43-week) SMA as an asset-class timing filter reduces drawdowns at similar returns | Supports MA lengths of ~30–40 weeks; **asset-class timing, not stock selection** |
| [A] | Moskowitz, Ooi & Pedersen (2012), JFE | Time-series momentum (12-month sign) in futures | Asset-class evidence |
| [A] | Huang, Li, Wang & Zhou (2020), JFE, "Time-series momentum: is it there?" | Much TSMOM predictability disappears under proper pooled tests | Weakens the TSMOM prior |
| [A] | Han, Yang & Zhou (2013), JFQA | MA timing applied to cross-sectional portfolios earns most in **high-volatility (small, illiquid)** deciles | Weak in large caps |
| [A] | Zakamulin (2014, 2017; book *Market Timing with Moving Averages*, 2017) | Out-of-sample MA-rule advantages are much smaller than in-sample; the main benefit is drawdown reduction in bear markets, with whipsaw costs in sideways markets | Expect the exit rule to change **risk**, not necessarily terminal wealth vs SPY, in a rising market (2010–2017) |
| [A] | Marshall, Nguyen & Visaltanachoti (Quantitative Finance, ≈ 2017; venue to verify) | TSMOM and MA rules capture largely the same information | Do not count close > MA and return > 0 as independent: **one direction group** |
| [P] | Weinstein (1988), *Secrets for Profiting in Bull and Bear Markets* | The 30-week MA "stage analysis" for individual stocks | Practitioner anchor for L = 30 weeks; no out-of-sample academic test of its own |
| [P] | Common convention | The 50/200-day "golden cross" ≈ 10/40 weeks | Anchor for SMA(S) / SMA(L) ≈ 1:3 |

## 3. Oscillators, trend strength, volume, volatility

| Tag | Source | Finding | Consequence |
|---|---|---|---|
| [P] | Wilder (1978), *New Concepts in Technical Trading Systems* | RSI(14), ADX(14) | Practitioner origin; the parameters are conventions, not estimates |
| [P] | Appel (MACD, 1970s) | MACD(12, 26, 9) | Practitioner. MACD line > 0 ≡ EMA12 > EMA26 (direction group); the histogram (line vs signal) is acceleration |
| [A] | Few credible peer-reviewed tests of RSI / ADX / MACD as cross-sectional stock selectors in large caps; most evidence is index-level or forum backtests | — | **Low prior weight.** Admitted only as one entry-confirmation group with the conventional values, not searched widely |
| [A] | Lee & Swaminathan (2000), JF | High-volume winners have **lower** future returns; low-volume winners persist longer | The sign of a volume confirmation is ambiguous for long-only momentum; **excluded from the grammar** |
| [A] | Ang, Hodrick, Xing & Zhang (2006), JF; Baker, Bradley & Wurgler (2011), FAJ | Low volatility earns relatively more per unit risk | A risk filter (as in Phase 3). Note: Phase 1 H005 (low volatility) failed Validation here |
| [I] | ATR%, Bollinger-band width, realised volatility | The same volatility information | One volatility measure only (26-week realised volatility rank) |

## 4. Exits, holding and "let winners run"

| Tag | Source | Finding | Consequence |
|---|---|---|---|
| [A] | Shefrin & Statman (1985), JF; Frazzini (2006), JF | The disposition effect (investors sell winners too early) is linked to under-reaction and momentum | A behavioural reason why holding winners while the trend persists **could** add value |
| [A] | Jegadeesh & Titman (2001) | Long-run reversal after ~12 months | Counter-argument: very long holds may give back gains. **The trend-state exit is the only protection** |
| [P] | Covel, *Trend Following*; Faith, *Way of the Turtle*; Clenow, *Stocks on the Move* | Trend-following practice: cut losers, let winners run, with state- or trailing-based exits; ranking by momentum within a market-trend filter (Clenow) | Practitioner convention; the evidence is mostly futures and survivor-biased stock samples |
| [I] | Our cost model | A state exit lowers turnover only if trend states persist: weekly evaluation halves or quarters re-entry churn compared with daily evaluation | The cost advantage is mechanical and **verifiable before the search** (feature-only turnover canary) |

## 5. What the evidence implies [I]

1. **The economic rationale is medium-term momentum / trend persistence with a disposition-effect argument for letting winners run.**
   - This is the most credible family in the technical literature.
   - Its large-cap, post-publication strength is modest.
   - It is expected to be weakest exactly in our universe (Hong, Lim & Stein).
2. **Weekly sampling adds no new information:** a weekly close is a daily close.
   - Its real advantages are mechanical: fewer decisions, lower turnover and costs, a holding period chosen by the trend itself.
   - "Less noise" is only true in the sense of fewer, slower decisions.
3. **What is genuinely different from Phase 3:**
   - a state-based exit instead of a fixed 63-session hold;
   - momentum (relative strength) ranking instead of each primary's own strength;
   - a much smaller, more literature-anchored space (240 configurations instead of 1,533).
4. **What is not different:** the information families. Phase 3's grammar already contained close > SMA, SMA crosses, K-month returns and 52-week-high proximity on daily data, and Phases 1–3 found no robust edge from them.
5. **Prior:** a modest edge (≈ 1–3% a year over a random book) is plausible. An edge large enough to be detected here (see the power study) is unlikely.
