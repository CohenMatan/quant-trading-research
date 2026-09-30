# E013-06 incident and the E013-03 status note (C03, 2026-09-30)

## E013-06 (H013 v1.1 seed 3): QuantConnect backtest stuck "In Queue"

- **Submitted:** 16:11:17 UTC. QuantConnect backtest `5c1afc8e56c21718609f6f98bd781082`, project `qr-S013` (37177722), from clean commit `83df333`.
- **What the runner saw.** Every `backtests/read` call for this backtest timed out on QuantConnect's side (120 s per attempt). The runner gave up after its retries and recorded the run as **failed** (`E013-06_runner_output.json`). The queue stopped as designed.
- **Other backtests were unaffected.** The same endpoint answered in 0.7 s for E013-05. General connectivity was normal: 0.2–0.4 s, and the proxy showed no relay failures.
- **QuantConnect state.** `backtests/list` shows the backtest at **"In Queue…", progress 0, not completed**, still at 16:40 UTC. It never started running, so no result exists. It occupies the organisation's only backtest node, so no other backtest can run.
- **Precedent.** E007-16 (C02) stayed "In Queue" indefinitely and was deleted with owner approval (D077).
- **Rule.** A stalled backtest is never deleted without owner approval (CLAUDE.md).
- **Registry.** E013-06 keeps its failed `original` row, plus an annotation. It is a started run, so under D069 it is counted as its configuration's first run. A re-run of the identical configuration is a technical repeat, not a new selection candidate.

## E013-03 (H013 v1.0 seed 3): QuantConnect status "Runtime Error" after completion

- QuantConnect's backtest list shows backtest `f20167ce25ee4d28cf44413e6f5ee8e4` with status **"Runtime Error"**. The error text is `FATAL UNHANDLED EXCEPTION: websocat: ... socket leak`, with no stack trace. `websocat` is a network-relay tool in QuantConnect's own infrastructure, **not our algorithm**.
- **When the runner read the backtest, it was completed with no error.** The download and integrity checks passed.
- **The results are complete:**
  - 2,013 daily equity points from 2010-01-04 to 2017-12-29, the same as the other seeds;
  - 974 orders;
  - every integrity check passed;
  - the harness summary is present. That summary is written in `on_end_of_algorithm`, so it only exists if the algorithm ran to its last day.
- **Conclusion:** the error was attached by QuantConnect's infrastructure after the algorithm had finished. It does not affect the result.
- **Possible link:** a server-side connection problem like this may be related to the E013-06 incident that followed.
