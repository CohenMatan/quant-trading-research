# LH-CP3 Protocol Addendum 1 — non-gating truth-audited view (written after the DEVELOPMENT run, before any held-back evaluation)

**Status:** non-gating. It does not change the frozen protocol (`LH_CP3_protocol.md`, SHA-256 38d790e5…), its thresholds V1–V5 or the mechanical classification of §10. Its SHA-256 is pinned in `tests/test_lh_cp3.py`, and it is committed before the held-back run.

## Why it exists (development finding, development registrants only)

**Disagreements with the truth.** In the development run (`LH_CP3_development.json`), R* accepted 60,778 labels. 51 of them disagreed with the "true" L0/L1 label: 35 unique registrant-periods across 30 registrants. That gives V2 a value of 2.77% against a threshold of 2.0% (fail).

**What the 35 periods are.** An offline check of each one against the registrant's own label sequence (development only) shows they are tagging problems in the *truth* labels, not reconstruction errors:
- **11** carry a label that contradicts their own form, for example a 10-Q tagged `FY`;
- **22** are isolated off-cycle labels: the labelled neighbours on both sides lie on one cycle, and only this label departs from it;
- **2** sit in visibly garbled sequences, for example 4, 3, 3, 3, 4.

In every one of the 35 periods, both independent methods (M-SEQ and M-CMP) agreed with each other.

**No rule change.** No reconstruction-rule defect was found, so `lh_cp3_rules.py` is frozen unchanged.

## What is added

For every trial, `truth_suspect` is set when either condition below holds. It is computed **from the truth labels and form types only**, independently of any reconstruction output.

1. **Form-inconsistent label:** a 10-Q labelled 4, or a 10-K / 10-K405 labelled 1–3.
2. **Isolated off-cycle label:** `lh_cp3_rules.isolated_off_cycle` flags the period in the registrant's full L0/L1 label sequence.

The held-back JSON reports the method statistics a second time with these trials set aside (`addendum1_truth_audited_non_gating`).

**The official classification remains the frozen, unaudited one.** The audited view is reported next to it for the owner's judgement, never instead of it.
