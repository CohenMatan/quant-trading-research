# X990 — dividend-feed precision probe (H021-A canary follow-up, D162; infrastructure, NOT research). For the nine
# Select Sector SPDRs + SPY, history 1998-12-01 .. 2017-12-31 only: at every distribution in QuantConnect's dividend
# feed, the amount implied by QuantConnect's own ADJUSTED series, a_imp = ref x (1 - (R_b / R_prev) / (A_b / A_prev))
# (A = ADJUSTED close, R = RAW close, b = ex-row, prev = previous bar), is compared with the feed's amount. Publishes
# only aggregate statistics of these differences (no price, no amount, no return).
from AlgorithmImports import *
import json
from datetime import datetime
import numpy as np
from qr_harness import QRAlgorithm
import qr_xs_panel as XP

H0, H1 = datetime(1998, 12, 1), datetime(2017, 12, 31)
LAST = np.datetime64("2017-12-29").astype(np.int64)
TICKERS = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "SPY")


class DividendPrecisionProbe(QRAlgorithm):
    def qr_initialize(self):
        self._qr_log_budget = 100
        if self.qr["end"] > "2017-12-31":
            raise Exception("X990: probe ends on or before 2017-12-31")

    def qr_select_universe(self, eligible):
        return []

    def _close(self, sym, mode):
        h = self.history([sym], H0, H1, Resolution.DAILY, fill_forward=False, data_normalization_mode=mode)
        d = XP.session_days(h.index.get_level_values(-1).values)
        keep = d <= LAST
        return d[keep], h["close"].to_numpy(float)[keep]

    def qr_on_end(self):
        out = {}
        for tk in TICKERS:
            rec = {}
            try:
                sym = Symbol.create(tk, SecurityType.EQUITY, Market.USA)
                dr, raw = self._close(sym, DataNormalizationMode.RAW)
                da, adj = self._close(sym, DataNormalizationMode.ADJUSTED)
                if not np.array_equal(dr, da):
                    raise Exception("RAW and ADJUSTED sessions differ")
                dv = self.history(Dividend, [sym], H0, H1)
                ed = XP.event_days(dv.index.get_level_values(-1).values)
                diffs, cents, rel, ref_prev = [], 0, [], 0
                n = 0
                for e, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                    if e > LAST:
                        continue
                    b = int(np.searchsorted(dr, e))
                    if b <= 0 or b >= dr.size:
                        continue
                    n += 1
                    amt, ref = float(amt), float(ref)
                    cents += int(abs(round(amt * 100) - amt * 100) < 1e-6)
                    ref_prev += int(abs(ref / raw[b - 1] - 1) < 1e-6)
                    a_imp = ref * (1.0 - (raw[b] / raw[b - 1]) / (adj[b] / adj[b - 1]))     # d = raw step / adjusted step
                    diffs.append(a_imp - amt)
                    rel.append(abs(a_imp - amt) / ref)
                d = np.abs(np.array(diffs))
                rec = dict(distributions=n, amounts_whole_cents=cents, reference_is_previous_raw_close=ref_prev,
                           implied_minus_feed_max_abs_usd=float(d.max()),
                           implied_minus_feed_median_abs_usd=float(np.median(d)),
                           within_half_cent=int(np.sum(d <= 0.005 + 1e-6)),
                           within_1e_4_usd=int(np.sum(d <= 1e-4)),
                           max_relative_to_reference=float(max(rel)))
            except Exception as ex:
                rec["error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
            out[tk] = rec
        self._qr_log("P6DIVPREC|" + json.dumps(out, sort_keys=True))
