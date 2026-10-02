# X978 v1.0 — identity fingerprints for the identity v2 links found after the 2020-2021 RSS fix (D113a; contradiction check) (infrastructure; NO orders, no rankings, no returns; D111).
# For candidate (SEC registrant, QuantConnect security without fundamentals) pairs not covered by X971 — registrants
# whose equity was still listed after 2021 and securities that outlived a registrant (holding-company successions) —
# pre-filtered offline by the strict ticker-name rule: SEC public float / (SEC cover shares x raw close at the float
# date). Outputs ratios and identifiers only.
from AlgorithmImports import *
import json
from datetime import date
from qr_harness import QRAlgorithm
from fp_ref import load_table


class IdentityFingerprints(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 100000
        t = load_table()
        self.float_obs = t["float_obs"]
        self.pairs = t["pairs"]
        self.queue = sorted((date.fromisoformat(o[0]), cik, i) for cik, obs in self.float_obs.items()
                            for i, o in enumerate(obs))
        self.qi = 0
        self.stats = {}
        self.n_eval = 0

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        if not (self.qi < len(self.queue) and self.queue[self.qi][0] < today):
            return []
        by_sid = {str(f.symbol.id): f for f in fl}
        while self.qi < len(self.queue) and self.queue[self.qi][0] < today:
            fdate, cik, i = self.queue[self.qi]
            self.qi += 1
            if (today - fdate).days > 5:
                continue
            _, flt, shares, _sd = self.float_obs[cik][i]
            if not shares or shares <= 0 or not flt or flt <= 0:
                continue
            for sid in self.pairs.get(cik, ()):
                f = by_sid.get(sid)
                if f is None or float(f.price) <= 0:
                    continue
                st = self.stats.setdefault((cik, sid), [])
                st.append(round(flt / (shares * float(f.price)), 3))
                self.n_eval += 1
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        for (cik, sid), rs in sorted(self.stats.items()):
            self._qr_log(f"P|{cik}|{sid}|{len(rs)}|{sum(1 for r in rs if 0.45 <= r <= 1.30)}|{','.join(str(r) for r in rs)}")
        self._qr_log("C|" + json.dumps({"evaluations": self.n_eval, "pairs": len(self.stats)}))
