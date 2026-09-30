# Phase 2 literature review: trend, momentum, pullbacks and technical rules

**Purpose.** This review gives the external evidence behind the Phase 2 proposal (`docs/checkpoints/P2_CP0_research_proposal.md`).

**How to read the citations.**

- References are cited from memory. Each should be verified against the original before it is quoted with numbers. Nothing here reports a specific coefficient as a claim of ours.
- Each paper's **publication year** is marked relative to our periods: IS 2010–2017, VAL 2018–2021.
- Work published before 2010 cannot carry look-ahead about our test periods.
- Later work is used only as a **caution** (for example about costs), never to choose rules.

## 1. What the literature supports

| Topic | Evidence | Published | What it says, and its relevance here |
|---|---|---|---|
| Cross-sectional momentum | Jegadeesh & Titman (1993, *J. Finance*); Jegadeesh & Titman (2001, *J. Finance*); Carhart (1997) | pre-2010 | Stocks with high past 3–12-month returns keep outperforming for 3–12 months. The standard design skips the most recent month (12-1) because of short-term reversal. Supports: holding recent winners for months, and a 12-1 ranking. |
| Where momentum lives | Novy-Marx (2012, *JFE*), "Is momentum really momentum?" | 2012; data before our IS | Intermediate (7–12 month) past returns carry most of the effect. **Caution only.** |
| Momentum across asset classes | Asness, Moskowitz & Pedersen (2013, *J. Finance*) | 2013; data before our IS | Momentum is pervasive. **Caution only.** |
| Time-series momentum (trend) | Moskowitz, Ooi & Pedersen (2012, *JFE*) | 2012; data before our IS | An asset's own 12-month return predicts its sign. Studied on futures, not single stocks. **Caution only.** |
| Moving-average trend rules | Brock, Lakonishok & LeBaron (1992, *J. Finance*) | pre-2010 | Simple MA rules (including 50/150/200-day) had predictive power on the Dow Jones 1897–1986. |
| Data-snooping check of MA rules | Sullivan, Timmermann & White (1999, *J. Finance*) | pre-2010 | After correcting for data snooping, the best technical rules **stopped** outperforming after 1986. Supports strong multiple-testing discipline and **pre-registration**. |
| Survey of technical analysis | Park & Irwin (2007, *J. Economic Surveys*) | pre-2010 | Many studies found profits, but much of the evidence suffers from data snooping, ex-post rule selection and cost omission. Profits weaken in later samples. |
| MA-based allocation | Faber (2007, *J. Wealth Management*) | pre-2010 | A 10-month (≈ 200-day) MA filter reduced drawdowns of asset classes, mainly by avoiding long bear markets. Mostly a risk-reduction result, not higher returns. A practitioner source. |
| MA timing and volatility | Han, Yang & Zhou (2013, *JFQA*) | 2013 | MA timing profits concentrate in high-volatility portfolios. **Caution only.** |
| Short-term reversal | Jegadeesh (1990, *J. Finance*); Lehmann (1990, *QJE*) | pre-2010 | Returns over 1 week to 1 month partially reverse. This is the classic basis for "buying the dip". |
| Reversal and liquidity | Avramov, Chordia & Goyal (2006, *J. Finance*) | pre-2010 | Short-term reversal profits concentrate in **illiquid** stocks and largely disappear after costs. **Important for us:** in a ≥ $2B large-cap universe, a pure dip-buying edge should be weak. Consistent with our H001 result. |
| Reversal conditioned on news | Da, Liu & Schaumburg (2014, *Management Science*) | 2014 | Reversal is stronger once news/fundamental components are removed. **Caution only.** H004 already cited it in the same spirit. |
| Chart patterns, algorithmically | Lo, Mamaysky & Wang (2000, *J. Finance*) | pre-2010 | Kernel-smoothed chart patterns carry some incremental information. It needs substantial smoothing machinery, and the effect is modest. |
| Consistency of past returns | Grinblatt & Moskowitz (2004, *JFE*) | pre-2010 | Consistent past winners outperform. Weakly supports preferring established trends over single jumps. |
| Momentum and volume | Lee & Swaminathan (2000, *J. Finance*) | pre-2010 | High-volume winners reverse sooner; the sign of volume information is ambiguous for entries. |
| Costs of anomaly strategies | Lesmond, Schill & Zhou (2004, *JFE*); Korajczyk & Sadka (2004, *J. Finance*) | pre-2010 | Momentum profits shrink substantially after realistic costs, especially at high turnover. |
| Costs of anomalies, broadly | Novy-Marx & Velikov (2016, *RFS*) | 2016 | Strategies with monthly turnover above roughly 50% rarely survive costs. **Caution only.** It matches our own C01–C03 finding. |
| Stop-losses | Kaminski & Lo (2014, *J. Financial Markets*) | 2014 | Stops add value only when returns are serially dependent (e.g. momentum regimes); otherwise they cost return. **Caution only.** Argues against arbitrary percentage stops. |

