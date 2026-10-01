Phase 2 — Approve SEC Verification and Survivorship Remediation Before H016
I approve the next infrastructure step for the fundamental-data programme.
H016 is still not approved.
The next phase is limited to:

1. SEC verification of QuantConnect fundamental timing/values.
2. Repair or reduction of the D043 survivorship gap.
3. Re-audit of coverage and remaining bias.

Do not define or backtest H016 during this work.
1. Existing PIT policies — approved
Keep the following policies already implemented:

* approved-field whitelist;
* unsafe-field blacklist;
* no direct use of shares outstanding, EPS or unsafe per-share/vendor-derived ratios;
* +90 calendar days for estimated filing dates;
* quarantine of suspicious records whose historical validity is unclear;
* Visa dated exchange correction for future research only;
* financial-company exclusion based on filing/report structure rather than unsafe current sector metadata;
* 200-day freshness limit;
* hard failure if an unapproved field is requested.

Do not rewrite prior research results because of these infrastructure improvements.
2. SEC access
Enable or use access to:

* `data.sec.gov`
* `www.sec.gov`

Start a new session if required for the network-policy change to take effect.
Use an SEC-compliant User-Agent/contact identifier.
A project-specific identifier is acceptable if no personal contact email is provided.
Respect SEC request-rate guidance and cache retrieved data where appropriate.
3. Independent SEC verification sample
Before repairing D043, independently verify the QuantConnect/PIT behavior against authoritative SEC data.
Use a representative sample including, where feasible:

* normal 10-Q;
* normal 10-K;
* amended filing;
* delayed filing;
* accounting restatement;
* company with a split;
* acquisition/delisting case;
* 2010–2012 case using estimated filing timing;
* at least one quarantined record.

For each sample, document:

```
company
fiscal/reporting period
SEC form
SEC filing date
relevant financial value in SEC filing
QuantConnect value
QuantConnect availability date
PIT-layer exposure date
match / mismatch
```

Clearly distinguish:

* confirmed;
* vendor-supported but not independently confirmed;
* unresolved;
* unsafe.

If SEC verification reveals a systematic timing or value problem, stop before attempting H016.
4. Resolve the 0.3% accession/restatement anomaly
Investigate the quarantined records whose accession metadata appears to correspond to a later filing.
For each sampled anomaly determine:

* whether the financial value existed in the original filing;
* whether QuantConnect is supplying a later restated value;
* whether only the accession reference is wrong while the underlying value is historically valid.

Do not automatically unquarantine these records.
Only release a quarantined record if its historical validity is established.
If unresolved, keep it excluded.
Report how much coverage is lost because of quarantine.
5. D043 survivorship remediation
Attempt to reduce the known missing-company survivorship gap using historical SEC data.
This is infrastructure reconstruction only.
Do not calculate factor returns or strategy performance.
The reconstruction must use only information available historically.
For each missing company/date determine whether you can reconstruct:

* existence/listing status;
* required fundamental statement totals;
* historical market capitalization sufficient for universe eligibility.

Do not use present-day survival status or later company information to infer historical eligibility.
6. Share-count reconstruction — special caution
Do not assume:

```
SEC share count × historical price = valid historical market cap
```

without establishing exactly what the share-count number represents.
Before using SEC share counts, document:

* the SEC/XBRL concept;
* whether it is shares outstanding at a specific date or weighted-average shares;
* the exact date associated with the value;
* whether it is split-adjusted;
* whether later corporate actions can alter interpretation;
* whether multiple share classes exist;
* whether the number can safely be carried forward to later dates;
* how long it remains valid.

Prefer a shares-outstanding snapshot tied to a known historical date.
Do not use weighted-average diluted/basic shares from the income statement as a substitute for point-in-time shares outstanding.
If safe historical market capitalization cannot be reconstructed for a company, leave it unresolved rather than inventing an approximation.
7. Corporate actions
Any reconstructed share-count history must correctly handle:

* stock splits;
* reverse splits;
* mergers;
* spin-offs;
* share-class changes;
* acquisitions;
* substantial issuance/buyback events where historical share counts change.

