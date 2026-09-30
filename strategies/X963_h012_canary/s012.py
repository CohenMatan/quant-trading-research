# S012 — H012 volatility-managed exposure (C03; research/hypotheses/H012.md, frozen before any C03 result).
# Basket: the `slots` largest eligible stocks by point-in-time Morningstar market cap (the universe
# filter's own value on day T; ties by security id), reconstituted at the first session of each quarter,
# equal weight. Exposure: on the last session of each month (or ISO week), target
# e = min(1, RV(252)/RV(short)) of SPY (indicator only, never traded); applied only if |e - applied| > band.
# Modes (same basket, reconstitution and execution): "timing" = the hypothesis; "control_a" = e = 1
# always; "control_b" = e = mean of the variation's own targets on the previous 12 rescale dates.
# Execution (D083): on an event close (first close, reconstitution, applied rescale) every basket name
# is targeted at e x slot weight and every other holding at 0, as next-open orders through the harness
# (D051 cash rules, $7/order, 10 bps slippage). Because D051 buys only from settled cash, the same
# targets are re-submitted at the next closes (at most REBAL_SESSIONS in all) until nothing is left to
# trade; residual differences below RESIDUAL_BAND of a position's target are not traded.
from AlgorithmImports import *
from datetime import timedelta
from qr_harness import QRAlgorithm
from signals import (band_exceeded, control_b, exposure_target, history_targets, is_reconstitution,
                     is_rescale_day, largest)

HIST_BARS = 600          # SPY history: RV(252) plus 12 monthly rescale dates before the start
REBAL_SESSIONS = 5
RESIDUAL_BAND = 0.05
CONTROL_B_K = 12


class VolManaged(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = HIST_BARS

    def qr_initialize(self):
        p = self.qr_params
        self.mode = p.get("mode", "timing")
        self.short, self.long = int(p["rv_short"]), int(p.get("rv_long", 252))
        self.cadence, self.band, self.slots = p["cadence"], float(p["band"]), int(p["slots"])
        if self.mode not in ("timing", "control_a", "control_b"):
            raise Exception(f"unknown mode {self.mode}")
        self.e_cur = None
        self.basket = []
        self.prev_month = None
        self.rebal_left = 0
        self.s12 = {"reconstitutions": 0, "rescale_days": 0, "rescales_applied": 0, "rescales_in_band": 0,
                    "target_missing": 0, "rebalance_closes": 0, "basket_missing_price": 0, "e_sum": 0.0,
                    "e_days": 0, "e_min": 1.0}
        # the variation's targets on past rescale dates, from point-in-time SPY history before the start
        hist = self.history(self.spy, HIST_BARS, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        dates, closes = [], []
        if hist is not None and not hist.empty:
            for idx, c in hist["close"].items():
                t = idx[-1] if isinstance(idx, tuple) else idx
                d = (t - timedelta(days=1)).date() if t.hour == 0 else t.date()
                if d < self.start_date.date():
                    dates.append(d)
                    closes.append(float(c))
        first_session = self.securities[self.spy].exchange.hours.get_next_market_open(
            self.start_date - timedelta(seconds=1), False).date()
        self.targets = [e for _, e in history_targets(dates, closes, self.short, self.cadence, first_session,
                                                       self.long)]
        self.s12["history_targets"] = len(self.targets)
        self.s12["history_last_date"] = str(dates[-1]) if dates else None

    def qr_select_universe(self, eligible_fundamentals):
        """Subscribe only the 2 x slots largest eligible names (the basket always comes from these)."""
        caps = {str(f.symbol.id): f for f in eligible_fundamentals}
        top = largest({k: float(f.market_cap) for k, f in caps.items()}, 2 * self.slots)
        return [caps[k].symbol for k in top]

    def _new_exposure(self, target):
        if self.mode == "control_a":
            return 1.0
        if self.mode == "control_b":
            b = control_b(self.targets, CONTROL_B_K)
            return 1.0 if b is None else b
        return target

    def qr_on_close(self, data):
        today = self.time.date()
        event = False
        if is_reconstitution(self.prev_month, today.month):
            info = {str(s.id): (s, cap) for s, (cap, _) in self.qr_eligible_info.items()}
            self.basket = [info[k][0] for k in largest({k: v[1] for k, v in info.items()}, self.slots)]
            self.s12["reconstitutions"] += 1
            event = True
        self.prev_month = today.month
        spy = self.qr_close.get(self.spy) or []
        target = exposure_target(spy, self.short, self.long)
        nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
        rescale_day = is_rescale_day(today, nxt, self.cadence)
        if self.e_cur is None:                           # first close: start at the mode's exposure
            if target is None:
                self.s12["target_missing"] += 1
            self.e_cur = self._new_exposure(1.0 if target is None else target)
            event = True
        elif rescale_day:
            self.s12["rescale_days"] += 1
            if target is None:
                self.s12["target_missing"] += 1
            else:
                e_new = self._new_exposure(target)
                if band_exceeded(e_new, self.e_cur, self.band):
                    self.e_cur = e_new
                    self.s12["rescales_applied"] += 1
                    event = True
                else:
                    self.s12["rescales_in_band"] += 1
        if rescale_day and target is not None:
            self.targets.append(target)                  # after Control B used the previous ones only
            self._qr_log(f"QRS012|e|{today}|{target:.6f}|{self.e_cur:.6f}")   # rescale day: target, applied
        if event:
            self.rebal_left = REBAL_SESSIONS
        if self.rebal_left > 0:
            self.rebal_left -= 1
            self.s12["rebalance_closes"] += 1
            w = self.e_cur * self.qr_slot_weight(self.slots)
            tg = {}
            for s in self.basket:
                if self.securities.contains_key(s) and float(self.securities[s].price) > 0:
                    tg[s] = w
                else:
                    self.s12["basket_missing_price"] += 1
            if self.qr_rebalance(tg, tag="s012", liquidate_others=True, band=RESIDUAL_BAND) == 0:
                self.rebal_left = 0
        self.s12["e_sum"] += self.e_cur
        self.s12["e_days"] += 1
        self.s12["e_min"] = min(self.s12["e_min"], self.e_cur)

    def qr_on_end(self):
        import json
        s = dict(self.s12, e_mean=self.s12["e_sum"] / max(self.s12["e_days"], 1))
        self._qr_log("QRS012|summary|" + json.dumps(s, sort_keys=True, default=str))
