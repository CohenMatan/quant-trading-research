# S025 v1.0 — H023 SCORE v2 WEIGHT SEARCH ON FROZEN DATA v2 (owner D199; research/phase8/H023_spec.md, pinned by
# qresearch.p8h023). NO orders, NO portfolio, NO performance; nothing after 2017-12-31 is requested (the last price row is
# the 2017-12-29 session): 2011-2017 is H023's TRAINING / DEVELOPMENT period, 2018-2021 and the Holdout stay sealed.
# This host is a subclass of the pinned H022 / Data v2 host S024 (uploaded byte-identical as qr_s024; S024 subclasses
# the frozen Data v2 host X998, uploaded byte-identical as qr_x998). Everything S024 builds is reused unchanged: Data v2
# universe, Score v1, the H022 population, responses, panel digest and the H022 canary checks. S025 only ADDS:
#   - the per-stock Score v1 layer subtotals (Technical / Fundamental / Sector) of every population row, checked to sum
#     to the Score v1 total, and their digest (pinned from the canary);
#   - the 92-configuration grid evaluation of qr_h023 (canary on SYNTHETIC responses only; optimiser-null worlds; the
#     ONE real development search with the pinned c_SEARCH).
# New attribute / method names carry the prefix g_ / _g_ (S024 and X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s024, qr_x998, qr_h023,
# qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs, qr_xs_diag, qr_xs_panel, qr_v2,
# qr_data_v2, qr_sec_corrections, qr_industry, qr_fundamentals.
# Modes (params.mode): canary = plumbing only (no IC of real responses); null = optimiser-null worlds params.seeds
# (refused unless the panel and layer-subtotal digests equal the pinned ones); real = refused unless the pinned
# c_SEARCH / fold thresholds / null provenance are given and both digests match.
from AlgorithmImports import *
import hashlib
import json
import os
import time
import numpy as np
import qr_x998  # noqa: F401  (the frozen Data v2 host, imported by qr_s024)
import qr_s024 as S24
import qr_h023 as G
import qr_p7_pred as R
import qr_p7_export as E

G_PROVENANCE = ("c_search", "c_fold", "null_result_sha256", "threshold_commit", "panel_sha256", "components_sha256",
                "spec_sha256")
G_MODULES = ("qr_h023.py", "qr_s024.py", "qr_x998.py", "qr_p7_pred.py")
G_CANARY_SEEDS = (950001, 950002)          # null worlds of the canary (synthetic responses)
G_CANARY_COLS = (G.CONTROL_INDEX, 0, 30, 61, 91)
G_TIMING_WORLDS = 10
G_SUMMARY_KEYS = ("t_ic", "ic_mean", "ic_se", "hi_ann", "mono", "q5_minus_q1_ann", "block_max", "hi_n_mean",
                  "hi_months", "half1", "half2")


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _plain(x):
    """JSON-ready copy: numpy arrays / scalars -> lists / Python numbers, dict keys -> strings."""
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return _plain(x.tolist())
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    return x


