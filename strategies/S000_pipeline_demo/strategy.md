# S000 — Pipeline demonstration (NOT research)

**Status:** infrastructure demo for CP2. It has **no hypothesis**, is **not a candidate** and will **not be promoted**. Its results carry no research meaning. It is registered as kind `demo` and counted as a trial for the Deflated Sharpe Ratio, which is the conservative choice.

**Rules (v1.0):**

1. Universe: the harness's eligible ≥ $2B universe. From it, take the 300 most liquid names by point-in-time 20-day average dollar volume.
2. At each close, if slots are free (10 slots), buy the names with the **lowest 5-day return**, based on point-in-time split- and dividend-adjusted closes. Each position gets 9.8% of equity. Orders are market-on-open the next day.
3. Sell each position after it has been held for 5 closes, also market-on-open.
4. Costs, universe filters and cash handling are the harness defaults, as in the experiment config.

**Why this rule:** it exercises every part of the pipeline:

- universe selection;
- adjusted rolling windows;
- a pure signal module (`signals.py`) covered by local look-ahead and determinism tests;
- daily entries and exits;
- cash planning;
- delistings.

**Disclosure:** short-term reversal is a well-known effect in the academic literature. If a future hypothesis resembles this rule, it must disclose that this demo's IS result has already been seen.
