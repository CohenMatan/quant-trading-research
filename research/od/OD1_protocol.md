# OD-1 — Outcome-driven discovery study (owner D308): frozen protocol

**Status:** FROZEN before any forward return is computed. The SHA-256 is pinned in `qresearch.od1` together with the host, the pure module and the evaluation rule. **EXPLORATORY:** 2010–2021 is exposed development data, and nothing here is independent validation. No 1999–2009 data, no Holdout and no purchase.

## 1. Sources and integrity rules

| Item | Rule |
|---|---|
| Prices / volume | QuantConnect's **Fundamental stream**, one row per security per session (as host X807): adjusted price (split- and dividend-adjusted; ratios give total return) and dollar volume. No OHLC (see §6). The run starts **2010-01-04 with no warm-up**: no market datum before 2010 is read. |
| SPY | Harness clock; total-return index from closes plus distributions (as X807) |
| Universe | Each month-end review t is the **UCR-1 repaired universe**: vendor-eligible (common, NYSE / Nasdaq / AMEX, point-in-time cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) plus SEC-repaired securities (frozen `qr_ucr`, RR6). Same code path as X807 / H032. RR6 = INCONCLUSIVE (residual gap ≤ 4.4% / yr). |
| Identity, SIC, share issuance | Frozen `qr_os1.identity` / `classify` on the two pinned objects `rr/ucr_sec_v1.json` and `rr/os1_sec_v1.json` |
| Fundamentals | New plain-JSON SEC extension object **`rr/od1_sec_v1.json`**, built offline from the same public SEC cache (`research/od/build_od1_sec.py`). It holds, per ORIGINAL periodic filing (10-K / 10-KT / 10-Q / 10-QT, filed 2010-01-01 → 2021-12-31), only values tagged with that filing's own accession number, i.e. as filed. Usable from the day after the filing date: strictly before review t. |
| Decision reviews | Month-end sessions **2011-01 → 2021-11** (131). The first review needs 252 sessions of 2010+ history. |
| Outcome labels | Adjusted price at review k+h divided by that at review k, for **h = 3 / 6 / 12 / 24 months**. A security that leaves the stream before k+h takes its **last observed adjusted price** (delisting at the last real close; flagged `left`). Labels never extend past the 2021-11 review, so the Holdout is never read. |
| Export | Aggregates only (counts, means, quantiles, per-review cross-sectional statistics), as plain JSON lines `OD1|…`. No identifiers, prices or per-security rows. |

## 2. Outcome definitions (Stage A)

For observation (i, k) and horizon h:
- **TR** = total return.
- **EX** = TR − SPY TR.
- **SR** = TR − median TR of the observation's FF12 sector at k (SIC from the latest periodic filing; the sector is unknown when there is no identity).
- **BA** = TR − β·SPY TR, with ex-ante 252-session β.
- **MAE** = the worst drawdown of the adjusted price at review checkpoints within the horizon (monthly granularity).

**Groups within the cross-section of review k:**
- **W** (exceptional winner) = top 10% of EX.
- **L** (major loser) = bottom 10% of EX.
- **M** (ordinary) = 40th–60th percentile of EX.
- **S** (severe loss) = TR ≤ −20% (h = 3 / 6) or ≤ −30% (h = 12 / 24).
- **B** (big winner, h = 12) = TR ≥ +100%.

**Periods:**
- **DISC:** decision k with label end ≤ the 2017-12 review.
- **STRESS:** decision ≥ 2018-01 with label end ≤ 2021-11.
- **ALL:** both periods.
- Discovery labels never use stress-period prices.

**Reported:**
- pooled and per-year distributions;
- concentration: the share of the cross-section's summed TR (one dollar per stock) contributed by its top 1 / 5 / 10% of observations (median over reviews), and the share of stocks with TR > 0;
- gain path for W at h = 12: share of the log gain from the best month; months up out of 12;
- `left` rates by group.

## 3. Features (Stage B / C)

All features are computed at review t from data dated ≤ t only, before any label exists. They are computed in-host, and labels are joined only in the end-of-run summary. c is the adjusted price and v the dollar volume, over the last 253 sessions; r is the daily return.

### Technical (T01–T30)

