# LH-CP2 — Fiscal Calendar Anomaly Resolution: INVESTIGATION PROTOCOL (frozen before any new aggregate)

**Owner decision:** D243 (`docs/owner/2026-10-18_lh_cp2_fiscal_calendar_anomaly_resolution.md`).

**Nature:** offline SEC metadata investigation. No price, return, QuantConnect run, surprise value or ranking. The frozen Stage C protocol, its hash (`ff97789b…`), results and classification (**C — NOT FEASIBLE**) are not modified.

**Hash rule:** this file's SHA-256 is pinned in `tests/test_lh_cp2.py`. It is committed before the investigation script produces any aggregate.

## 1. Cut-off enforcement

Every record dated after 2021-12-31 is dropped inside the loaders (`research/longhorizon/cp2/lh_cp2_safe.py`) before any caller can see it:
- companyfacts: filed, end and start dates;
- submissions: filingDate and reportDate;
- XBRL filing index: filed and period.

All outputs and examples pass `assert_no_post_cutoff`. Tests cover the loaders on synthetic and cached records.

## 2. Populations

- **P1 (reproduction):** the committed post-hoc diagnostic, re-run unchanged (`LH_StageC_fye_diagnostic.py`). It covers **unique** contiguous filing-table chains (13 and 5 periods) of all 3,941 Data v2.1 registrants, anchor periods 2011–2021, regardless of eligibility or values. Its output must equal the committed JSON.
- **P2 (Stage C-aligned):** the frozen Stage C stock-month population (U_NF), rebuilt with the frozen Stage C functions:
  - E981-01 universe;
  - Data v2.1 identity;
  - fresh anchor;
  - `chain_back`;
  - `q_detail`.
- **P2 reproduction check:** the C1, C2 and C6 coverage by year must equal `LH_StageC_audit.json` exactly. If not, STOP and report.
- **P2 records:**
  - each input-complete C1, C2 or C6 stock-month (year, security, CIK, anchor and 13-period chain);
  - a **unique chain** = (CIK, 13-period tuple), weighted by its stock-months.

## 3. Code groups (unchanged definitions)

Codes c0, c4, c12 come from `LH_StageC_audit.fye_at` (XBRL index, ±7 days). m = the largest circular day distance from c0. The groups:

| Group | Rule |
|---|---|
| EQUAL | All codes equal |
| S7 | m ≤ 7 |
| S31 | 8–31 |
| QA | m > 31 and within 15 days of 91 or 182 |
| OTHER | m > 31 otherwise (the "1.3%") |
| NOCODE | Any code missing |

## 4. Per-period metadata (all filed ≤ the decision day − 1, and ≤ 2021-12-31)

For each chain period p_k:
- **Accession:** the original 10-Q / 10-K of p_k from the XBRL index (same CIK, period within ±7 days, form 10-Q or 10-K, filed ≤ CUT). If several, the earliest filed.
- **Fiscal label L_k:** the modal `fp` of the companyfacts facts carrying that accession (Q1 = 1, Q2 = 2, Q3 = 3, FY = 4). If there is no accession or no fact, L_k = unknown.
- **Mapping check M_k:** fails if the accession's facts contain no duration fact ending within ±7 days of p_k, or if the XBRL-index filing date differs from the Data v2.1 original filing day by more than 3 days.
- **Transition flag T:** any submissions row of form 10-KT, 10-QT, 10-KT/A or 10-QT/A whose reportDate lies in [p12 − 7, p0 + 7].
- **Identity flag I** (stock-month level, aggregated to the chain as "any"): the security's Data v2.1 identity CIK at the decision day differs from its identity CIK at p12, or E981-01's own CIK list does not contain the identity CIK.
- **Duration evidence:** the share of chain values obtained from direct three-month facts vs year-to-date differences (`q_detail` method).

## 5. Fiscal-label consistency

- **Cycle:** consecutive periods p_{k+1} → p_k satisfy L_k ≡ L_{k+1} + 1 (mod 4, with FY = 4).
- **Same-quarter pairs:** L_k = L_{k+4} for every k = 0 … 8 (the seasonal comparisons of C1 / C2).
- A chain is **label-consistent** if all 13 labels are known and both hold; **label-broken** if all are known and either fails; **label-unknown** if any is unknown.

