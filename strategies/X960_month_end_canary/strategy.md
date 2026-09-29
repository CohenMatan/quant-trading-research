# X960: month-end close store canary (infrastructure)

Purpose: prove on QuantConnect that the month-end closes kept for H011 (S011) are correct. It runs on IS dates only (2010–2014), places no orders, is not a strategy and is not a trial.

It checks three things, for 8 long-listed stocks:

1. **Correct values.** At the first session of every month, the stored month-end closes equal those rebuilt from a fresh point-in-time daily history. This covers the AAPL 7:1 split in 2014 and dividends.
2. **No look-ahead.** The store never contains the current month.
3. **Enough history.** At the 2010 start there are at least 120 completed months, enough for the 10-year look-back. Pre-2010 prices are used as signal warm-up only (owner, 2026-09-29).