| Code | Definition | Family / prior work |
|---|---|---|
| T01 MOM12_1 | c[−22] / c[−253] − 1 | momentum (H002, H019 S1) |
| T02 MOM6_1 | c[−22] / c[−127] − 1 | momentum |
| T03 MOM3 | c[−1] / c[−64] − 1 | intermediate trend |
| T04 REV1M | c[−1] / c[−22] − 1 | reversal (H001) |
| T05 HI52 | c[−1] / max(c) | 52-week high (H003) |
| T06 LO52 | c[−1] / min(c) − 1 | rebound from lows |
| T07 TREND200 | c[−1] / mean(c[−200:]) − 1 | trend |
| T08 SLOPE200 | mean(c[−200:]) / mean(c[−221:−21]) − 1 | trend slope |
| T09 MA50_200 | mean(c[−50:]) / mean(c[−200:]) − 1 | trend state |
| T10 ID | sign(r12) × (%neg − %pos), over 252 daily returns | frog-in-the-pan (H019 S2) |
| T11 UPDAYS | share of positive daily returns, 252 | consistency |
| T12 VOL63 | sd of daily log returns over 63 × √252 | volatility (LOWVOL) |
| T13 VOLRATIO | sd21 / sd126 | volatility contraction |
| T14 MAXDD252 | min(c / cummax(c)) − 1 | correction depth |
| T15 RANGECOMP | (max − min) / mean over the last 21, divided by the same over the last 126 | compression |
| T16 DVSURGE | mean(v[−20:]) / mean(v) | volume expansion |
| T17 UPDV63 | Σ v on up days / Σ v on down days, last 63 | price advances on volume |
| T18 BIGUP | count of r > +5%, 252 | large up moves |
| T19 BIGDN | count of r < −5%, 252 | large down moves |
| T20 RS6 | (c[−1] / c[−127]) / (SPY[−1] / SPY[−127]) − 1 | relative strength |
| T21 DOWNMKT | mean(r − r_SPY) on SPY-down days, 252 | strength in weak markets |
| T22 BETA | OLS of daily r on r_SPY, 252 (≥ 200 pairs) | beta (control) |
| T23 MONTHSUP | number of positive 21-session blocks among the last 12 | persistent leadership |
| T24 SECREL6 | MOM6_1 − sector median MOM6_1 at t | sector-relative strength |
| T25 BREAKOUT | 1 if max(c[−5:]) ≥ max(c[:−5]) and mean(v[−5:]) / mean(v[−55:−5]) ≥ 1.5 | breakout on volume (H006 family) |
| T26 BASE | 1 if HI52 ≥ 0.95 and RANGECOMP ≤ 0.6 | consolidation near high |
| T27 SIZE | log point-in-time market cap (vendor, or SEC-repaired) | size (control) |
| T28 ACCUM63 | count of days in the last 63 with r > 0 and v > 2 × mean(v[−63:]) | accumulation-like events |
| T29 TRENDAGE | consecutive sessions, up to 200, with c > its trailing 50-session mean (the 253-session window cannot hold a 252-session SMA200 history) | trend maturity |
| T30 EXT50 | c[−1] / mean(c[−50:]) − 1 | distance from MA50 (extension) |

A technical feature is missing when its window has more than 10% missing sessions.

### Fundamental (F01–F17)

Non-financial registrants only (SIC outside 6000–6799).

**Inputs:**
- "Latest" = the latest original periodic filing filed before t and at most 200 days old.
- "Latest 10-K" = filed before t, with period end at most 456 days before t.
- Flows come from the filing's own facts: 3-month values for a 10-Q, annual for a 10-K; the prior-year comparative from the same filing.

