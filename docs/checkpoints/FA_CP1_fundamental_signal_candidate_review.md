# FA-CP1: One untested fundamental signal? Candidate review

**Date:** 2026-10-24 · **Owner direction:** D306 (`docs/owner/2026-10-24_close_h006x_refocus_fundamental_alpha.md`) · **Record:** D307
**Type:** design and review only. Nothing was run, computed on returns, built or bought. The Holdout and 1999–2009 were not touched.
**H006X:** closed as NOT MEANINGFUL (owner, D306).

## Answer

**No candidate survives.** No economically credible, previously untested, stock-level fundamental signal can be evaluated responsibly with our existing point-in-time SEC data. Each candidate fails for at least one of three reasons:
- it was already tested and rejected;
- it is a close variant of a closed line;
- it cannot be tested with a validated inference method and adequate power on the exposed 2010–2021 data.

The binding limits are generic (§3), not specific to any one signal.

**Recommendation:**
- Stop further historical stock-selection research on 2010–2021 until genuinely independent evidence can be obtained (§5).
- SPY remains the offensive baseline.
- No freeze-ready specification is produced, because the owner asked for one only if a credible and feasible candidate exists.

## 1. What has already been tested (fundamental and information mechanisms)

| Mechanism | Where | Result | Kind of failure |
|---|---|---|---|
| Profitability / quality levels (GP/A, cash conversion, equity / assets, B/M, accruals, asset growth, CFP, CBOP) | H016, H022, H023, H024 | H016 Sharpe 0.69 vs EW 0.85; H022 t_IC 0.48; H024 best single feature t 1.24 | **Economic:** valid tests, no effect |
| Learned combinations of those features | H026–H028 | Rejected; nulls structurally suspect (D238) | Economic and method |
| Earnings reaction (price-based post-earnings drift) | H017 | Beat SPY (CAGR 17.5% vs 14.9%), but evidence g/SE 0.71 and 74% of the excess in 2014–15 | **Not robust**; restart forbidden (D128) |
| Insider cluster buying (Form 4) | H025 | t −0.93 | Economic |
| Net share repurchase (SEC cover shares) | H032 | 11.84% vs SPY 16.31%; beta 1.17 | Economic |
| Business improvement composite (F1–F8) + H028 blend | H029 / H030 | Never return-evaluated | **Method:** both nulls inadequate, the third infeasible (D232–D237) |
| Profitability improvement ΔROA (F5), single signal | OC-2 | Stage 1 data PASS; calibration **C — NOT VALIDATED** (D250) | **Method:** the inference rule over-approves under a latent priced factor |
| Accounting earnings / revenue surprise (OF-A C1–C6) | LH-CP1–CP4 | Never return-evaluated | **Data:** the fiscal-label chain limits use to 2015–2021 (D245). **Power:** about 10–46% at +3% a year (LH-CP4) |

## 2. Remaining candidates screened

| Candidate | Distinct from tested work? | Point-in-time data on existing layers | Verdict |
|---|---|---|---|
| **SUE-NI** (seasonal earnings surprise, OF-A C1) | Accounting form of post-earnings drift; H017 tested the price form of the same mechanism | Needs 8–13 fiscally labelled quarters, so only 2015-01 → 2021-11 (83 reviews) under D245 | **Fails.** Low prior: the drift has been absent in large stocks since 2006 (Martineau 2022). Power 10–46% at +3% a year. The inference blocker (§3) applies. |
| **SUE-REV** (revenue surprise, Jegadeesh & Livnat, C2) | Overlaps H029 F1 (revenue acceleration) and the H022 revenue-growth layer | Same 2015–2021 limit | **Fails** for the same reasons; partly a duplicate. |
| Price-scaled or TTM earnings change (C3), gross-profit surprise (C5) | Essentially ΔNI or ΔGP scaled; near-duplicates of F5 / F2 | No labels needed, 2012–2021 | **Duplicate** of the closed OC-2 / H029 line (OC-CP2 item 18). |
| Other single business-improvement signals (F1, F2, F4, F8) | Same family as OC-2 | Data v3, 2012–2021 | **Closed:** OC-CP2 item 18 closes the family on existing data once OC-2 fails. The same method blocker applies. |
| R&D / intangible-investment intensity (Chan, Lakonishok & Sougiannis 2001; Eberhart et al. 2004) | Genuinely untested here | **Not on existing layers.** It needs a new SEC field object and host (an infrastructure build). Zero vs missing is ambiguous for non-reporters. | **Not feasible as instructed.** Also not credible on this window: R&D intensity in 2010–2021 is largely the technology / healthcare tilt whose outcome we already know (CLAUDE.md hindsight rule). After sector controls, little stock-specific variation remains. |
| Earnings-announcement premium | Distinct, calendar-based | Event Data v1 | **Not offensive:** turnover-heavy, small-stock effect in the literature (OC-CP2 §5). |
| Dividend initiations / increases | Distinct | QuantConnect dividend feed | **Not offensive:** mature-firm or defensive tilt; sparse among ≥ $2B names. |
| Analyst revisions, guidance, text, customer–supplier links | Distinct | No data (paid, or news, which is excluded), or a new infrastructure build | **Not feasible.** |

