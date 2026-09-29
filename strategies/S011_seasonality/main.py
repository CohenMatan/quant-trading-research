# S011 — same-calendar-month return seasonality (H011). Variations differ only in params.
# At the last session of month t-1 (LEAN exchange calendar), rank eligible stocks by their average
# return in calendar month t over the previous L years (completed month-end closes only), buy the
# top N at the next open (the first session of month t), hold the month; free slots are refilled
# daily from the current ranking (C02 plan). Pre-2010 prices are read only as signal look-back
# (owner approval 2026-09-29); universe eligibility and evaluation start in 2010.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from qr_indicators import sma
from signals import next_month, seasonal_score


class Seasonality(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 210           # SMA200 for v1.2
    MONTHLY_BARS = 12 * 10 + 14 # enough completed months for L = 10

    def qr_initialize(self):
        self.ranked = []
        self.rank_month = None

    def qr_on_close(self, data):
        p = self.qr_params
        held = [kv.key for kv in self.portfolio if kv.value.invested]
        exits = []
        if self.qr_is_last_session_of_month():
            y, m = next_month(self.time.year, self.time.month)
            scores = {}
            for s in self.qr_eligible:
                mc = self.qr_month_close.get(s)
                if mc is None or not data.bars.contains_key(s):
                    continue
                if p.get("trend_filter"):
                    c = self.qr_close.get(s)
                    t = sma(c, 200) if c is not None else None
                    if t is None or not list(c)[-1] > t:
                        continue
                v = seasonal_score(mc, y, m, int(p["lags"]))
                if v is not None:
                    scores[str(s.id)] = (v, s)
            self.ranked = [scores[k][1] for k in sorted(scores, key=lambda k: (-scores[k][0], k))]
            self.rank_month = (y, m)
            top = set(self.ranked[: int(p["slots"])])
            exits = [s for s in held if s not in top]
        cands = [s for s in self.ranked if s in self.qr_month_close]   # highest-ranked not held first
        self.qr_event_step(exits, cands, int(p["slots"]), tag="s011")
