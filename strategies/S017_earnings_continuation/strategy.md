# S017 — H017 earnings-event continuation (candidate, random-event controls, EW-H017)

- Frozen specification: `research/phase2/H017_spec.md`. Hypothesis: `research/hypotheses/H017.md`.
- Pure logic: `src/qresearch/lean/qr_h017.py`. Event table v1: `src/qresearch/lean/qr_h017_events*.py` (packed, SHA-256 checked on load), built by `research/phase2/h017/h017_event_table.py`.
- Books (params `book`): `candidate`, `random` (seed), `ew`. One code path; the canary X982 is a byte copy.
- Runs: E017-01..17 (configs written; each needs explicit owner approval, enforced by the runner), canary E982-01.
