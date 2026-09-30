# X965 v1.0 — Phase 2 H014 infrastructure canary (infrastructure, not research; not a trial). Runs the
# unchanged S014 algorithm (s014.py, signals.py and nullorder.py are byte copies, tested) with NON-candidate
# parameters on 2010-2012 and checks on QuantConnect itself:
#  A. features (close, MA50, MA200, RSI14 at T-8..T, 12-1 momentum, High(T-1)) from the harness windows equal
#     those from a fresh point-in-time (SCALED_RAW) history ending at today's bar (sample + all holdings,
#     every AUDIT_EVERY sessions); the window's last bar is today's (no look-ahead, no stale data);
#  B. the entry mask from the fresh features equals the live mask for the sampled names;
#  C. ranking: momentum order (highest first, ties by id) or the seeded random order, every close;
#  D. time exits fire exactly when held == limit; E. MA200 exits have Close < MA200 on fresh history;
#  F. rolls happen only for names with today's entry signal; G. every ranked name is eligible with PIT
#     market cap >= $2B and a real bar today. Exits, rolls and entries are logged (QRC65|...) for the
#     offline check of session counting and next-open fills against the fills table.
from AlgorithmImports import *
import json
import numpy as np
import s014
from nullorder import pick_order
from signals import MIN_BARS, entry_mask, features, momentum_order

AUDIT_EVERY, SAMPLE = 10, 20


class H014Canary(s014.TrendPullback):

    def qr_initialize(self):
        super().qr_initialize()
        self.c = {"audits": 0, "feature_checks": 0, "feature_mismatches": 0, "max_rel_dev": {}, "max_rsi_abs_dev": 0.0,
                  "window_not_today": 0, "fresh_short": 0, "mask_checks": 0, "mask_mismatches": 0,
                  "rank_checks": 0, "rank_errors": 0, "time_exit_checks": 0, "time_exit_errors": 0,
                  "ma200_exit_checks": 0, "ma200_exit_errors": 0, "roll_checks": 0, "roll_errors": 0,
                  "ranked_not_eligible": 0, "ranked_cap_below_2b": 0, "ranked_no_real_bar": 0,
                  "signals_logged": 0}

    def qr_on_close(self, data):
        today = self.time.date()
        held_before = {kv.key: self.qr_sessions_held(kv.key) for kv in self.portfolio if kv.value.invested}
        entry_before = {s: dict(e) for s, e in self._qr_entry.items()}
        cands, f, mask, ranked, exits = super().qr_on_close(data)
        c = self.c
        # C. ranking
        c["rank_checks"] += 1
        sig = [s for s, m in zip(cands, mask) if m]
        if self.mode == "rand":
            exp = pick_order([str(s.id) for s in sig], self.seed, self._qr_session)
        else:
            mom = {str(s.id): float(m) for s, m in zip(cands, f["mom"])}
            exp = sorted((str(s.id) for s in sig), key=lambda k: (-mom[k] if np.isfinite(mom[k]) else np.inf, k))
        if [str(s.id) for s in ranked] != exp:
            c["rank_errors"] += 1
        # G. ranked names come from today's eligible universe
        elig = set(self.qr_eligible)
        for s in ranked:
            if s not in elig:
                c["ranked_not_eligible"] += 1
            elif self.qr_eligible_info[s][0] < 2e9:
                c["ranked_cap_below_2b"] += 1
            if not (data.bars.contains_key(s) and not data.bars[s].is_fill_forward):
                c["ranked_no_real_bar"] += 1
        for s in ranked[:self.slots]:
            self._qr_log(f"QRC65|rank|{today}|{s.id}|{ranked.index(s)}")
        # D/E/F. exits and rolls
        sigset = set(sig)
        for s, h in held_before.items():
            rolled = s in self._qr_entry and s in entry_before and self._qr_entry[s]["session"] != entry_before[s]["session"]
            if s in exits:
                w = list(self.qr_close[s])
                below = w[-1] < float(np.mean(w[-200:]))
                reason = "ma200" if below else "time"
                self._qr_log(f"QRC65|exit|{today}|{s.id}|{reason}|{h}")
                if reason == "time":
                    c["time_exit_checks"] += 1
                    if h != self.limit:
                        c["time_exit_errors"] += 1
                else:
                    c["ma200_exit_checks"] += 1
                    self._fresh_ma200_check(s, today)
            if rolled:
                c["roll_checks"] += 1
                self._qr_log(f"QRC65|roll|{today}|{s.id}|{h}")
                if s not in sigset or h != self.limit:
                    c["roll_errors"] += 1
        if self._qr_session % AUDIT_EVERY == 0 and cands:
            self._audit(cands, f, mask, today)

    def _fresh(self, syms, today):
        hist = self.history(syms, MIN_BARS, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        out = {}
        if hist is None or hist.empty:
            return out
        for s in syms:
            try:
                h = hist.loc[s]
            except KeyError:
                continue
            if len(h) < MIN_BARS or h.index[-1].date() != today:
                self.c["fresh_short"] += 1
                continue
            out[s] = (np.array([h["close"].values], dtype=float), np.array([float(h["high"].values[-2])]))
        return out

    def _fresh_ma200_check(self, s, today):
        fr = self._fresh([s], today)
        if s in fr:
            cl = fr[s][0][0]
            if not cl[-1] < cl[-200:].mean():
                self.c["ma200_exit_errors"] += 1
                self._qr_log(f"QRC65|ma200_mismatch|{today}|{s.id}")

    def _audit(self, cands, f, mask, today):
        c = self.c
        c["audits"] += 1
        idx = list(range(0, len(cands), max(1, len(cands) // SAMPLE)))[:SAMPLE]
        idx += [i for i, s in enumerate(cands) if self.portfolio[s].invested and i not in idx]
        syms = [cands[i] for i in idx]
        fr = self._fresh(syms, today)
        for i, s in zip(idx, syms):
            if self._qr_last_bar.get(s) != today:
                c["window_not_today"] += 1
            if s not in fr:
                continue
            g = features(*fr[s])
            c["feature_checks"] += 1
            bad = False
            for k in ("close", "ma50", "ma200", "mom", "high_prev"):
                a, b = float(f[k][i]), float(g[k][0])
                dev = abs(a - b) / max(abs(b), 1e-12)
                c["max_rel_dev"][k] = max(c["max_rel_dev"].get(k, 0.0), dev)
                bad |= dev > 1e-6
            rd = float(np.max(np.abs(f["rsi"][i] - g["rsi"][0])))
            c["max_rsi_abs_dev"] = max(c["max_rsi_abs_dev"], rd)
            bad |= rd > 1e-4
            if bad:
                c["feature_mismatches"] += 1
                if c["feature_mismatches"] <= 30:
                    self._qr_log(f"QRC65|feature_mismatch|{today}|{s.id}")
            c["mask_checks"] += 1
            if bool(entry_mask(g, self.mode, **self.rule)[0]) != bool(mask[i]):
                c["mask_mismatches"] += 1
                self._qr_log(f"QRC65|mask_mismatch|{today}|{s.id}")
            if mask[i] and c["signals_logged"] < 400:
                c["signals_logged"] += 1
                self._qr_log("QRC65|signal|%s|%s|%.6f|%.6f|%.6f|%s|%.6f|%.6f" % (
                    today, s.id, g["close"][0], g["ma50"][0], g["ma200"][0],
                    ",".join("%.3f" % x for x in g["rsi"][0]), g["high_prev"][0], g["mom"][0]))

    def qr_on_end(self):
        super().qr_on_end()
        self._qr_log("QRC65|summary|" + json.dumps(self.c, sort_keys=True, default=str))
