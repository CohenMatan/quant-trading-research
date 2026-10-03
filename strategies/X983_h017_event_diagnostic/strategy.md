# X983 — H017 event-level diagnostic (E983-01; non-trading, aggregated; never a gate)

- Pre-declared in `research/phase2/H017_spec.md` §8. Used only within the PbNQ rule 7.
- **PREPARED, NOT RUN.** It computes post-event returns, so its config carries `owner_approval_required` and the runner refuses it without `--owner-approved <decision id>`.
- Analysis: `research/phase2/h017/E983_analyse.py`.
