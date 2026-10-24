# TT-CP2: Restricted WIKI sample and AI-assisted chart discovery

**Date:** 2026-10-24 · **Owner decision:** D302 (`docs/owner/2026-10-24_restricted_wiki_sampling_ai_pattern_discovery.md`) · **Record:** D303
**Code and records:** `research/tt/chart_discovery/`.
- `sample.py`: rules committed before the draw.
- `render.py`.
- `OBSERVATION_protocol.md`: committed before any chart was viewed.
- `PILOT_note.md`.
- `observations.jsonl`: one line per chart, 299 lines.
- Tests: `tests/test_chart_discovery.py`.

Raw prices, images and the chart id → company / date mapping stay local under `data/` and are git-ignored.

## Result in one line

I viewed and recorded **299 blinded charts**. The behaviours that recur are real but **not new**:
- what reads visually as a "strong stock" is, in two-thirds of cases, simply the top tercile of trailing 12-month return;
- the other recurring structures map onto hypotheses already tested and rejected (H002, H003, H004, H010, H014, H017, H018, H019, H020).

**The observations do not support a credible new hypothesis, and I do not recommend one.**

## 1. Charts sampled and analysed

| | Count |
|---|---|
| SEC frame registrant-months, 2011–2016 | 59,569 |
| Eligible candidates | 43,690 (1,049 registrants) |
| Charts drawn (target 300) | **299** |
| Charts viewed and recorded | **299**: pilot C001–C024, then C025–C299 in id order, none skipped |
| "No clear pattern" (`clarity = NONE`) | 21 |
| Weak or ambiguous structure | 152 |
| Clear structure | 126 |

**Pre-checks**
- **Dataset:** SHA-256 matched the manifest (`ca7fb174…`), so nothing was re-acquired.
- **Terms:** the published-terms check found no explicit applicable prohibition (`TERMS_CHECK.md`).
- **Leakage in code:** every chart's last bar equals its decision date. A synthetic test also shows that bars after the decision date never change a single byte of the image.

**Exclusions** (registrant-months)
- Identity: 8,248 AMBIGUOUS, 4,314 UNRESOLVED, 282 MISSING.
- Adjustment-defect tickers: 863.
- Window defects (split, spike, invalid OHLC, dividend-factor mismatch): 2,019.
- Fewer than 252 bars: 153.

**Adjustment defects.** The sampler excluded 58 tickers with any unexplained adjustment change in 2010–2017. That is a superset of the audit's 21: the audit counted only matched tickers, while the sampler applies the same frozen definition to every ticker.

## 2. Coverage and limitations

- **Spread:** proportional to the SEC frame by year (2011: 23 … 2016: 66), size tercile (99 / 101 / 99) and trailing-return tercile (95 / 105 / 99).
- **Exit groups:** CONTINUING 279, ACQUIRED 20 (target 21).
  - **One cell is unfilled:** 2011 / smallest size / acquired, with 0 candidates.
  - **Failed and delisted companies got a target of 0.** Together with the stopped-filing-only group they are 200 of 59,569 frame registrant-months (0.34%), so the proportional allocation rounds them to zero. Only 12 eligible failed-company months existed.
  - **The sample therefore contains no failed company.** It is **not representative of failures** and must not be called statistically representative. Acquisitions were never used as a substitute.
- **Survivorship:** WIKI remains unproven as survivorship-free (frozen audit INSUFFICIENT; owner exception D302).
- **Regime confound:**
  - Many charts share the same synchronous market shocks: deep V-shaped crashes, and a cluster of one-day extreme low wicks (C151, C170, C196, C198, C200, C216) consistent with a market-wide opening dislocation or bad prints.
  - Absolute charts mix market behaviour with stock-specific behaviour. 2015 decision dates hold 20 of the 50 breakdown / downtrend charts.
- **Event confound:** 62% of charts contain visible single-day gaps. Most visible structure is created by a few information days, typically earnings. Some gap-then-flat patterns look like pending acquisitions (C112, C177, C079).
- **Analyst limits:** one analyst, one pass, coarse visual categories. The tags are subjective and were not double-coded.

## 3. Most recurring behaviours

Counts come from the recorded tags. How each pattern emerged is noted.

| # | Behaviour | Charts | First noticed |
|---|---|---|---|
| B1 | **Persistent staircase leader**: year-long uptrend, at the year high, above rising MA50 and MA200 | 72 (46 of them with stable or contracting volatility) | C003, pilot |
| B2 | **Pullback / consolidation inside an uptrend** near the rising MA50 | 57 (`PULLBACK_IN_UPTREND` 40 + `TIGHT_RANGE_NEAR_HIGH` 17) | C010, pilot |
| B3 | **Large up gap on heavy volume that holds** for weeks | 15 tagged `GAP_AND_HOLD`; 133 charts show up gaps | C006, pilot |
| B4 | **V recovery after a capitulation low**, often market-wide | 80 `V_UP` year shapes | C001, pilot |
| B5 | **Top, then a break below MA200** with a rolling-over MA50 | 50 `BREAKDOWN` / `DOWNTREND` | C019 |

**Descriptive check (after viewing, strata only, no returns).**
- **B1:** 48 of the 72 charts (67%) fall in the top trailing-12-month-return tercile; 4 fall in the bottom tercile.
- **B5:** 32 of the 50 charts (64%) fall in the bottom tercile.

