# S018 — Phase 3 frozen technical search engine (H018)

- `main.py` is a **byte copy** of `strategies/X984_p3_engine/main.py` at the fidelity-verified revision (E984-09: every tolerance passes for all 6 control books; batch independence E984-07 = E984-08). `tests/test_p3_spec.py` checks the copy.
- **Search mode only** (`params.mode = "search"`), within the frozen specification `research/phase3/P3_spec.md` (hash-pinned in `qresearch.p3spec`).
  - **Null worlds** (`seed`, optional `block`): kind infrastructure, never strategy trials.
  - **The real world** (`name: "real"`, identity mapping): runs alone as the single research run, E018-07.
  - **Finalist trace** (`params.trace`): an infrastructure run on the real world (§15).
- `experiment.validate` enforces the frozen settings:
  - window 2010-03-01 → 2017-12-31, warm-up 2009-07-01;
  - $100K, 10 slots, 63 sessions, 10 bps, the H017 portfolio rules;
  - H018 / P3;
  - `owner_approval_required`.
- **Nothing runs without the owner's explicit approval** (runner `--owner-approved <decision id>`).
