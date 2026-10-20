# OS-CP1 — Offensive Score Research — Candidate Selection and First Experiment Design

**Date:** 2026-10-20 · **Decisions:** owner D274 (`docs/owner/2026-10-20_offensive_score_direction.md`), D275 (this checkpoint) · **Status: DESIGN ONLY — STOP for owner review**

**Nothing was registered, built, run, uploaded or bought.** No backtest, no new return analysis, no weight optimisation, no universe change. H028 is not reopened and the Holdout stays sealed. RR6 stays INCONCLUSIVE; H031 stays DRAFT.

## Summary

- **Answer to "is there a credible offensive score?"** Partly.
  - No mechanism we can access has credible evidence of alpha *specific to rising markets*. Upside capture above 1.0 without extra beta is the same thing as positive alpha at a beta near 1.
  - One mechanism is distinct from everything tested so far, well documented in large stocks before 2010, and testable with data already in place: **net share repurchase**. Its prior is modest, and it may turn out value-like rather than "offensive". The test is designed to show either.
- **Recommended hypothesis: OS-1, Net Share Repurchase Score.**
  - Rank eligible stocks by how much they reduced their split-adjusted shares outstanding over the last 12 months, using SEC cover-page counts as filed. Hold the Top 15, rebalance monthly, equal weight.
  - It is a fixed rule with no learned coefficients.
- **Data:** every input is already in place:
  - the point-in-time SEC object `rr/ucr_sec_v1.json` in the Object Store (D270, pending your ratification);
  - QuantConnect's universe and split factors, generated in the run.
  - No new data layer, upload or purchase.
- **First legitimate backtest:** about 2 working sessions and 3 QuantConnect runs: one no-returns canary, then two strategy runs. $0.
- **You decide** (§10): D270 ratification, exploratory protocol EDP-1, OS-1 as written, gates O1–O9, and the run authorisation.

## 1. Lessons from earlier research

| Study | What was tested | Gate that failed, and why | Lesson |
|---|---|---|---|
| H019 | 12-1 momentum, smooth momentum, trend factor (≥ $2B, 2011–2017) | Signal test: top-decile excess −2.18 / −1.20 / −2.85%/yr; IC t 0.22 / 0.34 / 0.12 | Momentum is not reproduced in our universe. "Momentum after up-markets" (Cooper, Gutierrez & Hameed 2004) is already covered: 2011–2017 was an up-state throughout |
| H024 | 11 features, 415 equal-weight models | Best model t 2.48 vs c_MODEL 4.37 (p 0.35); best single feature t 1.24 | Familiar factors carry little signal here, and model search uses up the power |
| H026 | Ridge-learned score over the H024 features, Top-15 | 1.19× SPY wealth, but S_WEALTH 0.171 < 0.2245 (D1) and 3 of 7 years ahead (D3) | All of the advantage came in SPY-down months (beta 0.80, down-capture 0.78; March 2020 = 64%). The learned score found **low volatility**, not stock selection |
| H027 | The same, against a LOWVOL-conditional null and an LV15 control | A4: behind LV15 over 2015–2017 (−0.058) | No edge beyond low-volatility exposure |
| H028 | The same with λ = 100 fixed | B4: behind LV15 over 2015–2017 (−0.006). Its null was later found structurally suspect (P13-CP5) and a repaired null was infeasible (P13-CP6) | The edge came from the 2018 / 2020 episodes; up-capture 0.97. A defensive profile, not an offensive one |
| OC-2 | ΔROA, a single-signal Fama–MacBeth test | Never reached real returns: the inference method failed synthetic validation (false approval 4.40% > 2% in a latent-factor world) | Regression tests with noisy controls cannot be validated on our data. Prefer portfolio tests with **same-universe controls** |
| H022 / H023 | Conviction score; weight search | t_IC 0.48; 80+ group −12.6%/yr; best weighting t 0.97 | Stacking familiar factors does not help |
| H017 | 8-K earnings-reaction continuation | Beat SPY (CAGR 17.5% vs 14.9%) but W2 g / SE 0.71 and R3: 74% of the excess in 2014–15 | A real-looking edge can be one episode; concentration gates matter |
| H016, H025, H018, H020, H021-A | GP/A; insider clusters; 1,533 technical rules; chart score; sector momentum | All failed their pre-registered gates | Quality, insiders, technical rules and sector rotation are exhausted on our data |
| RR1–RR7 | Platform and universe | Universe INCONCLUSIVE (RR6); packed tables refused; engine pin gated | Use plain JSON objects and generate identifiers in the run. Any test is exploratory, with the repaired and vendor universes compared |

