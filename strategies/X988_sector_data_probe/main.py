# X988 — Phase 6 sector-ETF DATA AVAILABILITY probe (P6-CP1; infrastructure, NOT research). For each candidate sector
# ETF / index ETF: first and last daily bar in QuantConnect (history requested 1998-01-01 .. 2017-12-31 only), bars,
# sessions missing against SPY's calendar after the first bar, zero-volume days, median daily dollar volume per year,
# and the dates and sizes of split / large-distribution events. Publishes NO return, NO ranking, NO price level.
from AlgorithmImports import *
import json
from datetime import datetime
import numpy as np
from qr_harness import QRAlgorithm
import qr_xs_panel as XP

H0, H1 = datetime(1998, 1, 1), datetime(2017, 12, 31)
LAST = np.datetime64("2017-12-29").astype(np.int64)
TICKERS = ("SPY",
           "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XLRE", "XLC",        # Select Sector SPDRs
           "IYM", "IYE", "IYF", "IYJ", "IYW", "IYK", "IDU", "IYH", "IYC", "IYZ", "IYR",          # iShares US sector
           "VAW", "VDE", "VFH", "VIS", "VGT", "VDC", "VPU", "VHT", "VCR", "VOX", "VNQ")          # Vanguard sector


class SectorProbe(QRAlgorithm):
    def qr_initialize(self):
        self._qr_log_budget = 2000
        if self.qr["end"] > "2017-12-31":
            raise Exception("X988: probe ends on or before 2017-12-31")

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        out = {}
        spy = None
        for tk in TICKERS:
            rec = {}
            try:
                sym = Symbol.create(tk, SecurityType.EQUITY, Market.USA)
                h = self.history([sym], H0, H1, Resolution.DAILY, fill_forward=False,
                                 data_normalization_mode=DataNormalizationMode.RAW)
                if h is None or h.empty:
                    rec["bars"] = 0
                else:
                    days = XP.session_days(h.index.get_level_values(-1).values)
                    if (days > LAST).any():
                        raise Exception("history after 2017-12-29")
                    c = h["close"].to_numpy(float)
                    v = h["volume"].to_numpy(float) if "volume" in h.columns else np.full(c.size, np.nan)
                    if tk == "SPY":
                        spy = days
                    rec.update(bars=int(days.size), first=str(np.datetime64(int(days[0]), "D")),
                               last=str(np.datetime64(int(days[-1]), "D")),
                               zero_volume_days=int(np.sum(v == 0)), nan_close=int(np.sum(~np.isfinite(c))))
                    if spy is not None:
                        cal = spy[spy >= days[0]]
                        rec["missing_sessions_vs_spy"] = int(np.setdiff1d(cal, days).size)
                        gaps = np.diff(np.searchsorted(cal, days))
                        rec["max_consecutive_missing"] = int(max(0, gaps.max() - 1)) if gaps.size else 0
                    yrs = np.datetime64(0, "D") + days.astype("timedelta64[D]")
                    yr = yrs.astype("datetime64[Y]").astype(int) + 1970
                    dv = c * v
                    rec["median_dollar_volume_musd_by_year"] = {
                        str(y): round(float(np.nanmedian(dv[yr == y])) / 1e6, 3) for y in sorted(set(yr.tolist()))}
                sp = self.history(Split, [sym], H0, H1)
                dv_ = self.history(Dividend, [sym], H0, H1)
                ev = []
                if sp is not None and not sp.empty:
                    ed = XP.event_days(sp.index.get_level_values(-1).values)
                    for e, typ, fac in zip(ed, sp["type"].tolist(), sp["splitfactor"].tolist()):
                        ev.append([str(np.datetime64(int(e), "D")), str(typ)[:12], round(float(fac), 6)])
                rec["split_events"] = ev
                big, n = [], 0
                if dv_ is not None and not dv_.empty:
                    ed = XP.event_days(dv_.index.get_level_values(-1).values)
                    for e, amt, ref in zip(ed, dv_["distribution"].tolist(), dv_["referenceprice"].tolist()):
                        n += 1
                        if float(ref) > 0 and float(amt) / float(ref) > 0.05:
                            big.append([str(np.datetime64(int(e), "D")), round(float(amt) / float(ref), 4)])
                rec["distribution_events"] = n
                rec["large_distributions_over_5pct"] = big
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            out[tk] = rec
        self._qr_log("P6PROBE|" + json.dumps(out, sort_keys=True))
