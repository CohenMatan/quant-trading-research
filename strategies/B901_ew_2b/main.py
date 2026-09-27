# B901 — equal-weight benchmark of the whole eligible >= $2B universe, rebalanced monthly.
# On the first close of each month: target weight (1 - buffer) / N for every eligible stock,
# liquidate holdings that are no longer eligible. Orders fill at the next open (harness).
# Optional sharding (params shard_count / shard_index) splits the universe deterministically by
# symbol ID, for use if a single backtest cannot hold the full universe.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import hashlib


def in_shard(symbol_id: str, count: int, index: int) -> bool:
    if count <= 1:
        return True
    return int(hashlib.sha1(symbol_id.encode()).hexdigest(), 16) % count == index


class EqualWeightUniverse(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.last_month = None
        self.count = int(self.qr_params.get("shard_count", 1))
        self.index = int(self.qr_params.get("shard_index", 0))

    def qr_select_universe(self, eligible):
        return [f.symbol for f in eligible if in_shard(str(f.symbol.id), self.count, self.index)]

    def qr_on_close(self, data):
        m = (self.time.year, self.time.month)
        if m == self.last_month:
            return
        self.last_month = m
        members = [s for s in self.qr_eligible
                   if in_shard(str(s.id), self.count, self.index)
                   and self.securities.contains_key(s) and self.securities[s].price > 0]
        if not members:
            return
        w = (1.0 - float(self._qr_pf.get("cash_buffer", 0.02))) / len(members)
        self.qr_rebalance({s: w for s in members}, tag="ew_rebal", liquidate_others=True,
                          band=float(self.qr_params.get("band", 0.25)))