**What these failures have in common:**
1. Every apparent "beat SPY" so far came from **defensive exposure** (low volatility) **or one episode**, never from persistent selection alpha.
2. **Searches and learned weights over familiar factors** used up the statistical power. A learned score is therefore **not recommended**: 131 monthly reviews, weak features, and a fitted score would rediscover low volatility (H026–H028).
3. Momentum, quality, low volatility, value-like and growth-level signals have been tried. A new candidate needs a **different information source**.
4. **Power is the binding limit.** A Top-15 book can show an edge of about 3%/yr at the exploratory standard, and about 6%/yr at the confirmatory one (Amendment 3).

## 2. Three distinct mechanisms

| | **M1. Net share repurchase** (recommended) | M2. Investor attention (abnormal volume) | M3. Accounting earnings surprise |
|---|---|---|---|
| Economic reason | Managers buy back when they think shares are undervalued and issue when overvalued; the market under-reacts. Supply also shrinks | A volume shock raises a stock's visibility; more investors and more demand lift its price (Merton 1987 investor recognition) | Investors under-react to earnings news, so prices drift after surprises |
| Literature before 2010 | Strong: Ikenberry, Lakonishok & Vermaelen 1995; Loughran & Ritter 1995; Daniel & Titman 2006; Pontiff & Woodgate 2008; **Fama & French 2008: net issues robust in big stocks** | Moderate: Gervais, Kaniel & Mingelgrin 2001; Barber & Odean 2008 (attention buying can reverse) | Strong historically (Bernard & Thomas 1989 / 1990), but Chordia et al. 2009 find it concentrated in illiquid stocks |
| Difference from H001–H030 | New source: corporate finance, share counts. Only overlap is one of six inputs in the composite H029 F7, never return-tested. Shortlisted in P2-CP3, never tested | New source: volume. Not used in any tested score | Same news as H017 (rejected) and the OF-A / OC-2 lines (closed, D251): **effectively a reopening** |
| Data fields | Cover-page shares outstanding per filing, with the as-of date and the filing date; QuantConnect split factors | Daily dollar volume (QuantConnect universe stream) | Quarterly net income, the same quarter a year earlier, filing timing |
| Point-in-time? | Yes: each filing is used only after its filing date; counts are never restated | Yes | Vendor quarterly values are first seen about one day after filing (D187); Q4 values are unmeasured |
| Available now? | **Yes**: already in `rr/ucr_sec_v1.json` in the Object Store | Yes | Only through the vendor stream (SEC Data v3 is packed and refused). Not available for names without a fundamentals object |
| Universe-bias exposure | **Low to moderate:** SEC-based, so it scores repaired names too. Heavy repurchasers rarely fail | Low (prices and volume exist for every name) | **High:** names without fundamentals, the problem population, cannot be scored |
| Turnover / cost at $100K | About 1–1.5× a year; about 0.4%/yr in costs | **About 100% a month; about 5%/yr in costs**, which removes any plausible edge | About 3–4× a year; about 1.5%/yr |
| Alpha vs beta | Corporate-finance signal with no mechanical link to beta; expected beta near 1 | Volume shocks cluster at news and earnings dates (overlap with H017) | Neutral beta |
| Simplest falsification | One Top-15 book vs SPY, equal-weight, random and beta-matched controls | The same | The same |
| **Verdict** | **Recommended** | Rejected at design: cost alone exceeds any plausible edge | Not now: reopens closed lines and is the most exposed to the universe gap |

**Considered and excluded:**
- **Residual momentum:** a momentum repackaging, and momentum failed in H019.
- **Upside beta:** Ang, Chen & Xing (2006) find it is not rewarded; this would be pure beta.
- **R&D intensity:** a growth / sector bet, and hindsight-prone given the 2010s technology rally; weak evidence in large caps.
- **Return seasonality:** high turnover.
- **Index-addition anticipation:** no point-in-time index membership.