## 6. Category of a code-changed chain (groups S7, S31, QA, OTHER); first match

| Order | Category | Rule |
|---|---|---|
| 1 | F — transition or amended filing pattern | T true |
| 2 | D — quarter-mapping problem | Any M_k fails |
| 3 | E — registrant or identity change | I true |
| 4 | B — genuine fiscal-year or quarter-structure change | Label-broken |
| 5 | G — unresolved | Label-unknown |
| 6 | A — 52/53-week calendar | Group S7 and label-consistent |
| 7 | C — SEC metadata inconsistency | Groups S31 / QA / OTHER and label-consistent |

**Amendments** (10-Q/A, 10-K/A) existing for chain periods are counted as a descriptive flag. They do not define a category: the frozen value rules use originals and as-known facts.

**The same label and mapping tests are also applied to EQUAL-code chains.** A continuous-looking chain is not proof of comparability (owner §6).

## 7. Comparability answers (owner §6), per category

Measured from §4 and §5:
1. **Quarter-end consistency:** gaps of 80–100 days, true by construction for every chain.
2. **Duration compatibility:** the direct vs year-to-date share.
3. **Continuity-rule detection:** no, for every chain here (they all passed it).
4. **q0 / q4 same fiscal quarter:** L0 = L4.
5. **All seasonal pairs valid:** §5.
6. **Possible incorrect arithmetic:** label-broken or transition chains, where year-to-date derivation can straddle a fiscal change.
7. **PIT:** all inputs are filed ≤ D − 1.
8. **Excludable without changing data:** yes, by flagging the chain.

## 8. Coverage effects (owner §8)

Exclusions are applied to P2 input-complete stock-months, separately and cumulatively:

| ID | Excludes |
|---|---|
| X1 | Chains that are **label-broken or carry T** (genuine fiscal changes that invalidate the quarter comparisons), whatever their code group |
| X2 | Chains with a mapping failure (D) |
| X3 | Chains that are **label-unknown** (unresolved) |

- **Reported:** C1, C2 and C6 coverage by year 2013–2021 against the unchanged **provisional 70% floor**; and the excluded share by FF12 sector, size tercile (SEC total assets at the anchor), firm age (years since the registrant's first SEC filing ≤ CUT: < 5, 5–15, ≥ 15), entrants (first 12 eligible months) and leavers.
- **Rule:** no exclusion is chosen or tuned for coverage.

## 9. Proposed period-validity rule (a proposal only; also computed descriptively)

Rule V is the conjunction of:
- the frozen chain rule;
- labels known and consistent (§5);
- no transition form (T);
- mapping valid (M);
- a valid quarterly value per period (frozen `q_known`).

Its outcomes:
- **Valid:** all hold.
- **Invalid:** labels broken, T, or M fails.
- **Unknown:** labels unknown. Handling: excluded (conservative). The share is reported.

Fiscal-year-end codes are **not** used. 52/53-week years are handled by period ends and durations. A genuine fiscal-year change is handled by restarting the history after the change.

## 10. Final classification (owner §11), applied mechanically

**C — INSUFFICIENT EVIDENCE:** labels are unknown for more than 10% of P2 C1-complete stock-months, or for more than 25% of OTHER-group chains.

**B — MATERIAL UNRESOLVED PROBLEMS:** not C, and either of:
- under rule V, C1, C2 or C6 coverage falls below the provisional 70% floor in any year 2013–2021 (compromising the proposed calculations);
- more than 1% of P2 C1-complete stock-months have **EQUAL** codes but are label-broken. This is a hidden fiscal change that the code test could never see; it signals that consistency cannot be established from codes, and is reported as a blocker if large.

**A — ANOMALIES SUFFICIENTLY EXPLAINED:** otherwise. Every OTHER chain is explained (A / C / E / F) or excludable by rule V (B / D / G), and rule V is PIT-safe.

**A does not change Stage C.** Any exception requires an owner decision.

## 11. Outputs

- `research/longhorizon/cp2/LH_CP2_investigation.py` / `.json` (aggregates and a few metadata-only examples, cut-off-asserted);
- `tests/test_lh_cp2.py`;
- the checkpoint `docs/checkpoints/LH_CP2_fiscal_calendar_anomaly_resolution.md`.
