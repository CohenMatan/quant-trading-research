# X966 v1.1 — window diagnostic after E965-04 (infrastructure, not research; places NO orders). Keeps the
from qr_harness import QRAlgorithm
# harness's 259-bar adjusted OHLC windows exactly as S014 does, and additionally records the DATE of every
# bar in each close window. Every AUDIT_EVERY sessions, for a sample of eligible names, it compares the live
# window with a fresh point-in-time (SCALED_RAW) history of the same length, bar by bar:
#   date alignment (missing / extra / filled-forward bars) and, on aligned dates, the price ratio live/fresh.
# Mismatches are logged (QRD66|...) with the pattern, so the cause of the E965-04 feature differences
# (dividend rescaling vs bar alignment) can be identified.
# v1.1 (E966-01 diagnostic defect): today's date is recorded at the start of the close hook (v1.0 recorded it
# after the hook, so every comparison was shifted by one bar); also compares by position.
from AlgorithmImports import *
from collections import deque
import json

WINDOW, AUDIT_EVERY, SAMPLE, MAX_LOG = 259, 10, 25, 400


class WindowDiag(QRAlgorithm):
    USES_UNIVERSE = True
    USES_OHLC = True
    WINDOW_BARS = WINDOW

    def qr_initialize(self):
        self.dates = {}
        self.ff = {}
        self.d = {"audits": 0, "checks": 0, "exact": 0, "dates_differ": 0, "prices_differ_aligned": 0,
                  "fresh_short": 0, "logged": 0, "ff_bars_in_window": 0, "div_events": 0, "split_events": 0,
                  "ratio_hist": {}}

    def _qr_load_windows(self, symbols):
        super()._qr_load_windows(symbols)
        if not symbols:
            return
        hist = self.history(symbols, self.WINDOW_BARS, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        for s in symbols:
            self.dates[s] = deque(maxlen=self.WINDOW_BARS)
            self.ff[s] = deque(maxlen=self.WINDOW_BARS)
        if hist is None or hist.empty:
            return
        for (s, t) in hist.index:
            if s in self.dates:
                self.dates[s].append(t.date())
                self.ff[s].append(False)

    def on_data(self, data):
        for s in data.dividends.keys():
            self.d["div_events"] += 1
        for s in data.splits.keys():
            self.d["split_events"] += 1
        super().on_data(data)

    def qr_on_close(self, data):
        today = self.time.date()
        for s, dq in self.dates.items():
            if self._qr_last_bar.get(s) == today and (not len(dq) or dq[-1] != today) and s in self.qr_close:
                dq.append(today)
                self.ff[s].append(bool(data.bars.contains_key(s) and data.bars[s].is_fill_forward))
        if self._qr_session % AUDIT_EVERY:
            return
        cands = [s for s in self.qr_eligible if s in self.qr_close and len(self.qr_close[s]) >= WINDOW
                 and data.bars.contains_key(s) and not data.bars[s].is_fill_forward]
        if not cands:
            return
        self.d["audits"] += 1
        syms = cands[::max(1, len(cands) // SAMPLE)][:SAMPLE]
        hist = self.history(syms, WINDOW, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        for s in syms:
            try:
                h = hist.loc[s]
            except KeyError:
                continue
            fd = [t.date() for t in h.index]
            if len(fd) < WINDOW or fd[-1] != today:
                self.d["fresh_short"] += 1
                continue
            fc = [float(x) for x in h["close"].values]
            lc = list(self.qr_close[s])
            ld = list(self.dates.get(s, []))
            nff = sum(1 for x in self.ff.get(s, []) if x)
            self.d["ff_bars_in_window"] += nff
            self.d["checks"] += 1
            if ld != fd:
                self.d["dates_differ"] += 1
                miss = sorted(set(fd) - set(ld))[:5]
                extra = sorted(set(ld) - set(fd))[:5]
                self._log(f"QRD66|dates|{today}|{s.id}|len={len(ld)}|ff={nff}|missing={miss}|extra={extra}"
                          f"|first_live={ld[0] if ld else None}|first_fresh={fd[0]}")
            n = min(len(lc), len(fc))
            pos_bad = [i for i in range(1, n + 1) if abs(lc[-i] / fc[-i] - 1) > 1e-6]
            self.d["positional_bad"] = self.d.get("positional_bad", 0) + int(bool(pos_bad))
            if pos_bad:
                self._log(f"QRD66|pos|{today}|{s.id}|nbad={len(pos_bad)}|first_back={pos_bad[0]}|last_back={pos_bad[-1]}"
                          f"|ratio_oldest={lc[-n] / fc[-n]:.6f}|ratio_at_first={lc[-pos_bad[0]] / fc[-pos_bad[0]]:.6f}")
            common = {d: i for i, d in enumerate(fd)}
            ratios = [(d, lc[i] / fc[common[d]]) for i, d in enumerate(ld) if d in common and i < len(lc)]
            bad = [(d, r) for d, r in ratios if abs(r - 1) > 1e-6]
            if not bad and ld == fd:
                self.d["exact"] += 1
            elif bad:
                self.d["prices_differ_aligned"] += 1
                steps = []
                prev = None
                for d, r in ratios:
                    if prev is None or abs(r - prev) > 1e-7:
                        steps.append(f"{d}:{r:.6f}")
                    prev = r
                self._log(f"QRD66|ratio|{today}|{s.id}|nbad={len(bad)}|steps={steps[:8]}")
                k = "%.4f" % bad[0][1]
                self.d["ratio_hist"][k] = self.d["ratio_hist"].get(k, 0) + 1

    def _log(self, line):
        if self.d["logged"] < MAX_LOG:
            self.d["logged"] += 1
            self._qr_log(line)

    def qr_on_end(self):
        self._qr_log("QRD66|summary|" + json.dumps(self.d, sort_keys=True, default=str))