class H023ScoreV2(S24.H022DataV2):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S025: unknown mode {mode!r}")
        if not p.get("grid_code_sha256"):
            raise Exception("S025: params need grid_code_sha256 (frozen qr_h023 fingerprint)")
        if mode == "null" and not p.get("components_sha256"):
            raise Exception("S025: null runs need the pinned layer-subtotal digest (components_sha256)")
        if mode == "real":
            for k in G_PROVENANCE:
                if p.get(k) in (None, ""):
                    raise Exception(f"S025: real mode needs the pinned optimiser-null provenance ({k})")
            if sorted(p["c_fold"]) != [str(y) for y in G.FOLD_YEARS]:
                raise Exception("S025: c_fold needs the four walk-forward fold thresholds")
        # S024's initialisation (its real mode needs H022 provenance, which H023 does not use: validated above)
        self.qr_params = dict(p, mode="canary" if mode == "real" else mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.h_mode = mode

    # ------------------------------------------------------------------------------------------------ layer subtotals
    def _g_attach(self, dates):
        """d['C'] = (n, 3) Technical / Fundamental / Sector subtotals of every population row from the frozen Score v1
        points (qr_p7_export rows: DIMS order); each row must sum to its Score v1 total. Digest -> st."""
        rows = {str(t): r for t, r in self.res_rows.items()}
        chk = dict(rows=0, sum_mismatch=0, total_mismatch=0, out_of_range=0, missing_points=0)
        h = hashlib.sha256()
        for d in dates:
            rr = rows[d["day"]]
            C = []
            for s, tot in zip(d["ids"], d["S"]):
                bits, total, pts = rr[s]
                chk["rows"] += 1
                if pts is None:
                    chk["missing_points"] += 1
                    C.append((0, 0, 0))
                    continue
                c = G.layer_split(pts)
                chk["sum_mismatch"] += int(sum(c) != int(total))
                chk["total_mismatch"] += int(int(total) != int(tot))
                chk["out_of_range"] += int(not all(0 <= v <= m for v, m in zip(c, G.LAYER_MAX)))
                C.append(c)
            d["C"] = np.array(C, dtype=np.int64).reshape(-1, 3)
            h.update(json.dumps([d["day"], d["ids"], d["C"].tolist()], separators=(",", ":")).encode())
        self.st["components_sha256"] = h.hexdigest()
        self.st["components_check"] = chk
        if chk["sum_mismatch"] or chk["total_mismatch"] or chk["out_of_range"] or chk["missing_points"]:
            raise Exception(f"S025: layer subtotals inconsistent with the Score v1 totals {chk}; nothing computed")
        base = os.path.dirname(os.path.abspath(G.__file__))
        mods = {}
        for n in G_MODULES:
            try:
                mods[n] = hashlib.sha256(open(os.path.join(base, n), "rb").read()).hexdigest()
            except Exception as ex:
                mods[n] = f"unavailable: {type(ex).__name__}"
        self.st["g_runtime_modules"] = mods
        return dates

    def _g_emit(self, tag, obj):
        blob = E.pack(json.dumps(_plain(obj), sort_keys=True, separators=(",", ":")))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"{tag}|{i // 9000}|{blob[i:i + 9000]}")
        return dict(blob_sha256=_sha(blob), blob_chars=len(blob))

    # ------------------------------------------------------------------------------------------------ canary
    def _canary_v2(self, dates):
        """H022's added canary checks (inherited), then H023's, on SYNTHETIC responses only: layer subtotals, exact
        control score, the grid against the frozen qr_p7_pred procedure (real and null assignments), the optimiser-null
        record (determinism, distinct worlds, control column), the selection / walk-forward machinery end to end, and
        the null runtime on the real panel's score side."""
        super()._canary_v2(dates)
        self._g_attach(dates)
        ck = self.st["canary"]
        g = dict(grid=len(G.GRID), control_index=G.CONTROL_INDEX, control=list(G.GRID[G.CONTROL_INDEX]))
        g["control_z_mismatch"] = int(sum(
            int(np.sum(G.z_scores(d["C"])[:, G.CONTROL_INDEX] != 360 * np.asarray(d["S"], dtype=np.int64)))
            for d in dates))
        rng = np.random.default_rng(990025)
        synth = [dict(d, y=rng.standard_t(5, len(d["ids"])) * 0.07) for d in dates]
        prep = G.prepare(synth)
        g["dates"] = len(prep)
        worst, compared = 0.0, 0
        for seed in (None,) + G_CANARY_SEEDS:
            s = G.summarise(G.world(prep, seed))
            for c in G_CANARY_COLS:
                dd = [dict(d, S=G.score_v2(d["C"], G.GRID[c])) for d in synth]
                rw = R.run_world(R.prepare(dd), seed=seed)
                rw = dict(rw, half1=rw["halves"][0], half2=rw["halves"][1])
                for k in G_SUMMARY_KEYS:
                    a, b = float(rw[k]), float(s[k][c])
                    if a != b and not (np.isnan(a) and np.isnan(b)):
                        worst = max(worst, abs(a - b))
                compared += 1
        g["vs_h022_procedure"] = dict(compared=compared, max_abs_diff=worst)
        t0 = time.perf_counter()
        recs = [G.null_record(prep, 900001 + i) for i in range(G_TIMING_WORLDS)]
        ws = (time.perf_counter() - t0) / G_TIMING_WORLDS
        again = G.null_record(prep, 900001)
        ctrl = R.run_world(R.prepare(synth), seed=900001)
        g["null_record"] = dict(world_s=round(ws, 4), world_s_1000=round(ws * 1000, 1), repeat_identical=again == recs[0],
                                distinct=len({json.dumps(r) for r in recs}), fields=len(G.NULL_FIELDS),
                                control_equals_h022=abs(recs[0][3] - ctrl["t_ic"]) < 1e-12,
                                finite_max_t=int(sum(np.isfinite(r[1]) for r in recs)))
        ev = G.evaluate(prep, G.CRIT_FLOOR, [G.CRIT_FLOOR] * 4)
        g["machinery"] = dict(evaluated=True, folds=len(ev["walk_forward"]["folds"]),
                              pseudo_oos_months=ev["walk_forward"]["pseudo_oos"]["months"],
                              structure_stock_months=ev["structure"]["stock_months"], synthetic_responses=True)
        ck["h023"] = g
        ck["real_ic_computed"] = False
        ck["gates_computed"] = False

    # ------------------------------------------------------------------------------------------------ null
    def _null(self, dates):
        self._g_attach(dates)
        if self.st["components_sha256"] != self.qr_params["components_sha256"]:
            raise Exception("S025: the layer subtotals differ from the pinned digest; no null world computed")
        t0 = time.perf_counter()
        prep = G.prepare(dates)
        rows = [G.null_record(prep, seed) for seed in self.h_seeds]
        out = self._g_emit("QRH", dict(fields=list(G.NULL_FIELDS), worlds=rows))
        self.st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(rows), dates=len(prep),
                               grid=len(G.GRID), world_s=round(time.perf_counter() - t0, 1), **out)

    # ------------------------------------------------------------------------------------------------ real
    def _real(self, dates):
        p = self.qr_params
        self.st["provenance"] = {k: p[k] for k in G_PROVENANCE}
        if self.st["panel_sha256"] != p["panel_sha256"]:
            raise Exception("S025: the prepared panel differs from the pinned H022 / Data v2 panel; nothing computed")
        self._g_attach(dates)
        if self.st["components_sha256"] != p["components_sha256"]:
            raise Exception("S025: the layer subtotals differ from the pinned digest; nothing computed")
        t0 = time.perf_counter()
        c_search = float(p["c_search"])
        c_fold = [float(p["c_fold"][str(y)]) for y in G.FOLD_YEARS]
        prep = G.prepare(dates)
        ev = G.evaluate(prep, c_search, c_fold)                      # the primary search first
        w, s, sel = ev["world"], ev["summary"], ev["selection"]
        out = dict(grid=[list(x) for x in G.GRID], days=[pp["day"] for pp in prep], years=w["years"],
                   n=[len(pp["ids"]) for pp in prep], IC=w["IC"], QM=w["QM"], HI=w["HI"], NH=w["NH"],
                   summary={k: v for k, v in s.items()}, selection=sel, walk_forward=ev["walk_forward"],
                   structure=ev["structure"], cstar=ev["cstar"], c_search=c_search, c_fold=c_fold)
        # NON-GATING diagnostic horizons (2 and 3 reviews ahead; overlapping; Newey-West lag h), after the primary
        for h, key in G.DIAG_HORIZONS:
            sh = G.summarise(G.world(G.prepare(dates, key)), lag=h)
            out[f"h{h}"] = {k: sh[k] for k in G_SUMMARY_KEYS}
        res = self._g_emit("QRH", out)
        self.st["real"] = dict(decisions=len(prep), grid=len(G.GRID), world_s=round(time.perf_counter() - t0, 1),
                               candidate=None if sel["candidate"] is None else list(G.GRID[sel["candidate"]]), **res)
