# S014: trend + pullback + confirmed recovery (H014, Phase 2)

- **Rules:** frozen in `research/phase2/P2_spec.md` §3–§5 (D094). This file only describes the code.
- **Code:**
  - `signals.py`: pure numpy functions (features, RSI14, entry masks, ranking, exit decision), unit-tested offline in `tests/test_p2_s014.py`.
  - `main.py`: the LEAN algorithm.
  - `nullorder.py`: a byte copy of X962's `signals.py` (the seeded random order).

| Version | Exit |
|---|---|
| v1.0 | Candidate A: MA200 break, or 63 sessions with horizon roll |
| v1.1 | Candidate B: MA200 break, or 126-session cap |

The book is chosen by params:

| `mode` | Book |
|---|---|
| `h014` | The strategy |
| `c1` | Trend-only control |
| `c2` | Pullback-without-recovery control |
| `rand` | Random-uptrend control (`seed`) |

The other params:
- `exit` (`A`/`B`) and `limit` (A: horizon; B: cap);
- `slots`;
- `rsi_pullback`, `window` and `rsi_recovery`.

**Data:** 259 adjusted daily OHLC bars per subscribed stock (`USES_OHLC`), loaded point in time and rescaled on splits and dividends by the harness.

**Summary line:** `QRS014|summary|{...}`. It holds:
- closes;
- candidates and signals per day;
- exits by reason;
- rolls;
- integrity counters (`held_short_window` and `held_no_entry` must be 0).
