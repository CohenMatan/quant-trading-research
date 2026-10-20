# Owner decision D269 — RR5 / UR-2 (2026-10-20)

**Context:**
- This follows RR5 (D268, `docs/checkpoints/RR5_ur1_sec_classification_audit_E805.md`, PR #125).
- The message is recorded verbatim below, before any work.

---

Owner Decision — RR5 / UR-2
I reviewed RR5, including the SCA-1 audit protocol.
I approve UR-2 Option A: one narrowly scoped SEC-based universe repair attempt, using only existing resources and no additional purchases.
The goal is to resolve the demonstrated 2010–2015 survivorship bias and obtain a credible, reproducible development universe.
This is a bounded final repair attempt, not authorization for an open-ended infrastructure project.
1. Approved Scope

* Implement a narrow in-cloud SEC-based universe repair.
* Use independently sourced SEC data already available in the QuantConnect Object Store.
* Generate all QuantConnect identifiers inside Cloud.
* Preserve the existing $2B market-cap, $5 price, $5M ADV20, US common-stock and exchange requirements.
* Perform one re-audit, with at most one documented infrastructure retry.
* Export only compliant aggregate audit results.
* No strategy backtests, new subscriptions, paid data or Holdout access.

2. Important Point-in-Time Correction
The existing SCA-1 measurement protocol permits SEC ticker evidence to begin 100 days before its first filing.
That retrospective matching convention must NOT be reused for historical investment eligibility.
For the repaired trading universe:

* All security identity and ticker mappings must be available as of the historical decision time.
* No future filing, future ticker history, future company identity or future universe membership may influence selection.
* SEC share counts must be available as of their actual filing dates.
* Handle share splits, stale share counts and multi-class securities explicitly.
* Use a documented, unique, PIT-valid identity match.
* Do not automatically include weak or ambiguous SEC matches solely because the retrospective audit labelled them possible missing.

If these requirements cannot be met, STOP before running the repair.
3. Independent Evaluation of the Repair
Preserve the original RR5 findings and frozen SCA-1 evidence.
Create a separately versioned repair protocol and re-audit specification, frozen before execution.
The re-audit must report:

* Original vendor-eligible universe counts.
* SEC-repaired eligible universe counts.
* Confirmed recovered securities and stock-months.
* Rejected or ambiguous matches.
* Remaining confirmed, possible and unresolved missing populations.
* Survivorship bias and uncertainty by year.
* Effects of dataset snapshot changes.

Do not treat recovery of SEC-identified securities as independent proof of an unbiased universe.
Explain which findings are verified by independent evidence and which rely on the same SEC data used for the repair.
Do not relax the original coverage or survivorship thresholds after seeing the results.
A PASS requires credible evidence that the remaining relevant universe risk is acceptably bounded. Otherwise return FAIL or INCONCLUSIVE.
4. Hard Stop
This approval covers one repair implementation and one re-audit only.
If the repaired universe remains FAIL or INCONCLUSIVE, STOP and report the remaining problems.
Do not automatically start another repair, shorten the development period, relax universe rules or accept a known bias.
We will then reconsider the research design separately.
5. Research Protocol and H031
I approve the RR screen v2 methodology in principle, including:

* D1 and D2 development screening.
* Explicit recognition of prior research exposure.
* One Holdout candidate for the entire programme.
* Separate written approval before any Holdout access.

However, do not freeze the final executable programme protocol until the universe definition and historical window are settled.
The current vendor-only universe definition may need updating if U-C succeeds.
Keep H031 in DRAFT status. No event canary or strategy run is authorized yet.
6. Final Deliverable
After the re-audit, produce a concise checkpoint answering:

1. Did the SEC repair work with strictly point-in-time data?
2. Is the 2010–2021 universe now credible enough for research?
3. What measurable bias or uncertainty remains?
4. Is any additional repair actually necessary?
5. Can we now freeze the programme protocol and proceed to the H031 event canary?

Commit the results through the normal workflow and STOP for owner approval.
Our priority remains finding promising investment strategies with our existing QuantConnect subscription, not building an indefinitely expanding data-repair system.
