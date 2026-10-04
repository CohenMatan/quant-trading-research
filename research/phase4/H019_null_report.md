# H019 null distribution and frozen family threshold (committed BEFORE the real evaluation)

- **Date:** 2026-10-04. Owner authorisation D145. Specification `research/phase4/P4_xs_spec.md` v2, SHA-256 `15fb0451d535ae31d234822ad60f58230f580b23a6683f2df67936429a47ca1e`.
- **No real-signal statistic existed when this file was committed.** The real evaluation E020-06 has not run.

## Null method (version: spec v2, section 6)

- Stratified identity-tethered within-date permutation: each receiving stock gets the JOINT feature vector (PRET, ID, A_3 … A_1000) of a random partner of the same stratum ("full" = PRET and ID defined; "partial" = moving averages only) and keeps it while both stay in the cross-section and stratum.
- In every world the COMPLETE procedure is recomputed from the mapped features with the receivers' real returns:
  - the trend-factor regressions (every month from 2010-01), the 12-month coefficient averages and S3;
  - S2's two-stage sort (PRET quintiles, then the ID key within each quintile; PRET, ID and their relation travel together in the feature vector);
  - all per-date statistics, Newey-West t-statistics and promotion inputs.
- Family statistic F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3). Threshold c = the 50th largest of R = 5,000 null F (α = 1%).

## Runs, seeds, completion

| Run | Seeds | Worlds | QC backtest | Code commit | Worlds time | Runner time |
|---|---|---|---|---|---|---|
| E020-01 | 1–1,000 | 1,000 | 059b4d79… | ee8647b | 876 s | 1,194 s |
| E020-02 | 1,001–2,000 | 1,000 | 14395712… | 23d7aa6 | 1,089 s | 1,543 s |
| E020-03 | 2,001–3,000 | 1,000 | f96b206e… | 4ff51fe | 993 s | 1,447 s |
| E020-04 | 3,001–4,000 | 1,000 | 5fcaddd8… | 5b4ecc7 | 900 s | 1,376 s |
| E020-05 | 4,001–5,000 | 1,000 | 1c2f8943… | 1e0b3dc | 820 s | 1,171 s |

- **Completed 5,000 / 5,000 worlds. Failed worlds: 0. Retried runs: 0.**
- Code commits differ only because each run's results were committed before the next run; S020 (byte copy of the canary-verified X985) and the specification are identical in all five.
- Every run saw identical inputs: feature digest `40c2a181dd4555ce4b5e447621bfb2a5d0f6d955675d7a8b5a7c83816fe87857` (the same as the passing canary E985-05).

## Max-statistic distribution

| Quantile | 1% | 5% | 10% | 25% | 50% | 75% | 90% | 95% | 97.5% | **99%** | 99.5% | 99.9% | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F | −0.897 | −0.444 | −0.210 | 0.212 | 0.717 | 1.262 | 1.798 | 2.150 | 2.474 | **2.868** | 3.197 | 3.981 | 4.335 |

**Frozen threshold c = 2.8714967** (the 50th largest of the 5,000 F; the interpolated 99th percentile is 2.868).

Per-statistic null distributions (1% / 50% / 99% quantile; sd):

| Statistic | 1% | 50% | 99% | sd |
|---|---|---|---|---|
| t_S1 | −2.871 | −0.595 | 1.560 | 0.956 |
| t_S2 | −2.849 | −0.546 | 1.693 | 0.970 |
| t_S3 | −2.573 | −0.088 | 2.367 | 1.065 |
| t_inc,S2 | −2.409 | 0.000 | 2.540 | 1.046 |
| t_inc,S3 | −2.548 | −0.035 | 2.492 | 1.058 |

## Empirical false-positive calibration (the null worlds judged by the frozen rules at c)

| Measure | Rate |
|---|---|
| F > c (family statistical gate) | 0.98% (binomial se 0.14%) |
| Any single statistic > c: t_S1 / t_S2 / t_S3 / t_inc,S2 / t_inc,S3 | 0.00% / 0.02% / 0.48% / 0.40% / 0.48% |
| Full promotion rule: S2 or S3 "candidate" | **0.00%** (0 / 5,000) |
| Full rule: S1 replication pass | 0.00% |
| Economic floor alone (top decile ≥ 3%/yr and spread > 0): S1 / S2 / S3 | 0.00% / 0.00% / 0.08% |

## Hashes

| Item | SHA-256 |
|---|---|
| Specification v2 | `15fb0451d535ae31d234822ad60f58230f580b23a6683f2df67936429a47ca1e` |
| `H019_null_result.json` (pinned in `qresearch.p4xs.NULL_RESULT_SHA256`) | `6d5ea4a0056728d116c6b96e3524d8be45bf3dc4e88fb54eb080db9ce44f883c` |
| `H019_null_worlds.csv` (per-world table) | `59a6cfb70fd49fc7d7b741a39225a8025aea6ef8f4692ada5735625971be94fd` |
| Threshold commit | the commit that adds this file and the pins; recorded in `qresearch.p4xs.THRESHOLD_COMMIT` and in the E020-06 config by the next commit |

The threshold is immutable. The real evaluation must start from a clean tree that carries exactly these pins; its host echoes them and the evaluation refuses any mismatch.
