# H020 canary E987-01 — assessment (before any null or real run)

**Run:** E987-01 (X987, commit 8b8abe9, QuantConnect backtest 37383009 project, 1,999 s).
**Report:** `research/phase5/H020_canary_report.json` (`python research/phase5/H020_eval.py canary`).
**Result: 12 / 14 checks pass.** Every chart, universe, timing, history, coverage, point-in-time recomputation and return-accounting check passes. The two failures concern a non-gating diagnostic's data coverage and a mis-specified check criterion. **Neither is a fidelity defect of the H020 pipeline**, so nothing in the implementation was changed and H020 proceeds to the null.

## Passing checks (key numbers)
- **Calendar:** ends 2017-12-29, with no row after it.
- **Universe:** all 417 research week-ends have their recorded point-in-time universe.
- **Decisions:** 412 primary decisions, 2010-01-08 → 2017-11-24. The last 4-week window ends 2017-12-22; the 13-week diagnostic has 403 decisions, the last window ending 2017-12-26.
- **Scores:**
  - 1,972 stocks; 441,233 eligible stock-weeks.
  - 420,639 scored (none failed): 20,517 excluded for < 504 bars, 77 with no bar at t.
  - 87 had no response and 3 had no momentum.
  - The minimum history of a scored stock is exactly 504 bars.
- **Independent point-in-time recomputation:** 120 sampled stock-weeks were recomputed from a fresh history request ending at t, with split events up to t only. Conditions, disqualifiers, score and states are identical in 120 / 120 cases; ratios differ by at most 8.9e-14; digests are identical.
- **Total shareholder return:** 238 sampled responses were recomputed independently from RAW prices and the split / dividend event lists. The maximum difference is 6.7e-16, with 0 NaN mismatches; the sample included 88 dividend windows, 1 split and 2 delistings.
- **Dividends in the response (panel-wide):** 86,571 of 420,549 four-week windows contain an ex-date. TSR ≥ price return in **all** of them (mean +0.76%). 1,153 windows end in a delisting and are valued at the last real close.
- **Placebo chart side:** t_ic −0.94, t_inc −1.16.
- **Null worlds:** deterministic; the chart-panel digest reproduces.
- **Runtime:** wall 1,959 s; score table 1,630 s; null world 0.46 s; max RSS 3.3 GB.

## Failure 1 — point-in-time industry coverage in 2010 (68.7% < 70%)
- **Coverage by year** (evaluation observations with a dated SEC SIC):

  | Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
  |---|---|---|---|---|---|---|---|---|
  | Coverage | 68.7% | 94.2% | 95.7% | 96.5% | 97.7% | 97.7% | 97.9% | 98.0% |

- **Cause:** the dated SIC starts at each company's first filing in the frozen data-v1 table, so early 2010 is less covered. That is correct point-in-time behaviour, not an error. No present-day label is substituted.
- **Consequence:**
  - The point-in-time industry data is reliable from 2011.
  - In 2010 about 31% of observations fall in the pre-registered 'Unclassified' group (addendum A2).
  - The NON-GATING SECTOR DIAGNOSTIC stays as pre-registered and is reported with this coverage disclosed. The limitation is acknowledged.
  - The diagnostic never gates, so H020 is not blocked (owner item 3).

## Failure 2 — planted-signal null criterion mis-specified
- **What was checked:** the planted score is Q := the rank of each stock's own 4-week response. It is **recovered perfectly**: IC = 1.000 at every one of the 412 decisions. Its t is degenerate (zero variance), so it is not reported.
- **What failed:** the check also required |t_ic| < 4 in **one** tethered null world. The world gave 4.47.
- **Synthetic evidence that this is expected** (`research/phase5/h020_planted_factor_check.py`, 800 stocks × 412 weeks, 40 null worlds):

  | Return model | Planted null t_ic sd | max \|t\| |
  |---|---|---|
  | No common return factors | 0.98 | 2.2 |
  | Three common factors | **4.8** | 10.2 |

- **Why:** with common factors, a fixed tethered pair's planted scores co-move through their factor exposures, so a single null world is far wider than N(0, 1).
- **Conclusion:** the |t| < 4 criterion assumed a standard normal null and was mis-specified for real returns. The 5,000-world empirical null exists to capture exactly this width on the real panel. Nothing in the null, the gates or the code changes.

## Decision
These are not fidelity defects (owner item 7). Proceed to E021-01..05 (5,000 null worlds) with the frozen code (S021 = byte copy of X987).
