# X980 — H016 non-candidate technical canary (infrastructure; not a trial)

- `main.py` is a **byte copy** of `strategies/S016_gross_profitability/main.py` (`tests/test_h016_sizing.py` checks this). The candidate, the random controls and the canary therefore run identical mechanics.
- The run (E980-01) uses `book` random with **seed 0**, which is not one of the five frozen control seeds, plus `canary: true`.
- **In-algorithm checks** (summary line `QRS016|summary|…`):
  - `pit_violations` = 0;
  - `financial_in_universe` = 0;
  - `max_topups_per_position` ≤ 1;
  - `min_topup_planned_usd` ≥ $250;
  - `max_topup_over_target_usd` ≤ 0.
- The GP/A ranking is shadow-computed at each rebalance and logged only as a count and a selection hash (`SH|…`). It is never traded or valued, so the canary never reveals candidate performance.
- **Offline checks** (`research/phase2/H016_canary_check.py`, from the fills and the equity curve):
  - 20 positions form;
  - the reserve is preserved;
  - no new purchase below the minimum;
  - at most one top-up per new position, each ≥ $250;
  - no negative cash;
  - cash and commission reconciliation;
  - equity from 2010-03-01 and first fills on 2010-03-02;
  - the quarterly dates.
