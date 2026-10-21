# OS-CP2 — H032 canary C-OS1 (E807-02): PASS

- **Decision trail:**
  - D278: owner approves the revised OS-1, then freeze + canary only.
  - D279: implementation and freeze.
  - D280: E807-01 failed at start-up; one retry.
  - D281: this result.
- **Frozen before the run:** spec `research/os/H032_spec.md`, pinned in `qresearch.os1` (commit f05a1de; host pin updated in 8623b4f for the D280 fix only).
- **What this is:** a data and mechanics check. **No strategy return was computed.**
  - **Not done:** no R1 / R2, no Holdout access, no purchase.
  - **Standing status:** H031 is parked; RR6 stays INCONCLUSIVE; anything H032 produces is EXPLORATORY.

## 1. Result in one paragraph

The canary **passed all ten frozen gates**:
- **Point in time:** no SEC row was used on or after its decision day.
- **Identity:** no duplicate matches; every restored security had a point-in-time identity.
- **Filter inputs:** the same-filing revenue comparative and the annual operating cash flow are available for 81–91% of the H032 universe every year.
- **Share counts and splits:** they behave as specified.
- **Coverage gates:**
  - Joint coverage first reaches 70% in **July 2012** (the mechanical start).
  - It then stays at or above 66.8%.
  - Leavers and restored names are not under-covered.
- **Books:** every book can be filled at every review and reproduces exactly when recomputed.
- **Subperiods:** A (2012-07 → 2015-12) has 42 reviews, above the 36 minimum; B (2016-01 → 2021-11) has 71.

**Two margins are thin and should be read with care:**
- split-adjusted share pairs inside the sanity bound are 90.05% against a 90% minimum;
- the lowest coverage after the start is 66.8% against a 65% minimum, in 2021.

## 2. Runs

| Run | Outcome | Detail |
|---|---|---|
| E807-01 | **Failed at start-up** (16 s, first simulated day, nothing measured) | Host defect: the price matrix was enlarged inside the indexing expression, so the write hit the old 4,096-row array. Fixed in one line, with a regression test that reproduces the failure (D280) |
| E807-02 | **Completed**, the one permitted retry | QuantConnect default build LEAN 18200; backtest `fae482142b5e…`; 272 s; 0 orders; 143 month-end reviews 2010-01 → 2021-11 |

- The SEC extension object `rr/os1_sec_v1.json` (SHA-256 `32bb0a66…`) was uploaded once, at 14:28:59 UTC, 36 minutes before E807-01.
- The original UCR-1 object is unchanged. The host checked both digests in the run.

## 3. Gates (frozen rule `research/os/OS1_eval.py`)

| Gate | Requirement | Result | |
|---|---|---|---|
| C1 point in time | 0 SEC rows used on or after the review day | 0 / 0 / 0 | PASS |
| C2 identity | 0 duplicate matches; 0 restored without identity | 0; 0 of 8,191 repaired stock-months | PASS |
| C3 same-filing annual inputs | every year ≥ 70% (F-OCF and F-REV inputs) | OCF 81–91%; revenue growth 82–86% (2012–2021) | PASS |
| C4 share counts and splits | unknown factor ≤ 5%; bound exclusions ≤ 5%; split-adjusted in bound ≥ 90% (≥ 20 pairs) | 0.14%; 1.41%; **90.05%** (1,719 of 1,909) | PASS (thin) |
| C5 G-COV1 | start at first ≥ 70%; then ≥ 65% | start **2012-07-31**; minimum **66.8%** | PASS (thin) |
| C6 G-COV2 | stayers − leavers ≤ 10 points (assessable reviews) | leavers 72.9% vs stayers 74.1%: gap +1.2 points; 23 reviews 2020-01 → 2021-11 **CENSORED** | PASS |
| C7 G-COV3 | vendor − restored ≤ 10 points | restored 83.1% vs vendor 72.9%: −10.2 points (restored better covered) | PASS |
| C8 book feasibility | full books ≥ 99%; beta controls ≥ 95% | every book 15 names at 100% of reviews; beta controls 1,234 of 1,234 | PASS |
| C9 determinism | in-run recomputation = online digests | 19 of 19 books identical | PASS |
| C10 subperiod A | ≥ 36 reviews | 42 (B: 71) | PASS |

## 4. What the canary shows (reported, never gating)

**Coverage by year.** All figures are % of the H032 universe (eligible, not known to be financial):

