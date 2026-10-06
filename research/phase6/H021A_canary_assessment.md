# H021-A canary assessment (E989-01, E989-02, E990-01, E990-02; D161, D162)

## Runs

| Run | What | Result |
|---|---|---|
| E989-01 | Canary | FAILED. A plumbing KeyError: the dividend feed for a short window without events came back without its columns. Fixed in plumbing only (D161) |
| E989-02 | Canary | Completed. 10 of 12 check groups pass. The two failures share one cause (below) |
| E990-01 | Dividend-precision probe | The implied-amount ratio was inverted, so the implied columns are void. Valid findings: feed amounts are 100% whole cents, and the reference price is always the previous raw close |
| E990-02 | Probe re-run (formula fixed) | Every one of the 757 distributions is explained within half a cent (below) |

## E989-02 checks

| Check | Result |
|---|---|
| All 9 histories present | Pass. First bar 1998-12-22 for all nine (SPY 1998-12-01), last bar 2017-12-29. Missing sessions: XLI 1, others 0. No used close needed carrying forward; every entry was the next session |
| No use before launch | Pass. The earliest row used is 1999-07-30 |
| Calendar | Pass. 215 decisions, 2000-01-31 → 2017-11-30; the last response ends 2017-12-29; every decision is a month-end; no month is missing |
| Independent day-by-day recomputation | Pass. Worst errors: signal 3.8e-15, 1-month 2.0e-15, 3-month 2.4e-15, 6-month 3.3e-15, SPY 1.3e-15 |
| Future-price perturbation | Pass. 0 / 20 signal changes and 0 / 20 response changes |
| Truncation (fresh history ending at t) | Pass. 135 comparisons over 15 decisions, worst 2.4e-15; 0 bars after t returned |
| Placebo (200 seeded random signal sets) | Pass. First t −0.33; mean t 0.04, sd 1.09; share with \|t\| > 2.576 = 1.0%; max \|t\| 3.64 |
| Planted (S := Y) | Pass. IC = 1 on every date and Top > Middle > Bottom; a weak planted signal gives t 11.2 |
| Null determinism | Pass. Fixed-point free and repeatable; 0.0045 s per world |
| Panel repeat | Pass. Identical digest |
| **ADJUSTED cross-check (tolerance 1e-4 per step)** | **FAIL as specified.** Max step deviation: SPY 4.6e-5; sector ETFs 1.7e-4 → 2.6e-4; XLF 4.6e-4 (2009-03-20). All maxima fall on quarterly ex-dividend dates. Max 6-month signal difference vs ADJUSTED: 7.4e-4 |
| **XLF 2016-09-19 (XLRE distribution)** | **FAIL as specified,** only through the same 1e-4 tolerance. Distribution 18.80% of the reference; raw close −18.25%; total-return step +0.678% vs ADJUSTED +0.696%; difference 1.9e-4 |

## Cause, verified by E990-02

QuantConnect's dividend feed reports each distribution **rounded to the cent**. ADJUSTED uses the exact factor file. For all 757 distributions (9 SPDRs + SPY, 1998–2017):

- the amount implied by ADJUSTED differs from the feed amount by **at most $0.0049999**, i.e. always within half a cent;
- the median difference is $0.001–0.002;
- the largest relative difference is 4.6e-4 of the price (XLF, at its 2009 low price).

## Assessment

- **Not a fidelity defect.** Distributions, including the XLF / XLRE distribution, are handled correctly. Their dates, reference prices and sign are right, and every total-return step is reproduced independently to 1e-15. The residual is the documented precision of the data source (±$0.005 per distribution).
- **The canary's 1e-4 tolerance was mis-specified.** It was tighter than that precision. This is the D155 precedent.
- **Impact on H021-A is negligible:**
  - signal differences are at most 7.4e-4, against a typical cross-sectional dispersion of 6-month sector returns of several percent;
  - a rank changes only when two sectors are within that distance;
  - the same panel is used by the canary, the null and the real run, so any such noise is inside the calibrated null as well.
- **Decision (D162):**
  - the frozen construction is kept unchanged: spec §4, `qr_h021` and the hashes;
  - the canary is not re-run;
  - the null proceeds;
  - P6-CP2 discloses the precision limit.
