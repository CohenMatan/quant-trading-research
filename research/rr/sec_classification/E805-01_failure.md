# E805-01 — documented infrastructure failure (SCA-1, D267)

- **What happened:** E805-01 (commit c350dfc, LEAN 18194, backtest started 2026-10-20 10:10:40Z) stopped in
  initialisation after 26 s: `X805: the SEC reference object is not in the Object Store` (the host's own
  `contains_key` guard). QuantConnect compiled and accepted the code (no compliance refusal). No data was processed,
  no aggregate was produced, nothing was exported.
- **State of the Object Store (read-only API checks after the failure):** `object/list` and `object/properties` show
  `rr/sca_sec_v1.json` (4,785,471 bytes, created 10:10:11Z, application/json) — uploaded 29 s before the backtest
  started. The organisation's `objectStorageUsed` still reported 8 bytes at 10:12:30Z, i.e. the upload had not yet
  been registered by the store's accounting: consistent with a propagation delay, not with a wrong key (the key in the
  host equals the key listed).
- **Classification:** documented infrastructure failure (protocol header: "Retry: E805-02, only after a documented
  infrastructure failure, with identical code, settings and SEC object").
- **Retry plan:** E805-02 with identical code (same commit content for host / qr_sca), identical settings and the same
  object (SHA-256 67bc9260…, unchanged in the store), started only after the store's usage accounting reflects the
  object. If E805-02 also fails, the audit STOPS and is reported; no further retry and no workaround.
