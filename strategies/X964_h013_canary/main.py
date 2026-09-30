# X964 v1.0 — C03 H013 infrastructure canary (infrastructure, not research; not a trial). Runs the
# unchanged S013 algorithm (s013.py, signals.py and nullorder.py are byte copies, tested) with the
# NON-candidate setting q = 0 (nothing excluded) and otherwise the settings of the null run E962-22
# (seed 1, 15 slots, hold 60, $100K, IS). Its fills must equal E962-22's exactly: S013's order is
# the null's order. Every AUDIT_EVERY sessions it also audits, without trading on it, the exclusion
# at the non-candidate level q = 0.25 for MAX and MAX5:
#  A. MAX/MAX5 from the harness windows equal those from a fresh point-in-time (SCALED_RAW) history
#     (sample of names), and each window ends at today's bar (no look-ahead, no stale data);
#  B. the excluded set has floor(q x n) names, all at or above every non-excluded value, and never
#     a name with fewer than 21 returns;
#  C. the allowed order is the null's order with exactly the excluded names removed.
from AlgorithmImports import *
import json
import math
import s013
from nullorder import pick_order
from signals import WINDOW, allowed_order, excluded_ids, lottery_stat

AUDIT_EVERY, AUDIT_Q, SAMPLE = 10, 0.25, 25


class H013Canary(s013.LotteryAvoid):

    def qr_initialize(self):
        super().qr_initialize()
        self.c = {"audits": 0, "max_checks": 0, "max_mismatches": 0, "max_abs_dev": 0.0,
                  "window_not_today": 0, "count_errors": 0, "order_errors": 0, "short_excluded": 0,
                  "pairing_errors": 0, "excluded_mean": {}, "short_windows": 0}

    def qr_on_close(self, data):
        super().qr_on_close(data)
        if self._qr_session % AUDIT_EVERY:
            return
        c = self.c
        c["audits"] += 1
        today = self.time.date()
        windows = {str(s.id): self.qr_close[s] for s in self.qr_eligible if s in self.qr_close}
        cands = [str(s.id) for s in self.qr_eligible
                 if data.bars.contains_key(s) and not data.bars[s].is_fill_forward]
        null = pick_order(cands, int(self.qr_params["seed"]), self._qr_session)
        for stat in ("max", "max5"):
            vals = {k: lottery_stat(w, stat) for k, w in windows.items()}
            have = {k: v for k, v in vals.items() if v is not None}
            c["short_windows"] = max(c["short_windows"], len(vals) - len(have))
            ex = excluded_ids(windows, AUDIT_Q, stat)
            c["excluded_mean"][stat] = c["excluded_mean"].get(stat, 0) + len(ex)
            if len(ex) != int(math.floor(AUDIT_Q * len(have) + 1e-9)):
                c["count_errors"] += 1
            if ex - set(have):
                c["short_excluded"] += 1
            rest = [v for k, v in have.items() if k not in ex]
            if ex and rest and min(have[k] for k in ex) < max(rest):
                c["order_errors"] += 1
            allowed = allowed_order(null, ex)
            if allowed != [k for k in null if k not in ex] or set(null) - set(allowed) != ex & set(null):
                c["pairing_errors"] += 1
        by_id = {str(s.id): s for s in self.qr_eligible}
        sample = sorted(cands)[::max(1, len(cands) // SAMPLE)][:SAMPLE]
        syms = [by_id[k] for k in sample]
        hist = self.history(syms, WINDOW + 1, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        for s in syms:
            if self._qr_last_bar.get(s) != today:
                c["window_not_today"] += 1
            try:
                fresh = [float(x) for x in hist.loc[s]["close"].values]
            except KeyError:
                continue
            for stat in ("max", "max5"):
                a, b = lottery_stat(self.qr_close[s], stat), lottery_stat(fresh, stat)
                if a is None or b is None:
                    continue
                c["max_checks"] += 1
                dev = abs(a - b)
                c["max_abs_dev"] = max(c["max_abs_dev"], dev)
                if dev > 5e-4:
                    c["max_mismatches"] += 1
                    if c["max_mismatches"] <= 50:
                        self._qr_log(f"QRC64|max_mismatch|{today}|{s.value}|{stat}|{a:.8f}|{b:.8f}")

    def qr_on_end(self):
        super().qr_on_end()
        a = max(self.c["audits"], 1)
        self.c["excluded_mean"] = {k: v / a for k, v in self.c["excluded_mean"].items()}
        self._qr_log("QRC64|summary|" + json.dumps(self.c, sort_keys=True, default=str))
