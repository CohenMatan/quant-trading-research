# X967: fundamental-data point-in-time integrity audit (infrastructure)

- **Purpose:** data quality and coverage only (D106). It places no orders, forms no portfolios and computes no returns or rankings.
- **What it checks:** the audits A–E described in `main.py`.
- **Output:** counts, buckets, dates, SEC accession years and ratios only, never raw Morningstar values (licence).
- **Code:** pure helpers in `audit_lib.py`, tested in `tests/test_fundamental_audit.py`.
- **Report:** `docs/checkpoints/P2_CP4_fundamental_data_audit.md`.
