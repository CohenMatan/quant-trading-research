# P6-CP2 — H021-A Sector Relative-Momentum Falsification Result

- **Date:** 2026-10-06.
- **Authority:** owner message 2026-10-06 (`docs/owner/2026-10-06_h021a_authorisation.md`, D160).
- **Frozen specification:** `research/phase6/H021A_spec.md` v1, hash-pinned in `qresearch.p6h021`.
- **Decisions:** D160–D164.

## Summary for the owner

**Verdict: H021-A DID NOT QUALIFY.**

**Question:** do sectors with the strongest 6-month total return beat the other sectors over the next month?

**Setup:**
- the nine original Select Sector SPDRs;
- 215 month-ends, 2000–2017;
- the one real test was run once, after the null threshold had been fixed and committed.

**Answer:** no detectable tendency.
- The average monthly rank correlation between past 6-month strength and next-month relative return is **−0.011** (t = −0.35). The required t was 2.66.
- **The top 3 sectors:** +0.16%/yr vs the sector average (+3% required).
- **The middle 3:** +0.80%/yr.
- **The bottom 3:** −0.97%/yr.
- The first half of the period (2000–2008) is slightly positive and the second half (2008–2017) negative.
- **All four gates fail.** The non-gating diagnostics agree: 2010–2017 and 2005–2017 are negative, and the 3- and 6-month responses are near zero.

**Frozen interpretation:** "No sector-relative momentum edge large and robust enough to meet the project's pre-registered statistical and economic requirements was detected. The study has only about 50% power around a +3.3%/yr top-3 edge. A small real edge may therefore remain undetectable."

**Not done:** no tuning, no other lookback, no H021-B, no portfolio. 2018–2021 and the Holdout were untouched, and nothing was purchased.

**Recommendation:** close H021-A as Rejected and close Phase 6 (§40).

---

## 1. Formal H020 closure

**H020** (structured chart score, Phase 5) was **CLOSED as Rejected / No Production Candidate Found** by the owner on 2026-10-06 (D160).

- It is preserved exactly as tested (P5-CP3: all gates G1–G5 failed).
- `research/hypotheses/H020.md` is updated.

## 2. The D035 Phase-6 amendment

D160 amends D035 **for Phase 6 only**:

- 2000-01 → 2017-11 may be used as development data for H021-A;
- this applies only to the nine original Select Sector SPDRs;
- it does **not** reopen 1999–2009 for the stock-level programme.

H021-A used decisions 2000-01-31 → 2017-11-30. Its signal history goes back to 1999-07-30 (the 6-month base of the first decision).

## 3. The exact universe

**XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY**, fixed for the whole experiment.

- XLRE, XLC and every other ETF family were excluded.
- SPY was used only for the NYSE session calendar and for the non-gating diagnostic D5.
- **XLF 2016:** the XLRE distribution of 2016-09-19 (18.80% of the reference price) was treated as a distribution in the total-return accounting (item 4). It changes neither the universe nor the hypothesis.

## 4. ETF data verification

**Source:** QuantConnect daily RAW bars, plus its split and dividend feeds, giving total-return closes and opens (the H019 / D148 construction). Only history from 1998-12-01 → 2017-12-31 was requested.

| Item | Result (E988-01 probe; E989-02 canary) |
|---|---|
| First bar | 1998-12-22 for all nine (SPY 1998-12-01). No backfill |
| Last bar | 2017-12-29 for all ten |
| Missing sessions after the first bar | XLI 1, all others 0. No close used by H021-A needed carrying forward, and every response entered at the first session after the decision |
| Splits | None in any of the ten |
| Distributions | 50 (XLK) to 78 per ETF; one large: XLF 2016-09-19, 18.80% |
| Reference price of the dividend feed | Always the previous raw close (757 / 757, E990-01) |
| **Precision of the dividend feed** | QuantConnect reports every distribution **rounded to the cent** (757 / 757). The amount implied by QuantConnect's exact ADJUSTED series differs by ≤ $0.0049999 for all 757 (E990-02). Effect: ≤ 4.6e-4 on one day's total-return step and ≤ 7.4e-4 on a 6-month signal |