Do not apply future split factors backward unless that transformation is explicitly required to align the SEC figure with the historical price series and is demonstrably point-in-time safe.
Document the convention used.
8. Dated correction layer
If the missing-company data can be repaired, build it as an explicit dated correction layer.
Every correction should have:

* company/security identifier;
* effective historical date range;
* source filing;
* source filing date;
* source value/date;
* reconstruction method;
* confidence/status.

The correction layer must be reproducible and auditable.
Do not silently patch the universe.
9. Coverage target and bias re-audit
After remediation, recompute yearly 2010–2021 coverage.
Report:

* true/estimated historically eligible companies;
* companies available in native QuantConnect data;
* companies recovered through corrections;
* unresolved missing companies;
* usable coverage percentage;
* missing companies that later delisted/failed;
* missing companies acquired successfully;
* missingness by year;
* missingness by size where possible.

Compare the result with the pre-remediation gap:

```
~14% missing in 2010
→ ~1% missing by 2021
```

Quantify how much of that gap was repaired.
10. Bias direction
Reassess whether the remaining missingness is systematically optimistic or pessimistic.
Do not use H016 or any quality ranking.
You may characterize the missing companies using historical outcomes already required for the survivorship audit, but do not turn this into factor research.
Answer:
Is the remaining universe sufficiently representative to support a profitability/quality backtest?
If the answer is uncertain, state that clearly.
11. Financial-company exclusion audit
Retain the filing-structure-based financial exclusion, but audit the approximately 2% disagreement with vendor templates/classifications.
Determine whether mismatches are:

* random;
* concentrated in specific financial subtypes;
* concentrated in non-financial companies with unusual reporting formats.

Create an explicit exception policy if needed.
Do not use current sector metadata to resolve historical classifications.
The candidate, benchmark and controls must eventually use the same historically defined universe.
12. PIT canaries after remediation
Run infrastructure-only canaries to verify:

* original SEC filing not visible before its filing date;
* amendments only visible after amendment filing;
* quarantined values stay hidden;
* reconstructed missing companies enter only when historically justified;
* reconstructed market cap does not use future share information;
* split handling is correct;
* acquisitions/delistings terminate eligibility correctly;
* Visa correction still behaves correctly;
* financial exclusion is stable;
* coverage reports reproduce deterministically.

No strategy trades.
No factor returns.
13. No H016 design
Do not decide or test:

* ROA;
* ROE;
* gross profitability;
* operating profitability;
* FCF yield;
* ranking formula;
* top-N cutoff;
* rebalance frequency;
* portfolio size;
* quality + value;
* quality + momentum.

Do not compare which fundamental metric historically performs best.
This phase is only about making the data trustworthy.
14. Phase 2 status remains unchanged
Keep:

* H014 rejected.
* H015 not adopted.
* Only 1 of 3 Phase 2 hypothesis slots consumed.
* Two slots remain.
* 2010–2021 development.
* 2022–2026 locked Holdout.
* G1–G4 unchanged.
* +0.25 Sharpe margin unchanged.
* DSR diagnostic only.
* PBO diagnostic only.

Do not access the Holdout.
15. Required checkpoint
Prepare a SEC Verification and Survivorship Remediation Checkpoint containing:

1. SEC-access status.
2. Verification-sample results.
3. QuantConnect-vs-SEC timing results.
4. QuantConnect-vs-SEC value results.
5. Restatement/accession anomaly findings.
6. Share-count reconstruction policy.
7. Historical market-cap reconstruction policy.
8. D043 repair method.
9. Companies/periods repaired.
10. Companies still unresolved.
11. Coverage before and after repair.
12. Remaining survivorship-bias assessment.
13. Financial-exclusion audit.
14. Canary results.
15. Automated tests.
16. Remaining risks.
17. A clear decision:
   * safe enough to design H016, or
   * not safe enough yet.
18. Any owner decisions still required.

Commit all code, evidence and documentation to GitHub.
STOP CONDITION
Do not define H016.
Do not run fundamental strategy backtests.
Do not calculate factor performance.
Do not consume a hypothesis slot.
Do not access the Holdout.
If reliable point-in-time reconstruction cannot be achieved, stop and report that limitation rather than approximating it away.
Stop after the checkpoint and wait for my approval.