| Year | Eligible names | Financials removed | No SEC identity | Joint coverage | Coverage among known non-financials | Passing both filters | Restored coverage |
|---|---|---|---|---|---|---|---|
| 2011 | 944 | 17.6% | 8.8% | 46.7% | 52.3% | 38.4% | 48.2% |
| 2012 | 956 | 18.1% | 6.8% | 70.4% | 76.8% | 63.5% | 76.6% |
| 2013 | 1,105 | 18.2% | 6.5% | 73.9% | 80.2% | 56.7% | 82.9% |
| 2015 | 1,251 | 20.7% | 6.0% | 74.7% | 80.9% | 59.8% | 86.3% |
| 2016 | 1,210 | 21.5% | 5.8% | 74.9% | 80.8% | 44.4% | 86.0% |
| 2018 | 1,359 | 21.2% | 7.2% | 73.2% | 80.6% | 60.9% | 72.6% |
| 2020 | 1,333 | 19.3% | 8.8% | 74.2% | 83.3% | 51.1% | 96.6% |
| 2021 | 1,675 | 18.2% | 14.8% | 68.5% | 83.6% | 34.0% | 91.0% |

- **Financials removed:** 18–22% of otherwise-eligible names. Every removed name is FF12 "Money".
- **The coverage gap is mostly identity, not the filters.**
  - Securities without a point-in-time SEC match count as not covered. Among names whose SIC is known, coverage is 80–84%.
  - 2021 has the most unmatched names (14.8%; the eligible count also jumps to 1,675). That year is the source of the 66.8% minimum (2021-11-30; 2021-08 to 2021-11 all near 67%).
- **The filters bite hardest after weak years.**
  - Only 44% of the universe passes in 2016 (energy and commodities after the 2015 slump).
  - Only 34% passes in 2021 (fiscal-2020 revenue declines).
  - Both effects were disclosed in OS-CP1 §11.5 before any result.
- **Later-disappearing names** (leave the stream within 24 months) are covered almost as well as survivors: 72.9% vs 74.1%. Restored names are covered better than vendor names.
- **Sector tilt**, 2013–2021, share of name-months:

  | Group | Universe | Passing pool | B1 holdings |
  |---|---|---|---|
  | Shops | 10.9% | 14.2% | **23.9%** |
  | BusEq | 18.4% | 22.2% | 19.5% |
  | "Other" SIC groups | 15.1% | 18.2% | 20.7% |
  | Health | 10.6% | 10.7% | **4.2%** |

  - B1 concentrates in retailers and services, which are classic repurchasers.
  - Health care is under-represented because of its issuance.
  - None of these are point-in-time sector caps; they are reported only.
- **Signal spread:** the median net share change is about 0 (OS −0.4% to +0.8% a year). The top decile reduces shares by about 3–6% a year.
- **B1 turnover** (2013–2021): about 18–30 new names a year, 33–42 distinct holdings a year.

## 5. What this does and does not mean

- **It means:**
  - the approved definitions are available point in time, with adequate coverage, on the actual repaired universe;
  - the coverage gates, the start date and the subperiods are fixed mechanically and before any return;
  - every control book is constructible and deterministic.
- **It does not mean:**
  - anything about performance;
  - that the residual RR6 universe uncertainty is resolved.
- **Not yet tested:** the shadow-book fidelity pre-gate (spec §9) needs the trading host and belongs to R1.

## 6. Owner decision needed

The frozen evaluation (spec §9) is the next step and **needs your approval**:
- **R1:** 10 bps slippage.
- **R2:** 20 bps.
- **Each run:** at most one infrastructure retry.
- **Window:** 2012-07 → 2021-11.
- **Comparisons:** SPY, equal weight, random, B2, beta-matched, momentum, B0 (reported) and vendor-universe controls.
- **Gates:** O1–O9; any failure → NOT PROMISING; all pass → EXPLORATORY PASS — UNIVERSE INCONCLUSIVE.
- **Work required:** the trading host (B1 in LEAN plus shadow controls with the same mechanics) has to be built first. That is about one session plus 2 runs, at $0.

| Option | Meaning |
|---|---|
| A (recommended) | Authorise building the R1 / R2 host exactly to spec §9, then R1 + R2 once each, then STOP |
| B | Stop here: H032 stays frozen and unevaluated |

**STOPPED awaiting the owner.**
