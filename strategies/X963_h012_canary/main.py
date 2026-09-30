# X963 v1.2 — C03 H012 infrastructure canary (infrastructure, not research; not a trial). Runs the
# unchanged S012 algorithm (s012.py and signals.py are byte copies, tested) with NON-candidate parameters
# (RV(10), weekly, 2010-2011) and checks on QuantConnect itself:
#  A. SPY RV(short) and RV(252) from the harness window equal RV from a fresh point-in-time
#     (SCALED_RAW) history at the same close, on every rescale day and on the first close;
#  B. the basket at each reconstitution is the `slots` largest eligible names by the market cap the
#     universe filter itself used, from the selection made for day T (never later);
#  C. orders are placed only on event closes and inside the rebalance window after them; inside the band
#     no rescale is applied (counted in the S012 summary);
#  D. the invested fraction after each completed rebalance, against e x (1 - cash buffer);
#  E. Control B's pre-start targets come only from history before the start date.
# v1.1 (after E963-01 stopped on the 2010-11-26 half-day): a fresh history shorter than the window, or
# not ending at today's bar, is counted and skipped instead of compared. v1.2: S012 forms its basket at the
# first close with eligible names (D083 addendum); days whose selection is not from today are logged.
# Fills at the T+1 open are checked by the harness self-check and the runner (fills_after_signal_date).
from AlgorithmImports import *
import json
import s012
from signals import largest, realized_vol


class H012Canary(s012.VolManaged):

    def qr_initialize(self):
        super().qr_initialize()
        self.sel_day = None
        self.window_open = 0
        self.c = {"rv_checks": 0, "rv_max_rel_dev": 0.0, "rv_mismatches": 0, "last_close_mismatches": 0,
                  "recon_checks": 0, "recon_mismatches": 0, "selection_not_today": 0, "basket_churn": [],
                  "order_days": 0, "orders_outside_window": 0,
                  "invested_checks": 0, "invested_dev": [], "history_targets": self.s12["history_targets"],
                  "history_after_start": 0, "skipped_min_position_end": None}
        if self.s12["history_last_date"] and self.s12["history_last_date"] >= str(self.start_date.date()):
            self.c["history_after_start"] += 1

    def qr_select_universe(self, eligible_fundamentals):
        self.sel_day = self.time.date()
        return super().qr_select_universe(eligible_fundamentals)

    def qr_on_close(self, data):
        today = self.time.date()
        before = dict(self.s12)
        orders_before = self._qr_stats["orders"]
        prev_basket = list(self.basket)
        was_open = self.rebal_left > 0
        super().qr_on_close(data)
        c = self.c
        recon = self.s12["reconstitutions"] > before["reconstitutions"]
        applied = self.s12["rescales_applied"] > before["rescales_applied"]
        first = before["e_days"] == 0
        if recon:
            c["recon_checks"] += 1
            caps = {str(s.id): cap for s, (cap, _) in self.qr_eligible_info.items()}
            ref = largest(caps, self.slots)
            if [str(s.id) for s in self.basket] != ref:
                c["recon_mismatches"] += 1
            if self.sel_day != today:
                c["selection_not_today"] += 1
                self._qr_log(f"QRC63|selection_not_today|{today}|{self.sel_day}")
            c["basket_churn"].append([str(today), len(set(map(str, self.basket)) - set(map(str, prev_basket)))])
        if self.s12["rescale_days"] > before["rescale_days"] or first:
            self._check_rv(today)
        placed = self._qr_stats["orders"] - orders_before
        if placed:
            c["order_days"] += 1
            if not (recon or applied or first or was_open):
                c["orders_outside_window"] += 1
        if was_open and self.rebal_left == 0 and not (recon or applied):
            pv = float(self.portfolio.total_portfolio_value)
            inv = float(self.portfolio.total_holdings_value) / pv if pv > 0 else 0.0
            c["invested_checks"] += 1
            c["invested_dev"].append(round(inv - self.e_cur * (1 - float(self._qr_pf.get("cash_buffer", 0.02))), 4))

    def _check_rv(self, today):
        w = list(self.qr_close.get(self.spy) or [])
        hist = self.history(self.spy, self.long + 1, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty or len(w) < self.long + 1:
            return
        fresh = [float(x) for x in hist["close"].values]
        last = hist.index[-1][-1] if isinstance(hist.index[-1], tuple) else hist.index[-1]
        if len(fresh) < self.long + 1 or last.date() != today:
            self.c["fresh_skipped"] = self.c.get("fresh_skipped", 0) + 1
            self._qr_log(f"QRC63|fresh_skipped|{today}|{len(fresh)}|{last}")
            return
        self.c["rv_checks"] += 1
        if abs(fresh[-1] / w[-1] - 1) > 1e-3:
            self.c["last_close_mismatches"] += 1
        for n in (self.short, self.long):
            a, b = realized_vol(w, n), realized_vol(fresh, n)
            dev = abs(a / b - 1)
            self.c["rv_max_rel_dev"] = max(self.c["rv_max_rel_dev"], dev)
            if dev > 1e-3:
                self.c["rv_mismatches"] += 1
                self._qr_log(f"QRC63|rv_mismatch|{today}|{n}|{a:.8f}|{b:.8f}")

    def qr_on_end(self):
        super().qr_on_end()
        d = self.c.pop("invested_dev")
        self.c["invested_dev_n"] = len(d)
        self.c["invested_dev_min"] = min(d) if d else None
        self.c["invested_dev_max"] = max(d) if d else None
        self.c["invested_dev_mean"] = sum(d) / len(d) if d else None
        self.c["skipped_min_position_end"] = self._qr_stats.get("skipped_min_position", 0)
        self._qr_log("QRC63|summary|" + json.dumps(self.c, sort_keys=True, default=str))
