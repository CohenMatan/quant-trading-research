# X965: Phase 2 H014 infrastructure canary

- **Status:** infrastructure. Not research and not a trial.
- **Code:** `s014.py`, `signals.py` and `nullorder.py` are byte copies of S014's files (tested).
- **What it runs:** NON-candidate parameters over 2010–2012 (configs E965-01..03).
- **What it checks:** the audits A–G listed in `main.py` (indicators vs fresh point-in-time history, masks, ranking, time and MA200 exits, rolls, universe). Its summary line is `QRC65|summary|{...}`.
- **Offline checks:** `research/phase2/P2_canary_check.py` verifies session counting and next-open fills from the `QRC65|exit`, `QRC65|rank` and `QRC65|roll` lines against the fills table.