| Code | Definition | Prior work |
|---|---|---|
| F01 REVYOY | rev / rev_py − 1, latest filing (rev_py > 0) | growth level (H022 layer) |
| F02 REVACCEL | F01(latest) − F01(previous periodic filing, filed 50–130 days earlier) | acceleration (H029 F1) |
| F03 NICHG | (ni − ni_py) / ta, latest filing | earnings change (OF-A C3) |
| F04 GMCHG | gp / rev − gp_py / rev_py, latest filing | margin change (H029 F2) |
| F05 ROA | ni / ta, latest 10-K | profitability level |
| F06 DROA | ni / ta − ni_py / ta_py, latest 10-K | ΔROA (OC-2, H029 F5) |
| F07 AG | ta / ta_py − 1, latest 10-K | asset growth (H024 AG) |
| F08 OCFTA | ocf / ta, latest 10-K | cash generation (H024 CBOP-like) |
| F09 ACCR | (ni − ocf) / ta, latest 10-K | accruals (H024 ACC) |
| F10 DLEV | (ta − eq) / ta − (ta_py − eq_py) / ta_py, latest 10-K | leverage change |
| F11 REPURCH | −NSI from frozen `qr_os1` (12-month split-adjusted share change; higher = more repurchase) | H032 |
| F12 EY | ni (latest 10-K) / point-in-time cap | valuation |
| F13 SP | rev (latest 10-K) / cap | valuation |
| F14 BM | eq (latest 10-K) / cap | value (H024 BM) |
| F15 GPA | gp / ta, latest 10-K | H016 |
| F16 REVCONS | number of the last 4 periodic filings (all within 450 days) with REVYOY > 0 | consistency |
| F17 NICONS | number of the last 4 with ni > ni_py | earnings stability |

## 4. Aggregates (Stage B–F)