## 5. Canary result

**E989-01** failed on a plumbing KeyError (D161): the dividend feed came back without its columns for a window with no events. This was fixed in plumbing only; no definition, constant or hash changed.

**E989-02** completed. 10 of 12 check groups pass (`research/phase6/H021A_canary_report.json`, `H021A_canary_assessment.md`):

| Check | Result |
|---|---|
| All 9 histories exist | Pass |
| No ETF used before launch | Pass. The earliest row used is 1999-07-30 |
| Monthly calendar | Pass. 215 decisions, 2000-01-31 → 2017-11-30; the last response ends 2017-12-29; no month missing |
| 6-month signals reproduced day by day from RAW prices + events | Pass. Worst error 3.8e-15 |
| 1-, 3- and 6-month and SPY responses reproduced | Pass. Worst error 3.3e-15 |
| Future-price perturbation | Pass. 0 / 20 signal and 0 / 20 response changes |
| Truncation at t (fresh history ending at t) | Pass. 135 comparisons, worst 2.4e-15 |
| Placebo ranks (200 seeded sets) | Pass. 1.0% beyond \|t\| 2.576 |
| Planted ranks | Pass. IC = 1 on every date and Top > Middle > Bottom |
| Null mapping deterministic, fixed-point free | Pass |
| ADJUSTED cross-check (pre-committed tolerance 1e-4) | Fail as specified: max 4.6e-4, on ex-dividend dates only |
| XLF 2016 XLRE distribution | Fail as specified (same tolerance): raw close −18.25%; total-return step +0.678% vs ADJUSTED +0.696% |

**Assessment (D162):** the two failures are the dividend feed's cent rounding (item 4), not an accounting error.

- Distributions are handled correctly, including the XLF / XLRE distribution, and every step is reproduced to 1e-15.
- The 1e-4 tolerance was tighter than the precision of the data source; this follows the D155 precedent.
- The frozen construction was kept, and the same panel was used by the canary, the null and the real run.
- This limitation is disclosed here.

## 6. Null completion count

**5,000 / 5,000 worlds** (seeds 1–5,000) in E022-01 … E022-05, at 1,000 worlds per batch.

- Every batch's signal / response panel digest equals the canary's.
- 4,931 distinct derangements: the seeds are independent draws from the 133,496 derangements of 9, so 69 repeats occur, as frozen in spec §10.

## 7. Null failures, recoveries and retries

- **QuantConnect runs:** 0 failed worlds, 0 failed runs, 0 retries, 0 recoveries.
- **Refused before submission:** four batch starts in a first loop were refused locally before anything reached QuantConnect, because the working tree held E022-01's uncommitted outputs. They were started again after a commit. No world was run twice.

## 8. Frozen c

**c = 2.658089662**: the 50th largest of the 5,000 null t_IC values (α = 1%).

- Null t_IC: mean 0.06, sd 1.11, 99th percentile 2.64, maximum 3.58.
- **Complete P1–P4 procedure under the null:** 10 / 5,000 worlds qualify (0.2%).

## 9. Threshold commit hash

**ea284cb2db2dbec986d6c0f06c255fb3a0fb481c**, which pins C, the null result, the per-world table, the panel digests and the host hash.

The E022-06 config was written in the next commit, a502ccb, and carries exactly these pins.

## 10. Null output hashes

| File / digest | SHA-256 |
|---|---|
| `research/phase6/H021A_null_result.json` | 6db1ed17d4832292bc35ff3046036b773ec702c60d95b12db742b85f1bc7367d |
| `research/phase6/H021A_null_worlds.csv` | c9ec9367da001360ff6f413d43d2e4c2130cd307bca1b30349ec16f8ee656ec9 |
| Signal / response panel digest | 50338b14768ce6cf0c3f2deb5ebac9dc5e409633b25c67fde9500fee0896d251 |
| Diagnostic panel digest | b5465aac8c5f87ac910d57079b02bec23587844ca428c62216969440dea8dc0b |

The QuantConnect backtests are recorded in the null result.

## 11. Spec and code hashes

