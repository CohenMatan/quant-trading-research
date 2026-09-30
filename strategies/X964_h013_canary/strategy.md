# X964: C03 H013 infrastructure canary

It runs the unchanged S013 code (`s013.py`, `signals.py` and `nullorder.py` are byte copies, pinned by a test) with the **non-candidate** setting q = 0. All other settings are those of the null run E962-22, so its fills must equal E962-22's exactly.

**Audit:** every 10 sessions it also checks the exclusion at q = 0.25, for both MAX and MAX5. It never trades on this audit. It checks:

- the statistics against fresh point-in-time history, with windows ending at today's bar;
- the count and ordering of the excluded set, including that stocks with short histories are never excluded;
- that the allowed order is the null's order minus the excluded names.

It is verification, not a trial.
