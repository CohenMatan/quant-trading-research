# X978: public-float fingerprints for the identity v2 links found after the 2020-2021 RSS fix (infrastructure, D113a)

- **What it does:** same algorithm as X977, on the (registrant, security) pairs that no earlier fingerprint run measured (mostly links found once the 2020-2021 XBRL RSS archives were parsed). SEC public float / (SEC cover shares x QuantConnect raw close) at each float date, as a contradiction check.
- **Inputs:** `fp_ref*.py`, built by `research/phase2/sec/build_fingerprints.py X978`.
- **Never:** orders, rankings, returns or exported vendor values.