| File | SHA-256 |
|---|---|
| `research/phase6/H021A_spec.md` v1 | d4a2b8864603965d52e09206d32246d368639eb52b277ee16e57d116fc960141 |
| `src/qresearch/lean/qr_h021.py` | 67820d91e783c24da1850ec03fa72f82d190becca30cba1bd4aa6df2136fc6cf |
| `strategies/X989_h021_sector/main.py` (= S022, byte copy) | 7c3d19f000e4aec93c55f31a1b533ec09045323623c8e749180c03ac436bdcee |

`tests/test_h021_spec.py` checks all of them.

## 12. c was pinned before the real run

The order of events was:

1. Null runs E022-01..05.
2. Threshold commit ea284cb.
3. E022-06 config commit a502ccb.
4. Clean tree verified.
5. E022-06 run **once** from a502ccb (QuantConnect backtest ba75227fda13bf0ee1bd94ccae9bee5f).

The host refuses to compute anything if its panel digests differ from the pinned ones; they matched.

## 13. Exact development dates

| Item | Dates |
|---|---|
| Decisions | Month-ends 2000-01-31 → 2017-11-30 |
| Signal | Trailing 6 months; the first base is 1999-07-30 |
| Responses | From the open of the first session after each decision to the next month-end close; the last ends 2017-12-29 |

## 14. Number of monthly decisions

**215**:

- halves 107 / 108;
- blocks 72 (2000–2005), 72 (2006–2011) and 71 (2012–2017).

## 15. Primary rank IC

The mean monthly Spearman IC is **−0.0108** (standard error 0.0305).

- 50.2% of months have a positive IC.
- By year: 2000 +0.06, 2001 +0.05, 2002 +0.13, 2003 −0.01, 2004 −0.00, 2005 +0.04, 2006 −0.16, 2007 +0.10, 2008 +0.23, 2009 −0.17, 2010 −0.07, 2011 −0.03, 2012 −0.13, 2013 +0.08, 2014 −0.05, 2015 −0.01, 2016 −0.16, 2017 −0.12.

## 16. t_IC

**t_IC = −0.354** (Newey-West lag 0).

## 17. Null percentile and empirical p

