# Owner message 2026-10-11: "Phase 7 — H022 / Data v2 Real Evaluation. Exactly One Real Evaluation — E024-07. Frozen Data, Frozen Score, Frozen Gates, Pinned c_IC"

Recorded summary (the full message is in the session transcript). Decision id: **D197**. Recorded and committed BEFORE E024-07 is launched.

**Approved:** exactly ONE real H022 evaluation on frozen Data Infrastructure v2, run **E024-07**. It is the first and only unpermuted H022 evaluation authorised so far.

**Frozen provenance:**

| Item | Value |
|---|---|
| Data v2 manifest | `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb` |
| H022 panel digest | `09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0` |
| Data-v2 c_IC | `2.3798883324991866` (from the 5,000 Data-v2 null worlds, pinned before any real result) |

The old 2.390976216956 stays DATA_V1_ONLY / UNUSED_ON_V2 and is never used.

**No changes before the run:**
- the data: Data v2, reference data, market-cap repair, M2, identity, restatement guard and universe;
- the score: Score v1 and H1–H7;
- the test: review dates, response, horizon, threshold, Newey-West lag, G1–G4, diagnostics, significance, economic floor, monotonicity and stability rules.

**Pre-run integrity gate:** the run is launched only if all of these hold:
- the manifest, Score v1, spec and `qr_p7_pred` hashes match;
- the pinned c_IC and panel digest match;
- there are 83 decision dates;
- there are no PIT, timing or post-2017 violations;
- the working tree is clean and this approval is committed.

The actual LEAN build is recorded. A different panel on the current build is a STOP; nothing is rebuilt or recalibrated.

**One real mapping only:**
- each stock's own frozen Score v1 ↔ its own subsequent response;
- no alternate mapping, score, threshold, horizon, universe or post-hoc subset.

**Population and response:**
- population: eligible, fully scorable, kept class, no H1–H7 disqualifier;
- decisions: 2011-01-31 → 2017-11-30, 83 monthly;
- response: next-session open after t → next review close, stock total shareholder return minus the equal-weight mean of the population over the same window (not SPY). Corporate actions as frozen.

**Statistic and gates:**
- monthly Spearman IC; t_IC = mean / Newey-West SE, lag 2;
- G1: t_IC > 2.3798883324991866 and mean IC > 0 (full precision, no rounding);
- G2: 80+ annualised demeaned return ≥ +3.0%;
- G3: quintile monotonicity Spearman ≥ 0.90 and Q5 > Q1;
- G4: both halves positive, and no calendar block (2011–12, 2013–14, 2015–16, 2017) above 50% of summed IC.

**QUALIFIED only if all four pass;** otherwise NOT QUALIFIED. No "almost passed" language as a reason to continue.

**Non-gating diagnostics** (pre-registered only), computed after the gates:
- sector-demeaned IC;
- regime IC;
- Fama-MacBeth with 12-1 momentum and log PIT market cap;
- 2- and 3-month horizons;
- IC by year and population by year.

None of them can override G1–G4.

**Not allowed:**
- a portfolio, wealth, CAGR, Sharpe, drawdown or SPY comparison;
- 2018–2021 or the Holdout;
- a rerun because the result is inconvenient, or removing observations;
- tuning on a failure.

An infrastructure failure before any real statistic is visible means STOP, document and ask; if any statistic became visible, record exactly what and ask.

**Checkpoint:** "P7-CP7 — H022 Data v2 Real Evaluation" (59 items). Conclusion is exactly one of:
- "QUALIFIED — H022 passes G1–G4 on Data v2";
- "NOT QUALIFIED — H022 fails one or more frozen gates";
- "BLOCKED — real H022 evaluation invalid / incomplete".

Then STOP.
