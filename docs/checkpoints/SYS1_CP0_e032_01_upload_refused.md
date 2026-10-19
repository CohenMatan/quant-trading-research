# SYS1-CP0 — Canary E032-01 refused at upload: QuantConnect no longer accepts compressed or encoded project files (STOP)

**Date:** 2026-10-19.
**Decisions:** D252 (SYS-1 approval), D253 (QuantConnect terms accepted; $1,000 ETF minimum trade approved).
**Status:** STOPPED awaiting the owner.

**Not done:**
- No SYS-1 result exists. No backtest was created and no data was read.
- E032-02 was not run.
- No retry was used: E032-03 / E032-04 are untouched.
- Nothing was changed in the frozen experiment.

H028 remains REJECTED — Frozen Defensive Research Reference. The Holdout stays sealed.

## 1. What happened

1. **Access check.** After the owner accepted the new QuantConnect terms (D253), the API answered normally (no running backtest).
2. **Start of E032-01.** E032-01 was started from the clean, committed tree (commit 62b623b, frozen protocol 2a16618f…).
3. **Refusal during upload.** QuantConnect refused to save one of the project files:

   > Cannot save 'qr_p7_export.py': it imports the compression package 'zlib'. Compressing, encoding, embedding binary blobs or otherwise obfuscating source code is against the QuantConnect Terms of Service; all project files must be saved as readable plain-text source. If you are hitting the file length limit, split the code over multiple files instead.

4. **Record.** The runner recorded E032-01 as **failed at the upload stage** (runtime 0 s, no backtest id) in `experiments/INDEX.csv`, `experiments/E032-01/result.json` and `report.md`.

## 2. Why it matters

This is a new platform rule, apparently part of the terms the owner just accepted. It does not hit only one file. It blocks the whole frozen chain that SYS-1 builds on, which is also the chain of H026–H028:

| part of the 49-file upload | affected? | why |
|---|---|---|
| `qr_p7_export.py` (frozen Score v1 helpers; packs result blocks) | **yes** | imports `zlib` and `base64` |
| `qr_data_v21.py` + `qr_data_v21_00..20.py` (frozen Data v2.1 reference table: SEC references, market-cap repair, guard, identity) | **yes** | the table is stored lzma-compressed and base85-encoded (21 files, 1.27 million characters) |
| everything else (hosts, H026–H028 logic, `qr_sys1`) | no | readable plain source |

**The table cannot simply be written out as plain text.**
- Decompressed, it is about **5.48 million characters** even as compact JSON.
- A project may hold at most 50 files of 64,000 characters each: **3.2 million** in total, before any code.
- So the frozen Data v2.1 infrastructure cannot be uploaded in any rule-compliant form as it stands.

**A retry would be pointless.** A documented retry (E032-03) uses identical code and would be refused identically. I did not use it.

**Scope beyond SYS-1.** Every QuantConnect host that carries packed reference data has the same problem: Data v2 / v2.1 / v3, the H017 and H025 event ledgers, and the SEC correction table. So does any host that emits packed result blocks.

**Housekeeping question.** Earlier QuantConnect projects (e.g. qr-S030) still contain such packed files. The owner may want to decide whether they should be removed from the QuantConnect account. I have not touched them.

## 3. Options (each needs an owner decision; nothing is started)

### A. Plain-text rebuild of the frozen chain

A new data version, "v2.2 plain text": the reference table written as readable source, and compression removed from `qr_p7_export`.

- **Size:** it does not fit as it stands (5.5M vs 3.2M characters). It would need the table cut to only what SYS-1 actually reads.
- **What that takes:**
  - an engineering study;
  - changes to frozen, pinned modules;
  - a new freeze;
  - proof that the frozen H026 panel digests and the exact E030-05 result are reproduced.
- **Assessment:** uncertain feasibility, large effort.

### B. Keep the reference table out of the source

Store it as a data file in QuantConnect's Object Store, read at run time; source modules plain text only.

- **Unknowns, to be checked before anything else:**
  - whether our plan includes Object Store space, or whether it costs money;
  - whether QuantConnect's compliance review accepts it.
- **Effort:** the loader, the result emission and the pins change. That means a new data version and an exact-reproduction canary again.
- **Assessment:** smaller code change than A, but platform and cost unknowns.

### C. Stop SYS-1

Record SYS-1 as **NOT RUN — PLATFORM BLOCKED**.
- This is not a FS-1..FS-6 classification: the architecture was never tested, so it is neither NOT EXECUTABLE nor NOT SUPPORTED.
- SPY remains the simple baseline.
- No QuantConnect-dependent research continues until a compliant data path exists.

**Recommendation:** first a **no-run feasibility study** of A and B. It would cover:
- which parts of the reference table the SYS-1 chain actually reads, and their plain-text size;
- whether the Object Store is available on our plan, and at what cost;
- what changes in which pinned files.

That study involves no backtest, no result and no purchase. Then the owner chooses A, B or C. If the study shows neither is feasible within budget, option C is the honest outcome.

## 4. What is unchanged

- The frozen SYS-1 protocol, engine, host, parameters, screens and configuration (pins in `qresearch.sys1`), and the owner approvals D252 / D253.
- E032-02 still runs only after a canary passes every mandatory check.
- No Holdout access, no allocation optimisation, no H028 change, no additional experiment.

## 5. Owner decision needed

1. Approve the no-run feasibility study of options A and B, choose an option directly, or stop SYS-1 (option C).
2. Optional: should the older QuantConnect projects that contain packed files be cleaned up?
