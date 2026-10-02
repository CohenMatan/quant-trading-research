# X979: field-level SEC verification of the 135 quarantined mixed-period reports (infrastructure, D114)

- **What it does:** for each target vendor report (2010–2012 quarters whose balance sheet belongs to an earlier period while the income statement matched the original filing, P2-CP6), it compares every releasable flow field with the SEC as-first-filed value of the original 10-Q/10-K. The comparison covers quarterly and fiscal-year revenue, gross profit, net income and operating cash flow.
- **Inputs:** `ref*.py`, built by `research/phase2/sec/build_x979.py`.
- **Output:** ratios, dates and identifiers only.
- **Never:** orders, rankings, returns or exported vendor values.
- **Release rule:** applied offline by `research/phase2/sec/x979_analyse.py`.
