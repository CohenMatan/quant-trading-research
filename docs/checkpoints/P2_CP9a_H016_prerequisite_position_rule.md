# P2-CP9a — H016 prerequisite 7 failed: the approved position rules cannot form the portfolio (STOP)

- **Date:** 2026-10-02.
- **Context:** the owner approved the H016 pre-registration and authorised development execution, provided every prerequisite passes. **"If any prerequisite fails, stop rather than bypass it."**
- **State:**
  - **Nothing was run on QuantConnect.** No H016 candidate or control was run, and no canary.
  - Phase 2 slot 2 is **not** consumed.
  - The Holdout is locked.
- **Status:** STOP, awaiting one owner decision.

## 1. What failed

**Prerequisite 7, "verify the $4,500 minimum-position rule".**

At $100K, 20 equal positions are about $4,900 each. The approved D051 execution rules, which H016 keeps, require:
- buys funded only from settled cash;
- a 2% cash buffer;
- a **15% reserve for opening gaps** on every buy (an order is sized so that cash still suffices if the stock opens 15% higher).

**Consequence:**
- The harness scales every first purchase from about $4,900 down to about **$4,250**.
- That is below the new **$4,500** minimum, so the harness skips it.
- On an all-cash account **no position is ever opened**, on the first day or any later day.
- Replacements at later rebalances are squeezed in the same way.

Under the same reserve, even at $200K the portfolio stays about 15% in cash if positions are never topped up after the first, scaled fill.

**Why it matters:** run as written, H016 at $100K would hold cash for twelve years and test nothing.

## 2. Evidence

`research/phase2/H016_position_rule_check.py` / `.json` uses the harness's own order planner, no market data and no strategy returns.

| Rule set | Positions formed | Invested | Average position | Orders to form |
|---|---|---|---|---|
| **Approved as written** ($4,500 min, 15% gap reserve) | **0** | 0% | — | 0 |
| **A:** $4,000 min, 15% reserve kept, positions built to slot value from settled cash | 20 | 97.5% | $4,850 | 60 |
| A without building | 20 | 85.2% | $4,250 | 20 |
| **B:** 5% gap reserve for H016, $4,500 min | 20 | 93.2% | $4,650 | 20 |
| **C:** approved rules; only entries cash funds at full size | **19** | 93.2% | $4,895 | 19 |
| $200K, approved rules, no building | 20 | 85.1% | $8,500 | 20 |
| $200K, approved rules, built to slot value | 20 | 97.9% | $9,750 | 80 |

## 3. Options

**A (recommended):**
- Lower the minimum new position to **$4,000**, which only matters for the first, reserve-scaled fill.
- Keep D051's 15% gap reserve intact.
- **Build** each new position to its slot value: at the following closes, while it is below 90% of its slot value at entry, it is topped up from settled cash; afterwards it is never resized.
- **Result:** 20 positions close to equal weight (about $4,850), about 97% invested.
- **Cost:** about 40 extra small orders at formation and about 5–10 per quarter afterwards, roughly +0.2% a year. That is well inside G4(c)'s 1.5% cap.
- It honours your intent ("about $5,000 per position, room for price/fill variation") and keeps the protective cash rule.

**B:**
- Reduce the gap reserve to **5% for H016** and keep $4,500; no building.
- **Result:** 20 positions at about $4,650, about 93% invested (about 7% cash, a drag of roughly 0.5% a year).
- The simplest option, but it weakens a protective execution rule. A gap above 7% at the open could leave cash slightly negative and fail the no-leverage integrity check.

**C:**
- Keep every approved rule, and submit only as many entries as settled cash can fund at full size.
- **Result:** 19 positions (the 20th slot is never funded), about 93% invested. It contradicts "20 positions".

**Applies to every book:** whichever option is chosen applies identically to the candidate, the five random controls, the $200K sensitivity and the perturbations. The same-universe EW benchmark (B901 mechanics, $10M paper notional) is unaffected.

## 4. What is ready (no QuantConnect runs)

| Component | File | Status |
|---|---|---|
| H016 specification (complete except §6.3) | `research/phase2/H016_spec.md` | DRAFT; frozen and hash-pinned once §6.3 is decided |
| Decision logic: GP/A, schedule, rankings, selection | `src/qresearch/lean/qr_h016.py` | Done; 8 tests incl. truncation (no look-ahead), same-quarter assets, negative GP, freshness |
| Strategy for every book: candidate, EW-H016, random controls | `strategies/S016_gross_profitability/main.py` | Done; options A/B/C are parameters only |
| Evaluation: common window from 2010-03-01, G1–G4, G2 median of 5, DSR, survivorship sensitivity S1/S2 | `src/qresearch/p2h016.py` | Done; 5 tests |
| Portfolio rule restricted to S016 (earlier experiments untouched) | `config.H016_PORTFOLIO`, `experiment.validate` | Done; holds the approved values until you decide |
| Frozen random seeds | Spec §6.1: seeds 1–5; canary seed 0 | Fixed now, before any result |
| Survivorship sensitivity | Spec §10, `p2h016` constants | Frozen inputs from the completed audit |

**Not done** (deliberately, until the decision):
- freezing the spec hash;
- the run configs;
- the canary;
- any run.

Data infrastructure v1 is unchanged (freeze test passes).

## 5. Decision required

**Choose A, B or C for §6.3.** After that I will:
1. record it in the spec and freeze the spec (hash-pinned);
2. write the configs;
3. run the non-candidate canary (E980-01) and verify every prerequisite;
4. then run the authorised plan, stopping at the development checkpoint.

**STOP.**
