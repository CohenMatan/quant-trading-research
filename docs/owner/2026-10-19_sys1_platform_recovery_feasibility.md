# Owner decision D255 — SYS-1 platform compliance and recovery feasibility (2026-10-19)

**Context:**
- This follows D254 (E032-01 refused at upload; `docs/checkpoints/SYS1_CP0_e032_01_upload_refused.md`, PR #118).
- The message is recorded verbatim below.

---

Owner Direction — SYS-1 Platform Compliance and Recovery Feasibility
I have reviewed the E032-01 upload refusal and D254.
I do not approve closing SYS-1 yet, but I also do not approve attempting another upload or bypassing QuantConnect's new restrictions.
Please conduct one read-only, documentation-only feasibility assessment of restoring SYS-1 through a compliant, reproducible approach.
1. Verify the current state
Verify the latest repository state, PR #118 and D254.
Preserve the failed-upload record.
E032-01 was blocked before a backtest started. It produced no experimental result. E032-02 remains unauthorized until a new compliant implementation passes the required canary.
H028 remains REJECTED. The Holdout remains sealed.
2. Investigate Option B first — QuantConnect Object Store
QuantConnect's published documentation indicates that paid organizations receive 50 MB of included Object Store capacity.
Determine, without uploading or moving data:

* Whether our actual organization has Object Store access and sufficient remaining quota.
* The size and number of required reference objects.
* Whether the data can be legitimately stored and read inside QuantConnect Cloud under the current Terms of Service.
* Whether the data's existing provenance and location permit the proposed migration.
* Whether any stored material would violate the restrictions on encoded, compressed or obfuscated source code.
* Whether the project can use readable, compliant Python source without importing prohibited compression utilities.
* Whether Object Store access creates runtime, memory, file-count or cost problems.
* Whether the exact H028 frozen behavior can be reproduced after migration.
* Whether a new data-version manifest, hash and full canary are required.

Do not use local copies of QuantConnect Platform Data in a way that violates the current terms.
Do not extract, export or reconstruct Platform Data outside QuantConnect.
Do not upload existing compressed reference files or use an alternative encoding to disguise them.
If compatibility with the Terms of Service cannot be established, classify this option as BLOCKED PENDING CLARIFICATION.
3. Investigate Option A second — Reduced Plain-Text Data
Determine whether a minimal, readable, non-obfuscated dataset containing exactly the predeclared information SYS-1 needs could fit the current project limits.
Report:

* Required source files and their sizes.
* Which fields are genuinely used by the frozen host.
* Estimated resulting file count and total size.
* Historical coverage and identity requirements.
* Whether the reduction changes any frozen strategy input or selection.
* Whether the reduced version can reproduce E030-05 exactly.
* Whether the approach is compliant rather than a workaround for platform restrictions.

Do not split or encode Platform Data to circumvent project limits.
Do not actually produce a replacement dataset yet.
4. Existing Legacy QuantConnect Projects
Do not delete or modify existing H026–H028 projects.
Prepare a read-only inventory using permitted metadata and existing local source-code records.
Distinguish between:

* Historical project source code.
* Reference data stored in project files.
* Existing backtest records and research evidence.
* Items whose retention or use may be restricted by the updated Terms.

Do not download project files containing Platform Data.
Explain whether leaving the projects untouched raises any compliance uncertainty.
If deletion or remediation is advisable, propose a safe procedure for separate owner authorization.
Do not assume that a previously accepted upload remains compliant for new use.
5. Financial and Research Constraints
No new subscription, storage purchase, data purchase or plan upgrade.
No QuantConnect backtest.
No new data export.
No change to H028 selection rules.
No allocation tuning.
No new experiment results.
No Holdout access.
Do not change the frozen SYS-1 protocol during this assessment.
Any future migration requires a separately approved new implementation freeze and exact-reproduction canary.
6. Deliverable
Create a concise checkpoint:
SYS-1 Platform Recovery Feasibility — Options A and B
For each option provide:

* Technically feasible: YES / NO / UNKNOWN.
* Terms compliance: SUPPORTED / UNCERTAIN / BLOCKED.
* Fits existing plan: YES / NO / UNKNOWN.
* Expected additional cost.
* Required files and infrastructure changes.
* Risk to exact H028 reproduction.
* Estimated engineering effort.
* Unresolved dependencies.
* Recommendation.

Conclude with one of:

1. Approve preparation of a compliant Object Store migration.
2. Approve preparation of a minimal readable-text implementation.
3. Request explicit platform clarification.
4. Close SYS-1 as PLATFORM BLOCKED.

This is a feasibility study only. Do not implement the proposed solution.
Record the owner direction, commit the documentation through the usual workflow and STOP for my review.
Our goal is to preserve research integrity, not to force SYS-1 to execute at the expense of compliance.