**Honest caveat on M1:**
- The buyback effect has historically been strongest in value stocks, and the long leg is weaker than the issuer-avoidance leg (P2-CP3).
- OS-1 may therefore look value-like with an up-capture below 1. In that case it **fails the offensive gates** even with positive alpha, and we learn exactly that.
- Post-publication decay is expected (McLean & Pontiff 2016: about a third on average). A realistic long-only edge is about 0–3%/yr.

## 3. Recommended hypothesis — OS-1 Net Share Repurchase Score

**Statement:**
- US common stocks in the approved ≥ $2B universe that cut their split-adjusted shares outstanding the most over the past twelve months earn higher total returns than SPY after costs.
- This holds in rising markets (upside capture ≥ 1) and is not explained by higher market beta or by the composition of our universe.

**Status:** to be registered as **H032** only on approval (§10). Not registered now.

## 4. Point-in-time data feasibility

| Input | Source | Point-in-time rule | Status |
|---|---|---|---|
| Shares outstanding S | `rr/ucr_sec_v1.json`, `p` records: `[filed, prefix, common_ok, shares, cover_end]`; 113,936 of 126,255 filings carry a single value | Usable only at decisions on a session strictly after `filed`; the count is the company's own, never restated | In the Object Store (SHA-256 ba3ab515…); **needs D270 ratification** |
| Identity | Same rules as UCR-1 (`qr_ucr`): the latest periodic filing is at most 200 days old; its prefix equals the QuantConnect ticker; a unique match; no contested prefix; class tickers and multi-value cover counts excluded; `common_ok` taken from the latest filing | As of the decision day only | Existing code, unchanged |
| Split factor F(d) | QuantConnect universe stream, recorded daily per security from 2009-05-01 (as in X806) | Generated in the run | Existing code (X806) |
| Universe and controls | X806 categories plus the frozen UCR-1 repair; vendor universe in a shadow book | In the run | Existing code; **exploratory use needs approval** (EDP-1) |

**Coverage:**
- Measured in E806-01: uniquely SEC-matched names with a fresh count are about 79–85% of eligible stock-months in 2011–2020 (74% in 2021, 54% in 2010).
- In 2010, companies with $2–5B of float had not yet started XBRL filing, so 12-month changes appear only from about mid-2011. The start date is therefore set **mechanically by the canary** (§5.5), before any return is seen.
- **Unscored names** (recent listings without 12 months of history, multi-class companies, ambiguous identity) cannot be selected. This is disclosed and reported.

## 5. Score and Top-N specification (freeze-ready; no parameter chosen from returns)

### 5.1 Score

At a decision session t, for a security i matched to registrant r:

1. **New count S₁:** r's latest single-value cover count filed before t, at most 200 days earlier; d₁ = its as-of date.
2. **Old count S₀:** among r's single-value counts filed before t, the one whose as-of date d₀ is closest to d₁ − 365 days. Required: |d₀ − (d₁ − 365)| ≤ 45 days; ties go to the earlier filing.
3. **Split adjustment:** S₀ₐ = S₀ × F(d₁) / F(d₀), where F(d) is QuantConnect's cumulative split factor for i at the close of day d. If F is unknown at either date (security not yet observed), the score is missing.
4. **Sanity bound:** if S₁ / S₀ₐ falls outside [2/3, 3/2], the score is missing.
   - This guards against unit errors and split-date mismatches, which produce 2× or ½×.
   - It is fixed as symmetric in log terms (|ln| ≤ 0.405), not tuned. Genuine repurchases above 33% a year are essentially absent.
5. **Net issuance:** NSI = ln(S₁ / S₀ₐ) × 365 / (d₁ − d₀).
6. **Offensive score:** OS = −NSI (more repurchase means a higher score).
7. **Normalisation:** cross-sectional percentile rank among scored, eligible names at t. Average ranks on ties.

### 5.2 Selection and portfolio

