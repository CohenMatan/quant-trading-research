# X958: D063 end-to-end canary (infrastructure)

Purpose: prove the full QuantConnect path for D063, following the steps below. Every 5th cycle it also deletes the history after the fill to exercise the daily safety net.

1. A stock is selected at the close.
2. It leaves the universe overnight while its next-open buy is pending.
3. The buy still fills.
4. The price history survives.
5. A time-exit rule that reads the history sells after 3 closes.

It places no strategy research trades and is not a trial.
