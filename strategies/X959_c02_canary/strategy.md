# X959: C02 infrastructure canary (infrastructure)

Purpose: prove on QuantConnect that the harness features added for C02 work end to end. It runs on IS dates only (2014), is not a strategy and is not a trial.

It checks four things:

1. **OHLC windows.** The open/high/low/close/volume histories kept by the harness equal a fresh point-in-time history from QuantConnect. This includes the AAPL 7:1 split on 2014-06-09 and dividends.
2. **Signal timing.** A toy gap signal (gap ≥ 3% that closes at or above its open) can only be computed after day T closes. Its buy must fill at the T+1 open (harness self-check and the runner's `fills_after_signal_date` check).
3. **Entry bookkeeping.** "Sessions held" is 0 at the close of the fill day. The gap day's low read back from the history equals the low seen at the signal.
4. **Month-end calendar.** `qr_is_last_session_of_month` flags exactly the last session of each month.

The pass criteria are listed in the experiment report.