| Item | Rule |
|---|---|
| Review | Every month-end session (the session calendar, P7-CP1) |
| Selection | Top N = 15 by OS. **Buffer:** a holding is kept while its rank is ≤ 2N = 30 and it is still eligible and scored. Free slots are filled from the top. Ties: ADV20 descending, then security id |
| Exit | At a review only: rank > 30, ineligible or unscored. Delistings and acquisitions follow the harness rules (D054 / D062) |
| Sizing | New position = equity / 15, capped at 10% of equity; $5,000 minimum; D051 settled-cash funding with the 15% gap reserve; no trimming, top-ups or leverage; idle cash earns nothing |
| Sector | **No sector cap.** No point-in-time sector field exists in the approved data, and adding one would be a new data layer. Concentration is reported as a non-gating diagnostic (vendor current-status sector, labelled not point-in-time) |
| Execution | Decision on information available at the close of t; market orders at the next session's open; $7 per order; 10 bps slippage per side (R1), 20 bps (R2) |
| Capital | $100,000 |
| Learned coefficients | **None.** A single fixed signal; nothing is estimated |

### 5.3 Why this is not a beta bet

- The input is a share count. It has no mechanical link to price volatility or beta.
- **Beta-matched random controls** (§6) and the regression alpha test whether any upside comes from beta.
- The Top 15 are reported with their ex-ante beta, volatility and 12-1 momentum, compared with the universe.

### 5.4 Missing data, corporate actions, identity

- **Missing score** → not selectable (same-universe rule). The equal-weight control uses the same scored set.
- **Stock-financed mergers** raise S, which is genuine issuance and part of the signal; increases of more than 50% fall to the bound.
- **Spin-offs** leave S unchanged.
- **Splits and reverse splits:** adjusted through F.
- **Ticker changes:** irrelevant, because S is per registrant and F is per QuantConnect security.

### 5.5 Window

- **Decisions:** from the first month-end at which at least 70% of eligible names in the repaired universe are scored, as measured by the canary before any return, through 2021-11-30. The run ends 2021-12-31.
- **Subperiods:** A = start → 2015-12; B = 2016-01 → 2021-12. Your fixed split, with A starting at the mechanical start.

## 6. Exploratory evaluation framework (pre-registered)

**Market regimes** (labels for evaluation only; never used in trading):
- **B1 SPY-up months:** SPY total return for the calendar month > 0.
- **B2 bull state:** SPY's trailing 12-month total return at the previous month-end > 0. This is ex-ante.
- **B3 strong-up months:** SPY ≥ +3% in the month.

**Controls:** shadow books in the same run, with the same mechanics, costs and schedule:
- SPY total-return buy-and-hold;
- equal-weight of the scored eligible universe;
- 5 random Top-15 books (seeds fixed at freeze);
- **5 beta-matched random books:** each pick drawn from the same ex-ante 252-day beta quintile as the selected name it replaces;
- a 12-1 momentum Top-15 (known-factor comparison, reported);
- the OS-1 rule run on the **original vendor universe** (EDP-1 E2).

**Gates.** All must pass on R1 unless stated:

| # | Gate |
|---|---|
| O1 | Terminal wealth > SPY after costs, **and** a CAGR excess of at least +1.0 point a year (EDP-1 E4) |
| O2 | g / SE ≥ 1.0 (Amendment 3 W2 statistic) |
| O3 | **Offensive profile:** upside capture in B1 months ≥ 1.00 **and** capture spread (up − down) ≥ +0.05 |
| O4 | Monthly regression on SPY: alpha > 0 with t ≥ 1.0 (Newey-West, lag 2). Beta reported |
| O5 | CAGR above the equal-weight universe, above at least 4 of 5 random books **and** above at least 4 of 5 beta-matched books |
| O6 | Excess over SPY and over equal-weight is positive in **both** subperiods A and B |
| O7 | No calendar two-year block contributes more than 50% of the summed log excess (P4) |
| O8 | O1's wealth condition still holds at 20 bps slippage (R2) |
| O9 | The vendor-universe shadow book also beats SPY and its own equal-weight |

**Reported, not gating:**
- downside capture, maximum drawdown, volatility, Sharpe;
- excess in B2 and B3;
- the comparison and correlation with momentum;
- turnover and costs; coverage; the share of profit from repaired names;
- sector (non-point-in-time); the largest years and months.

**Rough power:**
- With 15 stocks, tracking error is likely about 6–8%/yr over about 10.5 years. O1 and O2 together need a true edge of about 2.5–3%/yr.
- A real +2%/yr edge would pass all gates perhaps one time in three or less.
- With no edge, O2 alone passes about 16% of the time; the full set passes less often, but that rate is not calibrated.
- **A PASS is a reason to pay for independent validation, not evidence.**

