# X966: window diagnostic (infrastructure)

- **Purpose:** find the cause of the E965-04 feature mismatches between the harness's rolling windows and fresh point-in-time history.
- **What it does:** places no orders and records each bar's date in the windows.
- **How it compares:** bar by bar, logging `QRD66|dates|...` and `QRD66|ratio|...` lines.
- **Status:** not research and not a trial.