**Decile tables.** Group statistics are exported as compact lists in the fixed order `qr_od1.STAT_KEYS`, and `OD1_eval` unpacks them. For every feature (binary features: two groups; F16 / F17 / T23: their integer values), each review k, cross-sectional deciles among valid observations, every horizon and every period. For each group:
- n;
- mean and median EX;
- trimmed mean EX (top 1% of the group's observations removed);
- mean TR, SR and BA;
- P(EX > 0), P(W), P(L), P(S);
- mean MAE;
- `left` rate.

**Per-review series** (feature × horizon):
- D10 − D1 mean EX;
- top-decile mean EX minus the universe mean;
- rank IC of the feature with EX;
- **partial rank IC**: Pearson correlation of the feature rank and the EX rank after both are residualised by OLS on the ranks of MOM12_1, SIZE, BETA, VOL63 and FF12 dummies; F features also on ROA.

**Profiles.** For W / L / M / all (h = 6 and 12, per period): the share of observations in the feature's top quintile and in its bottom quintile, and the mean feature percentile.

**Breakdowns** (h = 12, D10 − D1 mean EX and top-decile excess over the universe, pooled per period):
- by FF12 sector;
- by size tercile;
- by SPY-up vs SPY-down label windows;
- by decision calendar year.

**Combined grids (Stage D)** — exactly these six, each 3 × 3 terciles within review. Same statistics as the decile tables, at h = 6 and 12:

| Grid | Rows × columns | Question |
|---|---|---|
| D1 | MOM12_1 × REVACCEL | price strength confirmed by accelerating business? |
| D2 | TREND200 × DROA | trend confirmed by profitability improvement? |
| D3 | MOM6_1 × NICHG | earnings strength without price strength? |
| D4 | HI52 × OCFTA | leaders confirmed by cash generation? |
| D5 | BREAKOUT (2) × REVYOY | failed vs successful breakouts by business growth |
| D6 | RS6 × REVCONS (≤ 1 / 2 / ≥ 3) | persistent leadership with consistent growth? |

**Source consistency (for §6).** Per review, the mean and median of TR and EX (h = 3 and 12) over the universe.

**Uncertainty.** Every per-review series is reported with its mean, Newey–West t (lag h − 1, monthly) and the number of non-overlapping periods. These t-values are **descriptive**. The partial IC does not remove latent-factor confounding (OC-CP5), and nothing here is validated alpha.

## 5. Stage G — candidate rule (fixed now; exploratory)

A feature, decile or grid cell is a **candidate** only if **all** of the following hold:

| # | Criterion |
|---|---|
| G1 | DISC, h = 12: the group's mean EX ≥ +4.0% and trimmed mean EX ≥ +2.0%, with n ≥ 1,000 observations from ≥ 48 reviews. For deciles, the group is the decile with the highest DISC mean EX; that choice of direction is part of the multiplicity, disclosed. |
| G2 | DISC partial rank IC (h = 6) in the group's direction: mean NW t ≥ 2.0 |
| G3 | STRESS: the same group's mean EX (h = 12) ≥ +2.0%, and the partial IC has the same sign |
| G4 | The group beats the universe mean EX (h = 12) in ≥ 7 of the decision years 2011–2020 that carry labels, and the best single year supplies ≤ 40% of the summed positive yearly excess |
| G5 | The top-minus-bottom (or group-minus-universe) spread is positive in ≥ 7 of the 11 non-financial FF12 sectors (pooled ALL), and in all three size terciles |
| G6 | Distinctness: a feature that duplicates a rejected hypothesis (T01 / T02 → H002 / H019; T05 → H003; T10 → H019 S2; T25 → H006; F06 → OC-2; F02 → H029 F1; F07 / F09 / F14 / F15 → H024 / H016; F11 → H032) may be reported, but only as **"re-observation of a rejected family"**. It is never a new candidate unless a grid shows information beyond the parent (Stage D) |

**Outcomes:**
- Up to three candidates are ranked by G2 t, then G3.
- **Stage H runs only if at least one non-duplicate candidate passes G1–G6.**
- Otherwise the report states **"no usable relationship"** and no strategy is built.
- **Multiplicity disclosed:** 47 features × 10 deciles × 4 horizons, plus 6 grids × 9 cells, were examined. With that many looks, a few G1-level groups are expected by chance.

## 6. WIKI candlestick and visual study (local; 2011–2016 decisions)

Purpose: the OHLC-dependent behaviours that the Fundamental stream cannot measure.

**Data, sample and exclusions:**
- WIKI file with SHA-256 matching the manifest.
- The frozen chart-discovery sampler's frame: SEC frame registrants with MATCHED identity, excluding the 58 adjustment-defect tickers and window defects.
- Month-end decisions 2011-01 → 2016-12; h = 12 labels from WIKI adjusted closes, ending ≤ 2017-12. SPY = E900-08 equity (98% SPY).
- No QuantConnect data leaves the cloud. WIKI rows and images stay local.

**Candlestick features (21 / 63 sessions):**

| Code | Definition |
|---|---|
| K1 CLV21 | mean (C − L) / (H − L) |
| K2 GAPUP63 | count of open / prior close ≥ +3% where the session closes above the prior close |
| K3 GAPDN63 | count of open / prior close ≤ −3% |
| K4 BIGBODY63 | count of \|C − O\| / O ≥ 4% |
| K5 UPWICK21 | mean (H − max(O, C)) / (H − L) |
| K6 LOWICK21 | mean (min(O, C) − L) / (H − L) |
| K7 ATRPCT21 | ATR21 / C |
| K8 ATRCHG | ATR21 / ATR126 |

Each is reported with the same decile statistics (h = 12; DISC-only years) plus the partial IC on MOM12_1 / SIZE (public-float proxy) / VOL63 / BETA.

**Source consistency:**
- Per-review universe mean TR (h = 3 / 12) on WIKI vs the QuantConnect aggregate: correlation and mean difference.
- The WIKI result is labelled **NOT CONSISTENT** if the h = 12 correlation is < 0.8 or the mean absolute difference is > 3 points.

**Blinded visual discrimination test:**
- Seed 20261025: 40 W, 40 L and 40 M observations (h = 12, EX groups within review) drawn from the WIKI frame across 2011–2016, at most one per registrant per group.
- Rendered with the frozen chart-discovery renderer: 252 bars, the decision bar last, no labels.
- Shuffled and viewed **blind**. For each chart, a prediction from {likely outperform, neutral, likely underperform} plus visible-feature tags, recorded before unblinding.
- Then unblinded.
- **Reported:** accuracy vs the 1/3 chance level, the W-vs-L hit rate, and a binomial p.
- **Visual information = "present"** only if W-vs-L classification accuracy ≥ 65% (excluding "neutral") with a binomial p < 0.01.

## 7. Stage H (only if §5 yields a candidate)

- A separate specification is frozen before any strategy run: one strategy, its fixed controls (SPY, the eligible-universe equal-weight baseline, and a matched control of same-month, same-sector, same-size-tercile names without the signal).
- Constraints: $100K, ≤ 15 positions, 10% initial cap, $5K minimum, ≤ 3 per sector, $7 + 10 bps, next-open execution, no grid.
- If §5 yields nothing, Stage H is not run.

## 8. Runs

- **E808-01:** host X808, infrastructure (exploratory outcome study, not a strategy trial), AUDIT 2010-01-04 → 2021-12-31, default build. One documented infrastructure retry (E808-02).
- The object `rr/od1_sec_v1.json` is uploaded, then the run waits ≥ 35 minutes for Object Store visibility (D268).