## 7. Stopping rules

- **Canary** (§8): any pre-set check fails, or QuantConnect refuses the code → STOP. Plumbing fixes only, documented.
- **One primary specification.** Runs R1 (10 bps) and R2 (20 bps) only, with at most one documented infrastructure retry each. No other N, horizon, bound, buffer or universe.
- **Any gate O1–O9 fails** → OS-1 is closed as NOT PROMISING. The offensive programme returns to you; no second mechanism starts automatically.
- **All gates pass** → "EXPLORATORY PASS — UNIVERSE INCONCLUSIVE (RR6)". STOP. The only next step is a proposal to pay for independent validation (licensed point-in-time data). The Holdout is not requested on exploratory evidence alone.

## 8. Minimum implementation and canary

**Code**, reusing existing modules; plain text; no new data or upload:

| Part | Content | Reuse |
|---|---|---|
| `qr_os1.py` (new, about 150–200 lines) | Old / new count selection, split adjustment, bound, NSI, ranking, Top-N + buffer plan | `qr_ucr.RepairRef` and the identity rules, unchanged |
| Host S033 | Harness trading (D051, costs), X806 categories + UCR-1 repair, daily split-factor record, ex-ante beta from the universe stream, shadow-book controls | `qr_harness`, `qr_ucr`, X806 categorisation, `qr_h026.simulate` or the SYS-1 ledger engine (both plain text) |
| Protocol | EDP-1 + OS-1 specification + evaluation rule, frozen and SHA-256-pinned before any run | Existing pin / config / runner patterns |
| Tests | Point-in-time cut-off (a filing dated t is not used at t), count pairing, splits (2:1, 1:2, reverse), bound, unknown factor, ranking ties, buffer, beta-matched draws | — |

**Canary C-OS1** (one run, aggregates only, **no returns**). Pass conditions fixed at freeze:
1. Point-in-time: 0 filings used with a filing date on or after t.
2. Monthly scored coverage in both universes; this fixes the mechanical start. At least 70% from the start month onward.
3. Bound exclusions ≤ 5% and unknown-split-factor cases ≤ 5% of scored names.
4. Identity: 0 duplicate matches.
5. Beta-matched controls constructible at every review.
6. Determinism: the same digests on recomputation in the run.
7. Shadow-book fidelity on a fixed **non-score** book within a pre-set tolerance.

Also reported: NSI quantiles per year and the yearly turnover of the Top-15 names (names only, no returns).

## 9. Work to the first legitimate backtest

| Step | Work | QuantConnect runs |
|---|---|---|
| 1 | Freeze EDP-1 + OS-1 (register H032); `qr_os1` / host / tests / configs; commit | 0 |
| 2 | Canary C-OS1, offline check, short canary note, STOP | 1 (+≤ 1 retry) |
| 3 | On approval: R1 + R2, offline gate evaluation, checkpoint, STOP | 2 (+≤ 1 retry each) |

**Total:** about 2 working sessions, 3 runs, $0.

## 10. Owner decisions needed

| # | Decision |
|---|---|
| 1 | **Ratify the D270 SEC object** (`rr/ucr_sec_v1.json`; RR7 §5). OS-1's share counts come from it |
| 2 | **Approve exploratory use** under EDP-1 (RR7 §1.3): decision book on the repaired universe, shadow book on the vendor universe, the +1.0 point margin, no Holdout on exploratory evidence |
| 3 | **Approve OS-1** (net share repurchase) as the single offensive hypothesis, registered as H032 at freeze, with §5 as written. This includes no sector cap, the 2N buffer, the [2/3, 3/2] bound and the mechanical start in place of a 2010 start |
| 4 | **Approve** gates O1–O9, the regime definitions and the stopping rules (§6–7) |
| 5 | **Authorise:** (a) steps 1–2 only and STOP after the canary (recommended), or (b) steps 1–3 with R1 / R2 conditional on a canary pass |
| 6 | **Confirm** that H031 stays DRAFT and parked, and that M2 / M3 are not pursued now |

**STOPPED awaiting the owner.**