- The real t_IC lies at the **36.4th percentile** of the 5,000 null worlds.
- The empirical p is (1 + #{null ≥ real}) / 5,001 = **0.636**.

## 18. Top 3 vs the sector average (annualised)

**+0.16%/yr**, against the +3.0%/yr floor.

## 19. Top 3 vs bottom 3

**+1.13%/yr**. This is descriptive, not a gate.

## 20. Tercile results

All figures are annualised, relative to the 9-sector average:

| Tercile | Return |
|---|---|
| Top 3 | +0.16%/yr |
| Middle 3 | **+0.80%/yr** |
| Bottom 3 | −0.97%/yr |

## 21. Monotonicity

**FAIL.** The middle tercile beats the top tercile.

## 22. First-half and second-half IC

| Half | Decisions | Mean IC |
|---|---|---|
| First | 1–107: 2000-01 → 2008-11 | **+0.049** |
| Second | 108–215: 2008-12 → 2017-11 | **−0.070** |

## 23. Block contributions

| Block | IC sum |
|---|---|
| 2000–2005 | +3.35 |
| 2006–2011 | −1.10 |
| 2012–2017 | −4.57 |
| **Total** | **−2.32** |

The total is ≤ 0, so the shares are undefined and P4 fails by rule.

## 24. Stability

**FAIL.** The second half is negative, and the total IC sum is negative.

## 25. Complete P1–P4 table

| Gate | Requirement | Result | Pass |
|---|---|---|---|
| P1 statistical | t_IC > c = 2.658 | −0.354 | **FAIL** |
| P2 economic | Top 3 ≥ +3.0%/yr vs the 9-sector average | +0.16%/yr | **FAIL** |
| P3 monotonic | Top > Middle > Bottom | +0.16 < +0.80 > −0.97 | **FAIL** |
| P4 stable | Both halves > 0; IC sum > 0; no block > 50% | +0.049 / −0.070; sum −2.32 | **FAIL** |

## 26. Overall verdict

**H021-A DID NOT QUALIFY**

## 27–31. NON-GATING DIAGNOSTICS

These were computed after the primary result. They can neither rescue nor veto it.

| # | NON-GATING DIAGNOSTIC | Decisions | Mean IC | t | Top / Middle / Bottom (annualised vs average) |
|---|---|---|---|---|---|
| 27 | 2010–2017 | 95 | −0.061 | −1.36 | −2.62 / +0.79 / +1.83 %/yr |
| 28 | 2005–2017 | 155 | −0.033 | −0.93 | −1.70 / +1.12 / +0.59 %/yr |
| 29 | 3-month response | 213 | +0.009 | 0.22 | +0.02 / +0.71 / −0.72 %/yr |
| 30 | 6-month response | 210 | +0.033 | 0.71 | −0.11 / +0.60 / −0.49 %/yr |

The 3- and 6-month rows use Newey-West lags 2 and 5.

**31. Sector average vs SPY:** the equal-weight mean of the nine SPDRs' next-month total return minus SPY's, over 215 decisions, is **+1.80%/yr** (t 2.27).

- This describes the equal-weight sector tilt relative to the cap-weighted index over 2000–2017.
- It has nothing to do with momentum. It is not a gate and not evidence for any strategy.

## 32. No tuning

The specification, code and constants are unchanged since freezing (the hashes in item 11).

- There was one plumbing fix to the canary path before any null world (D161).
- No result was used to change anything.

## 33. No alternate lookback

Only the frozen 6-month signal was computed. There was no 3, 9, 12 or 12-1 month version, no weekly version, no price-only version, no blend and no top-2.

## 34. No H021-B

No absolute-trend, cash, T-bill, breadth or indicator filter was built or run.

## 35. No portfolio

There was no top-3 rotation, $100K wealth, SPY wealth, CAGR, turnover, cost or drawdown. Every run was non-trading (0 orders).

## 36. 2018–2021 untouched

Every history request ended on 2017-12-31 (last bar 2017-12-29), and the host enforces this.

## 37. Holdout untouched

2022-01-01 → 2026-08-31 was never requested, and `HOLDOUT_UNLOCK.md` is absent.

## 38. Nothing purchased

The QuantConnect subscription is unchanged ($24/month). No data was bought.

## 39. Interpretation (frozen wording)

"No sector-relative momentum edge large and robust enough to meet the project's pre-registered statistical and economic requirements was detected. The study has only about 50% power around a +3.3%/yr top-3 edge. A small real edge may therefore remain undetectable."

This does **not** say that sector momentum does not exist, or that there is no 1–2.5% sector edge.

## 40. The next owner decision

1. **Close H021-A as Rejected / No Production Candidate Found**, preserved exactly as tested. **Recommended.**
2. **Close Phase 6.**
   - P6-CP1 already judged the realistic post-2000 effect (0–2.5%/yr) to be below what these data can detect.
   - H021-A found +0.16%/yr for the top 3, and a negative IC after 2008.
   - Any further sector variant (another lookback, weekly, top-2, trend or cash filter, another ETF family) would be a post-result rescue, which D160 forbids. **Recommended: no further sector work.**
3. **The next direction for the programme.** Phases 1–6 have found no production candidate, the Holdout has never been opened, and no data has been purchased. The owner may:
   - stop the research programme with "No Production Candidate Found" (defensible);
   - or name a genuinely new direction as a new phase.

   Nothing is started until the owner decides.

---

## Programme totals (registry)

- **Hypotheses:** 19 tested (H001–H021 with experiments).
- **IDs:** 61 strategy / infrastructure IDs, of which 20 are strategies.
- **Runs:** 321 original experiment runs, including 138 research runs.

**H021-A runs:**

| Run | Kind | Outcome |
|---|---|---|
| E989-01 | Canary | Failed, plumbing |
| E989-02 | Canary | Completed |
| E990-01 | Dividend-precision probe (infrastructure) | Inverted formula |
| E990-02 | Dividend-precision probe (infrastructure) | Completed |
| E022-01..05 | Null | Completed |
| E022-06 | The one real evaluation | Completed |

**STOP:** awaiting the owner's explicit decision.