The eye is mostly re-discovering past return.

**B3 and acquisitions.** 4 of the 15 gap-and-hold charts belong to registrants that were later acquired: 27%, against 7% in the sample. Because exit status is future information, this is a confound to note, not a usable rule.

## 4. Deterministic definitions

All definitions use data up to day t only.
- **B1 leader:**
  - close_t ≥ 0.97 × max(close over the last 252 sessions);
  - close_t > SMA50_t > SMA200_t;
  - SMA50 and SMA200 both above their values 20 sessions earlier.
  - Optional smoothness condition: fraction of up days over 252 sessions in the top quintile, or the "information discreteness" ID < 0, the frog-in-the-pan measure.
- **B2 pullback in uptrend:**
  - the B1 trend conditions hold 20 sessions ago;
  - the drawdown from the 252-session high is between 3% and 12%;
  - close_t is within ±2% of SMA50_t.
- **B3 gap-and-hold:**
  - open_d / close_{d−1} − 1 ≥ 5%;
  - volume_d ≥ 3 × the 50-day median volume;
  - for 20 sessions after d, no close below close_{d−1};
  - signal on day d + 20.
- **B4 V recovery:**
  - 252-session drawdown at the trough ≥ 25%;
  - close_t ≥ trough × 1.25;
  - close_t > SMA200_t.
- **B5 breakdown (exit or avoid):**
  - close_t < SMA200_t;
  - SMA50_t falling;
  - drawdown from the 252-session high ≥ 15%.

## 5. Comparison with hypotheses H001–H032

| Behaviour | Already tested (`research/hypotheses/STATUS.md`) | Verdict |
|---|---|---|
| B1 leader / smooth trend | H002 12-1 momentum, H003 52-week high, H019 S1 / S2 (frog-in-the-pan ID, the same smoothness idea) / S3 trend factor, H018 trend grammar, H020 chart score (HH / HL, base, trend) | **Substantially similar; rejected.** H019 found no momentum effect at all in ≥ $2B US stocks for 2011–2017. |
| B2 pullback | H004 pullbacks in momentum leaders, H014 trend + pullback + recovery | Rejected |
| B3 gap-and-hold | H010 gaps (C02), H017 earnings-reaction continuation: wealth beat SPY, but significance and robustness failed | Rejected; H017 was "promising but not qualified" |
| B4 V recovery | H001 short-term reversal, H014 recovery leg | Rejected; also dominated by market regime |
| B5 breakdown | Exit or avoid rule (trend exits in H018, H015 not adopted). Defensive, not offensive. | Not an offensive edge |

Renaming any of these would be presenting a rejected concept as new.

## 6. Reasons for and against an economic edge

**For** (literature only, not evidence from these charts):
- under-reaction to gradual information (frog-in-the-pan);
- post-earnings drift after large reactions;
- slow institutional accumulation in stair-step leaders.

**Against:**
- In this programme the same ideas failed on ≥ $2B US stocks 2011–2017 under rigorous nulls: H019 momentum t ≈ 0.2, H020 chart score, H017 significance.
- The H018 lesson applies: no-edge worlds always contain beautiful trending charts. A visually compelling leader is expected even when there is no edge.
- Most visible structure here is past return, market regime or single information events, including acquisitions.
- Nothing in 299 charts points to a price / volume feature that is both distinct from those and visibly frequent.

## 7. Recommended hypothesis

**None.** The observations do not genuinely support a new, distinct offensive hypothesis.

The least-tested angle is **held up-gap accumulation**: the count of large, volume-confirmed up gaps that were not filled over the past 252 sessions, read as repeated positive information events. It remains a combination of H017 (single-event continuation) and momentum, so I record it only as a candidate for the owner to consider, not as a recommendation.

## 8. Smallest rigorous future test (if the owner nonetheless pursues the B3 angle)

A **signal-level** falsification test in the style of H019, pre-registered before any data:
- one signal: held-gap count;
- primary statistic: incremental rank IC over 12-1 momentum and the H017 single-event reaction, with Newey–West standard errors;
- inference: an identity-tethered permutation null with a pre-pinned critical value;
- no portfolio and no parameter variants.

**Constraint:** no independent window exists.
- 2010–2021 on QuantConnect is already exposed (D285).
- 1999–2009 QuantConnect fails the universe audit (RR3).
- WIKI 1999–2009 is unviewed but survivorship-unverified, and has no SEC frame before XBRL.

Any result would therefore be exploratory, not confirmatory. Given that, my assessment is that this test is unlikely to be worth its cost.

**Method lessons for any future chart work:**
- render **relative to SPY**, so market regime is removed;
- use close-based features, because wick artefacts are present;
- double-code a subset to measure tag reliability.

## Constraints kept

- No backtest, no forward return or outcome computed for any chart, and no parameter search.
- No strategy registered, no QuantConnect run, no purchase.
- No 1999–2009 bar viewed (context bars start in 2010). Holdout sealed.
- Audit result unchanged (INSUFFICIENT).
- Only blinded images were sent; no raw tables. The mapping stays local.
- **Not verifiable from this session:** the Claude model-training setting is an account setting the owner must switch off.

**STOPPED.**
