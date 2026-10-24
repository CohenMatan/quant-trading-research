# Observation protocol — TT chart discovery (D302, Stage 3)

Written before any chart was rendered; committed before any chart was viewed.

**Order.** Charts are viewed in chart-id order (C001, C002, …). Ids come from a seeded shuffle, so their order carries no year, size, exit or behaviour information.
- **Pilot:** C001–C024.
- **Main pass:** continues to the last chart if the pilot shows the workflow is sound: images legible, no visible leakage, vocabulary usable.
- **No skipping.** Every chart viewed gets a record, including "no clear pattern".

**Blindness.**
- While observing, the analyst (Claude) never opens `data/chart_discovery/sample_mapping.json` and never sees a ticker, date, price level, stratum or outcome.
- Charts show only bars up to the decision date. The decision bar is the last candle, followed by a blank margin.
- No forward return, outcome or later price is computed for any chart in this stage, by any code. **Stage 3 has no outcome data at all.**

**Record.** One JSON line per chart in `observations.jsonl`, using a fixed vocabulary. The vocabulary may be extended only after the pilot, and only by adding values; every addition is listed in the checkpoint.

| Field | Values |
|---|---|
| `trend_252` | the whole visible year: `UP`, `DOWN`, `SIDEWAYS`, `V_UP` (fall then recovery), `INV_V` (rise then fall) |
| `trend_recent` | about the last 40 bars: `UP`, `DOWN`, `FLAT` |
| `location` | decision close within the visible year's range: `AT_HIGH` (within a few % of the high), `UPPER`, `MIDDLE`, `LOWER`, `AT_LOW` |
| `ma_state` | MA50 (blue) / MA200 (purple), where drawn: `ABOVE_BOTH`, `BETWEEN`, `BELOW_BOTH`, `NA` (MA200 not drawn) |
| `ma_slope` | `BOTH_RISING`, `BOTH_FALLING`, `MIXED`, `FLAT`, `NA` |
| `vol_regime` | price range of the last ~40 bars vs earlier: `CONTRACTING`, `EXPANDING`, `STABLE` |
| `volume` | last ~40 bars vs earlier: `RISING`, `FALLING`, `STABLE`, `RECENT_SPIKE` |
| `gaps` | visible large single-bar jumps: `NONE`, `UP_GAP`, `DOWN_GAP`, `BOTH` |
| `setup` | one primary structure at the decision point: `BREAKOUT_FROM_BASE`, `TIGHT_RANGE_NEAR_HIGH`, `PULLBACK_IN_UPTREND`, `EXTENDED_RUN`, `STEADY_UPTREND`, `GAP_AND_HOLD`, `BREAKDOWN`, `DOWNTREND`, `BASE_AFTER_DECLINE`, `RANGE_BOUND`, `RECOVERY_ATTEMPT`, `NONE` |
| `clarity` | `CLEAR`, `WEAK`, `NONE` (no recognisable structure) |
| `notes` | short free text describing what is visible |

**Pattern proposals** come only from recurring observations across charts. For each one, the checkpoint states:
- how many charts showed it, and which ones (by id);
- when during viewing it was first noticed.

Selecting or ranking patterns cannot use outcomes, because no outcome data exist in this stage.