## 3. The generic blockers (they bind any new signal)

1. **Inference is not validated.**
   - The only non-permutation design available is universe-wide Fama–MacBeth with stock-level controls for momentum, quality, size, sector and beta.
   - It failed its frozen calibration (OC-CP5). A priced latent characteristic, correlated 0.30 with the signal and absent from the controls, creates about +0.23% a year of false signal effect per +1% of latent premium. False approval reached 4.40% (limit 2%) in the severe high-noise world.
   - This is an identification limit of the data, not a fixable defect (OC-CP5a §9).
   - Identity-tether and permutation nulls are structurally suspect (D235, D238, D239).
   - So "beyond momentum, quality, size, sector and beta" cannot currently be established to the standard the programme set.
2. **Power is too low for plausible effects.**
   - **Signal level:** 118 monthly reviews (2012–2021) give an 80% minimum detectable effect of about +4.3% a year top-quintile (OC-CP2 §9). The 83 reviews of 2015–2021 give about +5.2% a year.
   - **Portfolio level against SPY:** with tracking error σ over T years, the 80% minimum detectable excess at one-sided 1% is about 3.17·σ/√T, as below.

     | Tracking error σ | 10 years | 12 years |
     |---|---|---|
     | 6% | 6.0% a year | 5.5% a year |
     | 8% | 8.0% a year | 7.3% a year |
     | 10% | 10.0% a year | 9.1% a year |

   - **What is plausible:** after publication decay (McLean & Pontiff 2016, about −58%) and in ≥ $2B stocks, a credible single-signal edge is about 0–3% a year.
   - A test that can only detect effects two to three times larger than plausible is not informative.
3. **The data are exposed.**
   - 2010–2021 has carried 30+ hypotheses; any result there is exploratory.
   - There is no independent window on QuantConnect: the 1999–2009 universe audit FAILED (RR3).
   - The Holdout is reserved for at most one candidate (D267), and none qualifies.
4. **The universe is limited.** The vendor ≥ $2B universe misses 3.5–6.1% a year of names in 2010–2015 (RR5). The repaired universe is INCONCLUSIVE (RR6, hard stop).

**Earnings / business-performance surprise or acceleration:**
- **Not novel.** H017 tested the price form; OC-2 / H029 tested the change and acceleration forms.
- **Not feasible as a validated test.** Blockers 1 and 2 apply, and the labelled-quarter forms are confined to 2015–2021.
- **Not a strong prior in large caps after 2006.**

## 4. Requirements checklist (D306)

| Requirement | Status |
|---|---|
| One primary signal, clear rationale independent of our winners | Possible on paper (SUE-NI), but its prior is low for this universe and era |
| Exact point-in-time availability and coverage | Known: SUE-NI 2015–2021 only under D245; F-signals 2012–2021 |
| Fixed, falsifiable signal-level test with an adequate inference method | **Not met:** the method is NOT VALIDATED (blocker 1) |
| Beyond momentum, quality, size, sector and beta | **Not establishable:** latent-factor identification (blocker 1) |
| Offensive evaluation (SPY-up periods, beta-adjusted excess, terminal wealth after costs) | Would be descriptive only; power too low (blocker 2) |
| No assumed learned score or Top-15 portfolio | Respected; no construction proposed |

## 5. Recommendation: stop until independent evidence exists

**Stop further historical stock-selection research on 2010–2021.** SPY remains the offensive baseline.

Genuinely independent evidence could come only from the following. Each needs a separate owner decision; none is proposed for execution here:

| Source | What it needs |
|---|---|
| (a) Licensed point-in-time data with pre-2010 history and a local engine (RR1 Option 3, deferred) | A data purchase (D123 / D124) |
| (b) A true forward record of one literature-defined signal, pre-registered and frozen before any forward data | No purchase. Evidence accrues slowly: several years before the power in §3 is reached |
| (c) Additional unseen history from another verifiable free source | None identified; WIKI is INSUFFICIENT (TT-CP1c) |

If the owner wants a stock-selection line to continue, (a) is the only route that could produce independent evidence on a useful horizon.

**STOPPED for owner review.**
