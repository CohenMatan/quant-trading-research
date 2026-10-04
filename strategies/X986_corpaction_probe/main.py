# X986 — infrastructure probe (scratch only, NOT research): does LEAN build 18131 return split / dividend HISTORY,
# and how do RAW / SCALED_RAW / SPLIT_ADJUSTED histories relate? AAPL (7:1 split 2014-06-09), one month.
# Publishes only API behaviour and a few price RATIOS (no raw price levels).
from AlgorithmImports import *
import json
from datetime import datetime
from qr_harness import QRAlgorithm


class Probe(QRAlgorithm):
    FIXED_TICKERS = ("AAPL",)

    def qr_initialize(self):
        self._qr_log_budget = 2000
        self.done = False

    def qr_on_close(self, data):
        if self.done or self.time.date() < datetime(2014, 6, 20).date():
            return
        self.done = True
        a = self.qr_fixed["AAPL"]
        out = {}
        for name, typ in (("split", Split), ("dividend", Dividend)):
            for form in ("list_dates", "period"):
                key = f"{name}_{form}"
                try:
                    if form == "list_dates":
                        h = self.history(typ, [a], datetime(2012, 1, 1), datetime(2014, 6, 19))
                    else:
                        h = self.history(typ, a, timedelta(days=900))
                    rows = []
                    if h is not None and hasattr(h, "iterrows"):
                        for idx, r in h.iterrows():
                            rows.append(str(idx)[:60] + " " + json.dumps({k: str(v)[:20] for k, v in r.items()})[:300])
                    else:
                        for x in list(h)[:40]:
                            rows.append(str(x)[:200])
                    out[key] = {"n": len(rows), "rows": rows[:15]}
                except Exception as e:
                    out[key] = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
        ratios = {}
        try:
            mode = {"raw": DataNormalizationMode.RAW, "scaled": DataNormalizationMode.SCALED_RAW,
                    "split": DataNormalizationMode.SPLIT_ADJUSTED, "adj": DataNormalizationMode.ADJUSTED}
            hs = {k: self.history(a, datetime(2014, 5, 1), datetime(2014, 6, 19), Resolution.DAILY,
                                  data_normalization_mode=m) for k, m in mode.items()}
            c = {k: [float(x) for x in v["close"].values] for k, v in hs.items()}
            for k in c:
                ratios[k + "_n"] = len(c[k])
            for k in ("scaled", "split", "adj"):
                ratios[k + "_over_raw_first"] = c[k][0] / c["raw"][0]
                ratios[k + "_over_raw_last"] = c[k][-1] / c["raw"][-1]
            ratios["raw_jump_max"] = max(abs(c["raw"][i] / c["raw"][i - 1] - 1) for i in range(1, len(c["raw"])))
            ratios["split_jump_max"] = max(abs(c["split"][i] / c["split"][i - 1] - 1) for i in range(1, len(c["split"])))
        except Exception as e:
            ratios["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        out["ratios"] = ratios
        self._qr_log("PROBE|" + json.dumps(out, sort_keys=True))