## 2. Common trading conventions (not evidence)

- **RSI(14):** Wilder (1978), *New Concepts in Technical Trading Systems*. The 14-period window and the 70/30 bands are Wilder's conventions, not empirically derived optima.
  - Practitioner writing (e.g. the "range shift" idea) holds that RSI stays roughly within 40–80 in uptrends, so a dip to about 40 marks a pullback in an uptrend.
  - **There is no peer-reviewed evidence that 40, 45 or a 5-day window is special.** These values are conventions.
- **50/200-day averages ("golden cross" state):** widely used conventions.
  - Brock et al. (1992) tested 50/150/200-day rules on an index, which is the nearest academic support.
  - The MA50 > MA200 state as a stock filter is a convention.
- **"Close above the prior day's high" as a reversal confirmation:** a convention (an outside or up-thrust day). No academic evidence specific to it was found.
- **Fibonacci retracements (38.2/50/61.8%):**
  - No credible academic evidence that these levels carry predictive power.
  - Any deterministic version needs a swing-high/low detector (e.g. a zig-zag with a percentage threshold), which is itself an arbitrary parameter chosen with hindsight.
  - **Recommendation: exclude.**
- **Hand-drawn trend lines:** not reproducible. Algorithmic versions need fitting choices (window, touch count, tolerance), and the nearest academic analogue (Lo et al. 2000) shows modest incremental information.
  - **Recommendation: exclude.**
- **Volume confirmation:** the evidence is ambiguous in sign (Lee & Swaminathan 2000).
  - **Recommendation: exclude as a rule; report as a diagnostic.**
- **Short averages (MA20):** redundant with RSI and the recovery condition for timing, and they add a parameter.
  - **Recommendation: exclude.**

## 3. Our own hypotheses (neither literature nor convention)

- That **waiting for a recovery** (rather than buying at the low) improves results inside an uptrend.
  - The literature supports two separate things: momentum drift over months, and short-term reversal. Reversal is weak in large caps.
  - The specific "trend + pullback + confirmed recovery" combination at a multi-month horizon is **our hypothesis to test**, not an established finding.
- That the benefit, if any, survives $7 per order plus 10 bps slippage at a 40–80+ session horizon.

## 4. Implications for the design

1. **The return source to expect is trend or momentum continuation over months.**
   - The reversal bounce is weak in large caps (Avramov et al.) and was already rejected in our own H001.
   - So the design should hold for months, and the key test is whether the entry timing (pullback + recovery) adds anything over simply holding the same uptrend stocks.
2. **Costs decide.** The literature (and our C01–C03) says high turnover kills such strategies, so the holding period must be long by design.
3. **Data snooping is the main risk in technical analysis** (Sullivan et al. 1999; Park & Irwin 2007). This calls for:
   - very few variants;
   - parameters fixed by convention before testing;
   - explicit controls;
   - multiple-testing correction.
4. **Momentum is best used as a ranking, not an additional filter.** As a filter it largely duplicates the MA trend condition. As a ranking it has the strongest pre-2010 evidence (Jegadeesh & Titman).
