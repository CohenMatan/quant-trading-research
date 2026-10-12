"""Experiment configuration: loading and validation (IDs, split label vs dates, holdout lock)."""
from __future__ import annotations

import json
import pprint
import re
from datetime import date

from . import config
from .holdout import check_dates

EXP_ID = re.compile(r"^E\d{3}-\d{2}$")
# Strategy number ranges keep experiment IDs (E<strategy number>-<run>) unique across prefixes:
# S000 = pipeline demo, S001–S899 research, B900–B949 benchmarks, X950–X999 infrastructure.
STRATEGY_ID = re.compile(r"^(S(?!9)\d{3}|B9[0-4]\d|X9[5-9]\d|X80\d)$")
HYP_ID = re.compile(r"^H\d{3}$")
VERSION = re.compile(r"^v\d+\.\d+$")
REQUIRED = ("experiment_id", "kind", "strategy_id", "strategy_version", "strategy_dir", "split",
            "start", "end", "cash", "universe", "costs", "portfolio", "params")


class ConfigError(ValueError):
    pass


def withdrawn() -> dict:
    """Experiment id -> reason, for configs withdrawn by an owner decision before they ever ran."""
    import json as _json
    return _json.loads(config.WITHDRAWN_FILE.read_text()) if config.WITHDRAWN_FILE.exists() else {}


def parse(text: str, unlock_file=None) -> dict:
    cfg = json.loads(text)
    validate(cfg, unlock_file=unlock_file)
    return cfg


def validate(cfg: dict, unlock_file=None) -> None:
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ConfigError(f"missing keys: {missing}")
    if not EXP_ID.match(cfg["experiment_id"]):
        raise ConfigError(f"bad experiment_id {cfg['experiment_id']!r} (expected E###-##)")
    if cfg["kind"] not in config.EXPERIMENT_KINDS:
        raise ConfigError(f"bad kind {cfg['kind']!r}")
    if not STRATEGY_ID.match(cfg["strategy_id"]):
        raise ConfigError(f"bad strategy_id {cfg['strategy_id']!r}")
    if not VERSION.match(cfg["strategy_version"]):
        raise ConfigError(f"bad strategy_version {cfg['strategy_version']!r}")
    if cfg["kind"] == "research":
        if not HYP_ID.match(str(cfg.get("hypothesis_id") or "")):
            raise ConfigError("research experiments need a hypothesis_id H###")
        if not cfg["strategy_id"].startswith("S"):
            raise ConfigError("research experiments need an S### strategy")
    # the experiment number's first part must be the strategy number
    if cfg["experiment_id"][1:4] != cfg["strategy_id"][1:4]:
        raise ConfigError("experiment_id E###-## must use the strategy's number")
    start, end = date.fromisoformat(cfg["start"]), date.fromisoformat(cfg["end"])
    check_dates(start, end, unlock_file=unlock_file)
    scheme = cfg.get("split_scheme", "cp1")
    splits = config.SCHEMES.get(scheme)
    if splits is None:
        raise ConfigError(f"unknown split_scheme {scheme!r}")
    split = cfg["split"]
    bounds = splits.get(split)
    if bounds is None:
        raise ConfigError(f"unknown split label {split!r} for scheme {scheme}")
    if not (bounds[0] <= start and end <= bounds[1]):
        raise ConfigError(f"dates {start}..{end} are outside split {split} {bounds[0]}..{bounds[1]}")
    if cfg.get("warmup_start"):
        # D114: history-only warm-up (state initialisation); never performance, selection or evaluation
        try:
            ws = date.fromisoformat(cfg["warmup_start"])
        except ValueError:
            raise ConfigError(f"warmup_start {cfg['warmup_start']!r} is not an ISO date")
        if not (config.WARMUP_EARLIEST <= ws < start):
            raise ConfigError(f"warmup_start must be on/after {config.WARMUP_EARLIEST} and before start {start} (D114)")
    kind = cfg["kind"]
    if kind == "research" and split not in ("IS", "VAL", "WF", "HOLDOUT", "DEV"):
        raise ConfigError("research experiments must run on a single split segment (IS, VAL, WF, HOLDOUT or DEV)")
    if split == "DEV" and cfg.get("programme") not in ("P2", "P11", "P12", "P13"):
        raise ConfigError("the DEV split (2010-2021 development) belongs to Phase 2 configs (programme 'P2', D094) and "
                          "the H026 / H027 / H028 development runs (programmes 'P11' / 'P12' / 'P13', D206 / D213 / D217)")
    if scheme == config.CURRENT_SCHEME:
        if kind in ("research", "benchmark") and start < config.OFFICIAL_START:
            raise ConfigError(f"{kind} experiments cannot start before {config.OFFICIAL_START} (D033)")
        if split == "AUDIT" and kind != "infrastructure":
            raise ConfigError("the AUDIT window is for data audits (kind 'infrastructure') only")
        if split == "STRESS" and kind != "stress":
            raise ConfigError("the STRESS window (1999-2009) is reserved for kind 'stress' (D035)")
        if kind == "stress":
            if split != "STRESS":
                raise ConfigError("stress experiments must use split STRESS")
            if not str(cfg.get("finalist_of") or "").startswith("S"):
                raise ConfigError("stress experiments must name the finalist strategy in 'finalist_of' (D035)")
    if cfg["strategy_id"] == "S016" and cfg.get("params", {}).get("book") in ("gpa", "random"):
        # D115: every trading H016 book (candidate, random controls, sensitivities) uses the H016 portfolio rules
        approved = dict(config.H016_PORTFOLIO)
        if cfg.get("construction_variant") == "H016_P2":
            # D116: pre-declared perturbation P2 (H016_spec.md section 7): 25 slots, minimum new position x 20/25
            if int(cfg["params"].get("slots", -1)) != 25:
                raise ConfigError("H016 perturbation P2 holds 25 slots")
            approved.update(max_positions=25, min_position_usd=config.H016_PORTFOLIO["min_position_usd"] * 20 // 25)
        if cfg["portfolio"] != approved:
            raise ConfigError(f"S016 books must use the H016 portfolio rules {approved} (D115/D116)")
        if cfg["kind"] == "research" and cfg.get("hypothesis_id") != "H016":
            raise ConfigError("S016 research runs belong to hypothesis H016")
        if float(cfg["costs"].get("slippage_bps", -1)) != 10:
            raise ConfigError("base slippage is 10 bps per side (D024); stress multiples via slippage_stress_multiple")
    if cfg["strategy_id"] == "S017" and cfg.get("params", {}).get("book") in ("candidate", "random"):
        # H017 (owner 2026-10-03): every trading book (candidate, random-event controls, sensitivities) uses the H017
        # portfolio rules; the pre-declared perturbations P5/P6 change only the slot count
        approved = dict(config.H017_PORTFOLIO)
        slots = int(cfg["params"].get("slots", 10))
        variant = cfg.get("construction_variant")
        if variant is not None:
            if config.H017_SLOT_VARIANTS.get(variant) != slots:
                raise ConfigError(f"H017 construction variant {variant!r} needs slots {config.H017_SLOT_VARIANTS.get(variant)}")
            approved["max_positions"] = slots
        elif slots != 10:
            raise ConfigError("H017 books hold 10 slots (8/12 only as the pre-declared perturbations P5/P6)")
        if cfg["portfolio"] != approved:
            raise ConfigError(f"S017 books must use the H017 portfolio rules {approved}")
        if cfg["kind"] == "research" and cfg.get("hypothesis_id") != "H017":
            raise ConfigError("S017 research runs belong to hypothesis H017")
        if float(cfg["costs"].get("slippage_bps", -1)) != 10:
            raise ConfigError("base slippage is 10 bps per side (D024); stress multiples via slippage_stress_multiple")
    if cfg["strategy_id"] in ("X984", "S018"):
        # Phase 3 (P3-CP2): every engine run ends on or before 2017-12-31 (search window; 2018+ is the one-shot internal
        # OOS and is never loaded by the engine); the real search / null runs need explicit owner approval
        if cfg["end"] > "2017-12-31":
            raise ConfigError("Phase 3 engine runs end on or before 2017-12-31 (search window)")
        if cfg.get("params", {}).get("mode") == "search" and not cfg.get("owner_approval_required"):
            raise ConfigError("Phase 3 search / null runs need owner_approval_required (owner 2026-10-04)")
    if cfg["strategy_id"] == "S018":
        # H018 frozen search (research/phase3/P3_spec.md, P3-CP2): exactly the frozen window, account, portfolio,
        # costs and architecture (63 sessions, 10 slots; Stage 2 and 126/20 removed); the real world only in the
        # research run, null worlds only in infrastructure runs
        p = cfg.get("params", {})
        names = [w.get("name") for w in p.get("worlds", [])]
        if (cfg.get("hypothesis_id") != "H018" or cfg.get("programme") != "P3" or p.get("mode") != "search"
                or (cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-03-01", "2017-12-31", "2009-07-01")
                or float(cfg["cash"]) != 100000 or int(p.get("slots", -1)) != 10 or int(p.get("hold", -1)) != 63
                or cfg["portfolio"] != dict(config.H017_PORTFOLIO)
                or float(cfg["costs"].get("slippage_bps", -1)) != 10):
            raise ConfigError("S018 runs must follow the frozen Phase 3 specification (H018, P3, search mode, "
                              "2010-03-01..2017-12-31, warm-up 2009-07-01, $100K, 10 slots, 63 sessions, 10 bps)")
        if not names or len(set(names)) != len(names):
            raise ConfigError("S018 runs need distinct world names")
        real = [n for n in names if n == "real"]
        trace = bool(p.get("trace"))
        if real and (names != ["real"] or kind != ("infrastructure" if trace else "research")):
            raise ConfigError("the real world runs alone: as the research run, or as an infrastructure finalist trace "
                              "(params.trace, P3_spec.md section 15)")
        if trace and not real:
            raise ConfigError("a finalist trace runs on the real world")
        if not real and kind != "infrastructure":
            raise ConfigError("null-world runs are infrastructure (never strategy trials)")
    if cfg["strategy_id"] in ("X985", "S020"):
        # H019 (research/phase4/P4_xs_spec.md v2; owner 2026-10-04): the frozen window and universe; nothing after
        # 2017-12-31; X985 = the plumbing canary only; S020 = null batches (infrastructure) and the one real evaluation
        # (research), every S020 run only with explicit owner approval
        from . import p4xs
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-01-04", "2017-12-31", "2009-07-01")
                or not u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("H019 runs use 2010-01-04..2017-12-31, warm-up 2009-07-01 and the data-v1 universe "
                              "(>= $2B, >= $5, ADV20 >= $5M, SEC correction layer)")
        mode = p.get("mode")
        if cfg["strategy_id"] == "X985":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X985 runs only the H019 plumbing canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H019" or cfg.get("programme") != "P4" or not cfg.get("owner_approval_required"):
                raise ConfigError("S020 runs belong to H019 / P4 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p4xs.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S020 null runs are infrastructure batches {p4xs.NULL_BATCHES}")
            elif mode == "real":
                if kind != "research" or not all(k in p for k in ("threshold_c", "threshold_commit",
                                                                   "null_result_sha256", "spec_sha256")):
                    raise ConfigError("the S020 real evaluation is the research run and carries the pinned null "
                                      "provenance (threshold_c, threshold_commit, null_result_sha256, spec_sha256)")
            else:
                raise ConfigError("S020 modes: null or real")
    if cfg["strategy_id"] in ("X987", "S021"):
        # H020 (research/phase5/H020_spec.md v1 + addendum 1; owner authorisation 2026-10-05, D154): the frozen window
        # and universe; nothing after 2017-12-31; X987 = the plumbing / fidelity canary only; S021 = null batches
        # (infrastructure) and the one real evaluation (research), every S021 run only with explicit owner approval
        from . import p5h020
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-01-04", "2017-12-31", "2009-07-01")
                or not u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("H020 runs use 2010-01-04..2017-12-31, warm-up 2009-07-01 and the data-v1 universe "
                              "(>= $2B, >= $5, ADV20 >= $5M, SEC correction layer)")
        mode = p.get("mode")
        if p.get("dev_max_columns") and not cfg.get("scratch_only"):
            raise ConfigError("dev_max_columns is for scratch development runs only")
        if cfg["strategy_id"] == "X987":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X987 runs only the H020 plumbing / fidelity canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H020" or cfg.get("programme") != "P5" or not cfg.get("owner_approval_required"):
                raise ConfigError("S021 runs belong to H020 / P5 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p5h020.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S021 null runs are infrastructure batches {p5h020.NULL_BATCHES}")
            elif mode == "real":
                if kind != "research" or not all(k in p for k in ("c_ic", "c_inc", "threshold_commit",
                                                                   "null_result_sha256", "spec_sha256",
                                                                   "addendum_sha256", "chart_panel_sha256")):
                    raise ConfigError("the S021 real evaluation is the research run and carries the pinned null "
                                      "provenance (c_ic, c_inc, threshold_commit, null_result_sha256, spec_sha256, "
                                      "addendum_sha256, chart_panel_sha256)")
            else:
                raise ConfigError("S021 modes: null or real")
    if cfg["strategy_id"] in ("X991", "X992"):
        # P7-CP1 data / fidelity audits (owner 2026-10-06, D165): infrastructure only, the frozen data-v1 universe,
        # 2010-01-04..2017-12-31 with the history-only warm-up from 2008-07-01; never 2018+ (no returns, no score)
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2010-01-04", "2017-12-31", "2008-07-01")
                or kind != "infrastructure" or not u.get("sec_corrections")
                or float(u.get("min_market_cap", 0)) != 2e9 or float(u.get("min_price", 0)) != 5.0
                or float(u.get("min_avg_dollar_volume", 0)) != 5e6 or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("P7-CP1 audits are infrastructure runs on 2010-01-04..2017-12-31 (warm-up 2008-07-01) "
                              "with the data-v1 universe")
    if cfg["strategy_id"] == "X993":
        # P7-CP3 score availability / mechanics export (owner 2026-10-06, D171): infrastructure, non-trading, the
        # frozen data-v1 universe, official window 2011-01-03..2017-12-31 with the history-only warm-up from
        # 2008-07-01; never 2018+ (no returns, no performance)
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or kind != "infrastructure" or not u.get("sec_corrections")
                or float(u.get("min_market_cap", 0)) != 2e9 or float(u.get("min_price", 0)) != 5.0
                or float(u.get("min_avg_dollar_volume", 0)) != 5e6 or int(u.get("adv_days", 0)) != 20
                or cfg.get("params", {}).get("mode") != "export"):
            raise ConfigError("X993 (P7-CP3) is an infrastructure export on 2011-01-03..2017-12-31 (warm-up "
                              "2008-07-01) with the data-v1 universe")
    if cfg["strategy_id"] == "X995":
        # P7-CP5c (owner D184): new-dataset fundamental-timing probe; infrastructure only, QuantConnect's default build
        # (recorded), 2009-06-01 .. at most 2017-12-31 (no 2018-2021, no Holdout)
        if (kind != "infrastructure" or cfg["start"] != "2009-06-01" or cfg["end"] > "2017-12-31"
                or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("X995 is the P7-CP5c infrastructure probe on the default build, 2009-06-01 .. <= 2017-12-31")
    if cfg["strategy_id"] == "X996":
        # P7-CP5d (owner D186): Score v1 migration feasibility (first-seen ledger M1 / M2); infrastructure only on
        # QuantConnect's default build (recorded); the X993 window and data-v1 universe filters, ending 2017-12-31 or
        # truncated at 2013-12-31 (no 2018-2021, no Holdout); no returns
        u = cfg["universe"]
        if (kind != "infrastructure" or cfg["start"] != "2011-01-03" or cfg.get("warmup_start") != "2008-07-01"
                or cfg["end"] not in ("2013-12-31", "2017-12-31") or not u.get("sec_corrections")
                or float(u.get("min_market_cap", 0)) != 2e9 or float(u.get("min_price", 0)) != 5.0
                or float(u.get("min_avg_dollar_volume", 0)) != 5e6 or int(u.get("adv_days", 0)) != 20
                or cfg.get("params", {}).get("mode") not in ("M1", "M2")
                or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("X996 is the P7-CP5d infrastructure run (mode M1 / M2) on the default build, "
                              "2011-01-03 .. 2013-12-31 or 2017-12-31 (warm-up 2008-07-01), data-v1 universe filters")
    if cfg["strategy_id"] == "X997":
        # P7-CP5e (owner D188): universe-repair feasibility (shadow SEC market cap + earlier SEC identity for M2);
        # infrastructure only on QuantConnect's default build (recorded); X993 window and data-v1 universe filters,
        # 2011-01-03 .. 2017-12-31 (warm-up 2008-07-01); no 2018-2021, no Holdout, no returns
        u = cfg["universe"]
        if (kind != "infrastructure" or cfg["start"] != "2011-01-03" or cfg.get("warmup_start") != "2008-07-01"
                or cfg["end"] != "2017-12-31" or not u.get("sec_corrections")
                or float(u.get("min_market_cap", 0)) != 2e9 or float(u.get("min_price", 0)) != 5.0
                or float(u.get("min_avg_dollar_volume", 0)) != 5e6 or int(u.get("adv_days", 0)) != 20
                or cfg.get("params", {}).get("identity") not in ("extended", "v2")
                or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("X997 is the P7-CP5e infrastructure run (identity extended / v2) on the default build, "
                              "2011-01-03 .. 2017-12-31 (warm-up 2008-07-01), data-v1 universe filters")
    if cfg["strategy_id"] == "X998":
        # P7-CP5f (owner D190): Data Infrastructure v2 score / mechanics export; infrastructure only, default build
        # (recorded); the v2 host installs its own SEC layer (universe.sec_corrections off); 2011-01-03 .. 2017-12-31
        # (or 2013-12-31 for the truncation test), warm-up 2008-07-01; no 2018-2021, no Holdout, no returns
        u = cfg["universe"]
        mode = cfg.get("params", {}).get("mode")
        if (kind != "infrastructure" or cfg["start"] != "2011-01-03" or cfg.get("warmup_start") != "2008-07-01"
                or cfg["end"] not in ("2013-12-31", "2017-12-31") or u.get("sec_corrections")
                or float(u.get("min_market_cap", 0)) != 2e9 or float(u.get("min_price", 0)) != 5.0
                or float(u.get("min_avg_dollar_volume", 0)) != 5e6 or int(u.get("adv_days", 0)) != 20
                or mode not in ("export", "power") or (mode == "power" and cfg["end"] != "2017-12-31")
                or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("X998 is the Data v2 infrastructure export (mode export / power) on the default build, "
                              "2011-01-03 .. 2017-12-31 (or 2013-12-31), warm-up 2008-07-01, data-v1 universe filters, "
                              "universe.sec_corrections off")
    if cfg["strategy_id"] in ("X999", "S024"):
        # H022 on FROZEN Data Infrastructure v2 (owner D194, P7-CP6): the frozen X998 host (uploaded as qr_x998) with the
        # unchanged H022 spec / qr_p7_pred; default build (recorded); 2011-01-03 .. 2017-12-31, warm-up 2008-07-01,
        # universe.sec_corrections off (Data v2 installs its own SEC layer). X999 = the canary only; S024 = the 5,000
        # null worlds in the five pinned batches + the pre-specified determinism rerun, each against the pinned panel
        # digest. The real evaluation is NOT authorised: refused until C_IC_V2 is pinned and only as a research run.
        from . import p7pred_v2
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H022 / Data v2 runs use 2011-01-03..2017-12-31, warm-up 2008-07-01, the Data v2 universe "
                              "filters (universe.sec_corrections off) and the default-build policy")
        if p.get("spec_sha256") != p7pred_v2.SPEC_SHA256 or p.get("pred_code_sha256") != p7pred_v2.PRED_CODE_SHA256:
            raise ConfigError("H022 / Data v2 runs carry the pinned spec and qr_p7_pred fingerprints")
        if cfg.get("hypothesis_id") != "H022" or cfg.get("programme") != "P7" or not cfg.get("owner_approval_required"):
            raise ConfigError("H022 / Data v2 runs belong to H022 / P7 and need owner_approval_required")
        if cfg["strategy_id"] == "X999":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X999 runs only the H022 / Data v2 plumbing canary (infrastructure)")
        elif mode == "null":
            seeds = tuple(p.get("seeds", ()))
            if (kind != "infrastructure" or seeds not in p7pred_v2.NULL_BATCHES + (p7pred_v2.RERUN_SEEDS,)
                    or p7pred_v2.PANEL_SHA256 is None or p.get("panel_sha256") != p7pred_v2.PANEL_SHA256):
                raise ConfigError("S024 null runs are infrastructure batches of the pinned seeds against the pinned "
                                  "Data v2 panel digest (set from the canary)")
        elif mode == "real":
            if (kind != "research" or p7pred_v2.C_IC_V2 is None or p.get("c_ic") != p7pred_v2.C_IC_V2
                    or p.get("null_result_sha256") != p7pred_v2.NULL_RESULT_SHA256
                    or p.get("panel_sha256") != p7pred_v2.PANEL_SHA256):
                raise ConfigError("the H022 / Data v2 real evaluation needs the pinned Data-v2 c_IC, null result and "
                                  "panel digest (and a separate owner authorisation)")
        else:
            raise ConfigError("S024 modes: null or real")
    if cfg["strategy_id"] == "S025":
        # H023 Score v2 weight search (owner D199, research/phase8/H023_spec.md): the S024 host (uploaded as qr_s024) on
        # frozen Data v2, 2011-01-03 .. 2017-12-31 only (2011-2017 = H023 training / development; 2018+ sealed); canary
        # and the 5,000 optimiser-null worlds (pinned batches + rerun) are infrastructure; the ONE real development
        # search is research and needs the pinned c_SEARCH, fold thresholds, null result and digests
        from . import p8h023
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H023 runs use 2011-01-03..2017-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p8h023.SPEC_SHA256 or p.get("pred_code_sha256") != p8h023.PRED_CODE_SHA256
                or p.get("grid_code_sha256") != p8h023.CODE_SHA256["src/qresearch/lean/qr_h023.py"]):
            raise ConfigError("H023 runs carry the pinned H023 spec, qr_p7_pred and qr_h023 fingerprints")
        if cfg.get("hypothesis_id") != "H023" or cfg.get("programme") != "P8" or not cfg.get("owner_approval_required"):
            raise ConfigError("H023 runs belong to H023 / P8 and need owner_approval_required")
        if mode == "canary":
            if kind != "infrastructure":
                raise ConfigError("the H023 canary is infrastructure")
        elif mode == "null":
            seeds = tuple(p.get("seeds", ()))
            if (kind != "infrastructure" or seeds not in p8h023.NULL_BATCHES + (p8h023.RERUN_SEEDS,)
                    or p.get("panel_sha256") != p8h023.PANEL_SHA256 or p8h023.COMPONENTS_SHA256 is None
                    or p.get("components_sha256") != p8h023.COMPONENTS_SHA256):
                raise ConfigError("H023 null runs are infrastructure batches of the pinned seeds against the pinned "
                                  "panel and layer-subtotal digests (set from the canary)")
        elif mode == "real":
            if (kind != "research" or p8h023.C_SEARCH is None or p.get("c_search") != p8h023.C_SEARCH
                    or p.get("c_fold") != {str(k): v for k, v in (p8h023.C_FOLD or {}).items()}
                    or p.get("null_result_sha256") != p8h023.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p8h023.THRESHOLD_COMMIT
                    or p.get("panel_sha256") != p8h023.PANEL_SHA256
                    or p.get("components_sha256") != p8h023.COMPONENTS_SHA256):
                raise ConfigError("the H023 real development search needs the pinned c_SEARCH, fold thresholds, null "
                                  "result, threshold commit and digests")
        else:
            raise ConfigError("S025 modes: canary, null or real")
    if cfg["strategy_id"] == "S026":
        # H024 Feature Redesign and Selection (owner D201, research/phase9/H024_spec.md): the S024 host (uploaded as
        # qr_s024) on frozen Data v2, 2011-01-03 .. 2017-12-31 only (2011-2017 = H024 development; 2018+ sealed); the
        # canary and the 5,000 null worlds are infrastructure; the ONE real development search is research and needs
        # the pinned c_MODEL / c_FEATURE / fold thresholds, null result, library and population digests
        from . import p9h024
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H024 runs use 2011-01-03..2017-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p9h024.SPEC_SHA256 or p.get("pred_code_sha256") != p9h024.PRED_CODE_SHA256
                or p.get("feature_code_sha256") != p9h024.CODE_SHA256["src/qresearch/lean/qr_h024.py"]):
            raise ConfigError("H024 runs carry the pinned H024 spec, qr_p7_pred and qr_h024 fingerprints")
        if cfg.get("hypothesis_id") != "H024" or cfg.get("programme") != "P9" or not cfg.get("owner_approval_required"):
            raise ConfigError("H024 runs belong to H024 / P9 and need owner_approval_required")
        pinned = (p9h024.FEATURES is not None and p.get("features") == list(p9h024.FEATURES)
                  and p.get("links") == [list(x) for x in p9h024.LINKS]
                  and p.get("library_sha256") == p9h024.LIBRARY_SHA256
                  and p.get("population_sha256") == p9h024.POPULATION_SHA256
                  and p.get("panel_sha256") == p9h024.PANEL_SHA256)
        if mode == "canary":
            if kind != "infrastructure":
                raise ConfigError("the H024 canary is infrastructure")
        elif mode == "null":
            if kind != "infrastructure" or tuple(p.get("seeds", ())) not in p9h024.NULL_BATCHES + (p9h024.RERUN_SEEDS,) \
                    or not pinned:
                raise ConfigError("H024 null runs are infrastructure batches of the pinned seeds against the pinned "
                                  "library, population and panel (set from the canary)")
        elif mode == "real":
            if (kind != "research" or not pinned or p9h024.C_MODEL is None or p.get("c_model") != p9h024.C_MODEL
                    or p.get("c_feature") != p9h024.C_FEATURE
                    or p.get("c_fold") != {str(k): v for k, v in (p9h024.C_FOLD or {}).items()}
                    or p.get("null_result_sha256") != p9h024.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p9h024.THRESHOLD_COMMIT):
                raise ConfigError("the H024 real development search needs the pinned c_MODEL, c_FEATURE, fold "
                                  "thresholds, null result, threshold commit, library and population digests")
        else:
            raise ConfigError("S026 modes: canary, null or real")
    if cfg["strategy_id"] == "S027":
        # H025 Insider Cluster Buying (owner D204, research/phase10/H025_spec.md): the S024 host (uploaded as qr_s024) on
        # frozen Data v2 + the frozen SEC event ledger, 2011-01-03 .. 2017-12-31 only (2011-2017 = H025 development;
        # 2018+ sealed); audit, canary and the 5,000 matched null worlds are infrastructure; the ONE real development
        # evaluation is research and needs the pinned c_EVENT, null result, ledger and response-panel digests
        from . import p10h025
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H025 runs use 2011-01-03..2017-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p10h025.SPEC_SHA256 or p.get("pred_code_sha256") != p10h025.PRED_CODE_SHA256
                or p.get("h025_code_sha256") != p10h025.CODE_SHA256["src/qresearch/lean/qr_h025.py"]
                or p.get("payload_sha256") != p10h025.PAYLOAD_SHA256
                or p.get("calendar_sha256") != p10h025.CALENDAR_SHA256):
            raise ConfigError("H025 runs carry the pinned H025 spec, module, SEC ledger payload and calendar digests")
        if cfg.get("hypothesis_id") != "H025" or cfg.get("programme") != "P10" or not cfg.get("owner_approval_required"):
            raise ConfigError("H025 runs belong to H025 / P10 and need owner_approval_required")
        pinned = p10h025.IN_HOST_LEDGER_SHA256 is not None and p.get("in_host_ledger_sha256") == p10h025.IN_HOST_LEDGER_SHA256
        if mode == "audit":
            if kind != "infrastructure":
                raise ConfigError("the H025 no-return audit is infrastructure")
        elif mode == "canary":
            if kind != "infrastructure" or not pinned:
                raise ConfigError("the H025 canary is infrastructure and needs the pinned in-host ledger digest")
        elif mode == "null":
            # the first null run (E027-04) SETS the response-panel digest; every later null run must carry the pin
            panel_ok = (p.get("response_panel_sha256") is None and cfg["experiment_id"] == p10h025.NULL_RUNS[0]) \
                or (p10h025.RESPONSE_PANEL_SHA256 is not None
                    and p.get("response_panel_sha256") == p10h025.RESPONSE_PANEL_SHA256)
            if kind != "infrastructure" or tuple(p.get("seeds", ())) != p10h025.NULL_SEEDS_RANGE or not pinned \
                    or p10h025.EVENT_LEDGER_SHA256 is None or not panel_ok:
                raise ConfigError("H025 null runs are infrastructure: seeds 1..5000 against the pinned ledger digests")
        elif mode == "real":
            if (kind != "research" or not pinned or p10h025.C_EVENT is None or p.get("c_event") != p10h025.C_EVENT
                    or p.get("null_result_sha256") != p10h025.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p10h025.THRESHOLD_COMMIT
                    or p.get("response_panel_sha256") != p10h025.RESPONSE_PANEL_SHA256
                    or p.get("event_ledger_sha256") != p10h025.EVENT_LEDGER_SHA256):
                raise ConfigError("the H025 real development evaluation needs the pinned c_EVENT, null result, threshold "
                                  "commit, event-ledger and response-panel digests")
        else:
            raise ConfigError("S027 modes: audit, canary, null or real")
    if cfg["strategy_id"] == "X801":
        # Data Infrastructure v2.1 (owner D206): the frozen X998 extended through 2021-12-31 (no 2022+ data); export
        # audits only (infrastructure): full 2011-2021, the 2011-2017 reproduction window and the 2013 truncation
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg.get("warmup_start")) != ("2011-01-03", "2008-07-01")
                or cfg["end"] not in ("2021-12-31", "2017-12-31", "2013-12-31")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("X801 runs use 2011-01-03..2021-12-31 (or the 2017 / 2013 ends), warm-up 2008-07-01, the "
                              "Data v2 universe filters (universe.sec_corrections off) and the default-build policy")
        if p.get("mode") != "export" or kind != "infrastructure" or cfg.get("programme") != "P11" \
                or cfg.get("hypothesis_id") != "H026" or not cfg.get("owner_approval_required"):
            raise ConfigError("X801 runs are Data v2.1 infrastructure exports for H026 / P11 with owner approval")
    if cfg["strategy_id"] == "X802":
        # H029-A Business Improvement data-feasibility audit (owner D227, research/phase14/H029A_audit_spec.md): the
        # frozen X801 Data v2.1 host + qr_h029a; aggregates only (coverage, staleness, distributions, input-to-input
        # correlations); NO returns; 2011-01-03 .. 2021-12-31 (nothing after 2021-12-31); infrastructure, AUDIT window
        from . import p14h029a
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H029-A audit runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe "
                              "filters (universe.sec_corrections off) and the default-build policy")
        if (p.get("mode") != "audit" or p.get("spec_sha256") != p14h029a.SPEC_SHA256
                or p.get("h029a_code_sha256") != p14h029a.CODE_SHA256.get("src/qresearch/lean/qr_h029a.py")
                or p.get("data_v21_manifest_sha256") != p14h029a.DATA_V21_MANIFEST_SHA256):
            raise ConfigError("H029-A audit runs carry the pinned audit spec, qr_h029a and Data v2.1 manifest fingerprints")
        if (kind != "infrastructure" or split != "AUDIT" or cfg.get("hypothesis_id") != "H029"
                or cfg.get("programme") != "P14" or not cfg.get("owner_approval_required")):
            raise ConfigError("H029-A runs are infrastructure audits (AUDIT window) for H029 / P14 with owner approval")
    if cfg["strategy_id"] == "X803":
        # Data v3 audit (owner D229, research/phase14/data_v3/DATA_V3_spec.md): the frozen X801 Data v2.1 host + qr_v3
        # (guard v3, v3 view, H029 signals, SEC validation, F7 split test); aggregates only; NO returns;
        # 2011-01-03 .. 2021-12-31 (nothing after 2021-12-31); infrastructure, AUDIT window
        from . import p14datav3
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("Data v3 audit runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe "
                              "filters (universe.sec_corrections off) and the default-build policy")
        if (p.get("mode") != "audit" or p.get("spec_sha256") != p14datav3.SPEC_SHA256
                or p.get("v3_code_sha256") != p14datav3.CODE_SHA256.get("src/qresearch/lean/qr_v3.py")
                or p.get("guard_sha256") != p14datav3.GUARD_SHA256 or p.get("val_sha256") != p14datav3.VAL_SHA256
                or p.get("data_v21_manifest_sha256") != p14datav3.DATA_V21_MANIFEST_SHA256 or not p14datav3.SPEC_SHA256):
            raise ConfigError("Data v3 audit runs carry the pinned spec, qr_v3, packed-table and Data v2.1 manifest "
                              "fingerprints")
        if (kind != "infrastructure" or split != "AUDIT" or cfg.get("hypothesis_id") != "H029"
                or cfg.get("programme") != "P14" or not cfg.get("owner_approval_required")):
            raise ConfigError("Data v3 runs are infrastructure audits (AUDIT window) for H029 / P14 with owner approval")
    if cfg["strategy_id"] == "S031":
        # H029 / H030 (owner D229, research/phase14/H029_H030_spec.md): the standalone S031 host on the frozen X801 Data
        # v2.1 host + Data v3 + the frozen H028 path; 2011-01-03 .. 2021-12-31 (evaluation 2015-2021; nothing after
        # 2021-12-31); canary and the null worlds are infrastructure; the ONE real development run is research (DEV)
        # and needs the pinned c_UP_H029, c_INCREMENTAL_H030, null result and threshold commit
        from . import p14datav3, p14h029
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H029 / H030 runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe "
                              "filters (universe.sec_corrections off) and the default-build policy")
        w28, wlv, coef = p14h029.h028_inputs()
        if (not p14h029.SPEC_SHA256 or p.get("spec_sha256") != p14h029.SPEC_SHA256
                or p.get("h029_code_sha256") != p14h029.CODE_SHA256["src/qresearch/lean/qr_h029.py"]
                or p.get("data_v3_manifest_sha256") != p14h029.DATA_V3_MANIFEST_SHA256
                or p.get("guard_sha256") != p14datav3.GUARD_SHA256
                or p.get("h029_panel_digests_sha256") != p14h029.h029_panel_digests_sha256()
                or p.get("h026_feature_panel_sha256") != p14h029.H026_FEATURE_PANEL_SHA256
                or p.get("h026_response_panel_sha256") != p14h029.H026_RESPONSE_PANEL_SHA256
                or p.get("h028_real_wealth") != w28 or p.get("lv15_real_wealth") != wlv
                or p.get("h028_coefficients") != coef):
            raise ConfigError("H029 / H030 runs carry the pinned spec, qr_h029, Data v3, H026 panel and frozen H028 / "
                              "LV15 fingerprints")
        if cfg.get("hypothesis_id") != "H029" or cfg.get("programme") != "P14" or not cfg.get("owner_approval_required"):
            raise ConfigError("S031 runs belong to H029 / P14 and need owner_approval_required")
        if mode in ("canary", "null"):
            if kind != "infrastructure":
                raise ConfigError("S031 canary / null runs are infrastructure")
            if mode == "null" and tuple(p.get("seeds", ())) not in [tuple(v) for v in p14h029.NULL_SEEDS.values()]:
                raise ConfigError("S031 null batches are the pinned seed ranges")
        elif mode == "real":
            if (kind != "research" or split != "DEV" or p14h029.C_UP_H029 is None
                    or p.get("c_up_h029") != p14h029.C_UP_H029
                    or p.get("c_incremental_h030") != p14h029.C_INCREMENTAL_H030
                    or p.get("null_result_sha256") != p14h029.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p14h029.THRESHOLD_COMMIT):
                raise ConfigError("the ONE real H029 / H030 run is research (DEV) with the pinned thresholds")
        else:
            raise ConfigError("S031 modes: canary, null, real")
    if cfg["strategy_id"] == "S028":
        # H026 Learned Stock Score Portfolio (owner D206, research/phase11/H026_spec.md): the frozen X801 Data v2.1 host
        # (uploaded as qr_x801) + qr_h026, 2011-01-03 .. 2021-12-31 (2011-2021 = H026 development; nothing after
        # 2021-12-31); canary and the 5,000 null worlds are infrastructure; the ONE real development run is research on
        # the DEV split (programme P11) and needs the pinned c_WEALTH, null result, threshold commit and panel digests
        from . import p11h026
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H026 runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p11h026.SPEC_SHA256
                or p.get("h026_code_sha256") != p11h026.CODE_SHA256["src/qresearch/lean/qr_h026.py"]
                or p.get("data_v21_manifest_sha256") != p11h026.DATA_V21_MANIFEST_SHA256):
            raise ConfigError("H026 runs carry the pinned H026 spec, qr_h026 and Data v2.1 manifest fingerprints")
        if cfg.get("hypothesis_id") != "H026" or cfg.get("programme") != "P11" or not cfg.get("owner_approval_required"):
            raise ConfigError("H026 runs belong to H026 / P11 and need owner_approval_required")
        panel = p11h026.FEATURE_PANEL_SHA256 is not None and p.get("feature_panel_sha256") == p11h026.FEATURE_PANEL_SHA256
        if mode == "canary":
            if kind != "infrastructure" or split != "AUDIT":
                raise ConfigError("the H026 canary is infrastructure (AUDIT window)")
        elif mode == "null":
            if (kind != "infrastructure" or split != "AUDIT" or not panel
                    or tuple(p.get("seeds", ())) not in p11h026.NULL_BATCHES + (p11h026.RERUN_SEEDS,)):
                raise ConfigError("H026 null runs are infrastructure batches of the pinned seeds against the pinned "
                                  "feature panel (set from the canary)")
        elif mode == "real":
            if (kind != "research" or split != "DEV" or not panel or p11h026.C_WEALTH is None
                    or p.get("c_wealth") != p11h026.C_WEALTH
                    or p.get("null_result_sha256") != p11h026.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p11h026.THRESHOLD_COMMIT
                    or p.get("response_panel_sha256") != p11h026.RESPONSE_PANEL_SHA256):
                raise ConfigError("the H026 real development run needs the pinned c_WEALTH, null result, threshold "
                                  "commit, feature- and response-panel digests")
        else:
            raise ConfigError("S028 modes: canary, null or real")
    if cfg["strategy_id"] == "S029":
        # H027 Exposure-Controlled Learned Stock Score (owner D213, research/phase12/H027_spec.md): the pinned H026 host
        # S028 (uploaded as qr_s028) + qr_h027, 2011-01-03 .. 2021-12-31 (fully seen development data; nothing after
        # 2021-12-31); canary and the 5,000 LOWVOL-conditional null worlds are infrastructure; the ONE real
        # development run is research on the DEV split (programme P12) and needs the pinned c_WEALTH_CONDITIONAL
        from . import p12h027
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H027 runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p12h027.SPEC_SHA256
                or p.get("h027_code_sha256") != p12h027.CODE_SHA256.get("src/qresearch/lean/qr_h027.py")
                or p.get("data_v21_manifest_sha256") != p12h027.DATA_V21_MANIFEST_SHA256
                or p.get("h026_feature_panel_sha256") != p12h027.H026_FEATURE_PANEL_SHA256
                or p.get("h026_response_panel_sha256") != p12h027.H026_RESPONSE_PANEL_SHA256):
            raise ConfigError("H027 runs carry the pinned H027 spec, qr_h027, Data v2.1 manifest and H026 panel digests")
        if cfg.get("hypothesis_id") != "H027" or cfg.get("programme") != "P12" or not cfg.get("owner_approval_required"):
            raise ConfigError("H027 runs belong to H027 / P12 and need owner_approval_required")
        if mode == "canary":
            if kind != "infrastructure" or split != "AUDIT" or p.get("h026_null_rows_sha256") != p12h027.H026_NULL_ROWS_SHA256:
                raise ConfigError("the H027 canary is infrastructure (AUDIT window) with the E028-04 null-row digest")
        elif mode == "null":
            if (kind != "infrastructure" or split != "AUDIT"
                    or tuple(p.get("seeds", ())) not in p12h027.NULL_BATCHES + (p12h027.RERUN_SEEDS,)):
                raise ConfigError("H027 null runs are infrastructure batches of the pinned seeds")
        elif mode == "real":
            if (kind != "research" or split != "DEV" or p12h027.C_WEALTH_CONDITIONAL is None
                    or p.get("c_wealth_conditional") != p12h027.C_WEALTH_CONDITIONAL
                    or p.get("null_result_sha256") != p12h027.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p12h027.THRESHOLD_COMMIT
                    or p.get("h026_real_wealth") != p12h027.H026_REAL_WEALTH
                    or p.get("h026_real_s_wealth") != p12h027.H026_REAL_S_WEALTH or p12h027.ADEQUATE is not True):
                raise ConfigError("the H027 real development run needs the pinned c_WEALTH_CONDITIONAL, null result, "
                                  "threshold commit, H026 references and an ADEQUATE conditional null")
        else:
            raise ConfigError("S029 modes: canary, null or real")
    if cfg["strategy_id"] == "S030":
        # H028 Fixed Strong Shrinkage Learned Stock Score (owner D217, research/phase13/H028_spec.md): the pinned H027 host
        # S029 (uploaded as qr_s029) + qr_h028, lambda = 100 for every fit; 2011-01-03 .. 2021-12-31 (fully seen
        # development data); canary and the 5,000 lambda-100 conditional null worlds are infrastructure; the ONE real
        # development run is research on the DEV split (programme P13) and needs the pinned c_WEALTH_H028 + tolerance
        from . import p13h028
        p = cfg.get("params", {})
        u = cfg["universe"]
        mode = p.get("mode")
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2021-12-31", "2008-07-01")
                or u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20 or cfg.get("lean_version_policy") != "default_build_digest_verified"):
            raise ConfigError("H028 runs use 2011-01-03..2021-12-31, warm-up 2008-07-01, the Data v2 universe filters "
                              "(universe.sec_corrections off) and the default-build policy")
        if (p.get("spec_sha256") != p13h028.SPEC_SHA256
                or p.get("h028_code_sha256") != p13h028.CODE_SHA256.get("src/qresearch/lean/qr_h028.py")
                or p.get("data_v21_manifest_sha256") != p13h028.DATA_V21_MANIFEST_SHA256
                or p.get("h026_feature_panel_sha256") != p13h028.H026_FEATURE_PANEL_SHA256
                or p.get("h026_response_panel_sha256") != p13h028.H026_RESPONSE_PANEL_SHA256
                or p.get("h027_real_wealth") != p13h028.H027_REAL_WEALTH
                or p.get("h027_real_s_wealth") != p13h028.H027_REAL_S_WEALTH
                or list(p.get("h027_lambda_schedule", [])) != list(p13h028.H027_LAMBDA_SCHEDULE)):
            raise ConfigError("H028 runs carry the pinned H028 spec, qr_h028, Data v2.1 manifest, H026 panel digests and "
                              "the H027 references")
        if cfg.get("hypothesis_id") != "H028" or cfg.get("programme") != "P13" or not cfg.get("owner_approval_required"):
            raise ConfigError("H028 runs belong to H028 / P13 and need owner_approval_required")
        if mode == "canary":
            if (kind != "infrastructure" or split != "AUDIT"
                    or p.get("h027_null_rows_sha256") != p13h028.H027_NULL_ROWS_SHA256):
                raise ConfigError("the H028 canary is infrastructure (AUDIT window) with the E029-02 rows 1-25 digest")
        elif mode == "null":
            if (kind != "infrastructure" or split != "AUDIT" or p13h028.TOLERANCE is None
                    or tuple(p.get("seeds", ())) not in p13h028.NULL_BATCHES + (p13h028.RERUN_SEEDS,)):
                raise ConfigError("H028 null runs are infrastructure batches of the pinned seeds, after the tolerance "
                                  "table is pinned")
        elif mode == "real":
            if (kind != "research" or split != "DEV" or p13h028.C_WEALTH_H028 is None
                    or p.get("c_wealth_h028") != p13h028.C_WEALTH_H028
                    or p.get("null_result_sha256") != p13h028.NULL_RESULT_SHA256
                    or p.get("threshold_commit") != p13h028.THRESHOLD_COMMIT
                    or p.get("tolerance") != p13h028.TOLERANCE
                    or p.get("tolerance_sha256") != p13h028.TOLERANCE_SHA256 or p13h028.ADEQUATE is not True):
                raise ConfigError("the H028 real development run needs the pinned c_WEALTH_H028, null result, threshold "
                                  "commit, tolerance table and an ADEQUATE conditional null")
        else:
            raise ConfigError("S030 modes: canary, null or real")
    if cfg.get("lean_version_policy") is not None and not (
            cfg["strategy_id"] in ("X994", "S023", "X995", "X996", "X997", "X998", "X999", "S024", "S025", "S026", "S027", "X801", "S028", "S029", "S030", "X802", "X803", "S031") or (cfg["strategy_id"] == "X993" and
                                                       cfg.get("lean_version_policy") == "default_build_digest_verified")):
        raise ConfigError("lean_version_policy is allowed only for the H022 family (X994 / S023) and the X993 score "
                          "export used to diagnose it (D182)")
    if cfg["strategy_id"] in ("X994", "S023"):
        # H022 (research/phase7/P7_predictive_spec.md v1 + the D177 wording fix; owner authorisation 2026-10-06, D177):
        # the X993 v1.1 window and data-v1 universe, nothing after 2017-12-31, the frozen spec / module fingerprints;
        # X994 = the plumbing canary only; S023 = null batches (infrastructure) and the ONE real evaluation (research,
        # only with the pinned c_IC and null provenance), every S023 run only with explicit owner approval
        from . import p7pred
        p = cfg.get("params", {})
        u = cfg["universe"]
        if ((cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2011-01-03", "2017-12-31", "2008-07-01")
                or not u.get("sec_corrections") or float(u.get("min_market_cap", 0)) != 2e9
                or float(u.get("min_price", 0)) != 5.0 or float(u.get("min_avg_dollar_volume", 0)) != 5e6
                or int(u.get("adv_days", 0)) != 20):
            raise ConfigError("H022 runs use 2011-01-03..2017-12-31, warm-up 2008-07-01 and the data-v1 universe "
                              "(>= $2B, >= $5, ADV20 >= $5M, SEC correction layer)")
        if (p.get("spec_sha256") != p7pred.SPEC_SHA256
                or p.get("pred_code_sha256") != p7pred.CODE_SHA256["src/qresearch/lean/qr_p7_pred.py"]):
            raise ConfigError("H022 runs carry the pinned spec and qr_p7_pred fingerprints (qresearch.p7pred)")
        mode = p.get("mode")
        # D182 (owner option B, P7-CP5a): after QuantConnect gated engine selection, X994 canaries and the S023 real
        # evaluation may run on QuantConnect's default build; the real run is then valid only through the host's
        # panel-digest guard (the prepared panel must equal the pinned PANEL_SHA256 the null was calibrated on)
        pol = cfg.get("lean_version_policy")
        if pol is not None and (pol != "default_build_digest_verified" or not (
                cfg["strategy_id"] == "X994" or (mode == "real" and p.get("panel_sha256")))):
            raise ConfigError("lean_version_policy 'default_build_digest_verified' is allowed only for X994 canaries "
                              "and the digest-guarded S023 real evaluation (D182)")
        if cfg["strategy_id"] == "X994":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X994 runs only the H022 plumbing canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H022" or cfg.get("programme") != "P7" or not cfg.get("owner_approval_required"):
                raise ConfigError("S023 runs belong to H022 / P7 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p7pred.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S023 null runs are infrastructure batches {p7pred.NULL_BATCHES}")
            elif mode == "real":
                if (kind != "research" or p7pred.C_IC is None or p.get("c_ic") != p7pred.C_IC
                        or p.get("threshold_commit") != p7pred.THRESHOLD_COMMIT
                        or p.get("null_result_sha256") != p7pred.NULL_RESULT_SHA256
                        or p.get("panel_sha256") != getattr(p7pred, "PANEL_SHA256", None)):
                    raise ConfigError("the S023 real evaluation is the research run and carries exactly the pinned "
                                      "null provenance (c_ic, threshold_commit, null_result_sha256, panel_sha256)")
            else:
                raise ConfigError("S023 modes: null or real")
    if cfg["strategy_id"] in ("X989", "S022"):
        # H021-A (research/phase6/H021A_spec.md v1; owner 2026-10-06, D160): a non-trading one-month host that reads
        # history 1998-12-01 .. 2017-12-31 only; X989 = the fidelity canary; S022 = null batches (infrastructure) and
        # the one real evaluation (research), every S022 run only with explicit owner approval
        from . import p6h021
        p = cfg.get("params", {})
        if (cfg["start"], cfg["end"], cfg.get("warmup_start")) != ("2017-12-01", "2017-12-31", None):
            raise ConfigError("H021-A runs use the one-month host window 2017-12-01..2017-12-31 (no warm-up)")
        mode = p.get("mode")
        if cfg["strategy_id"] == "X989":
            if mode != "canary" or kind != "infrastructure":
                raise ConfigError("X989 runs only the H021-A fidelity canary (infrastructure)")
        else:
            if cfg.get("hypothesis_id") != "H021" or cfg.get("programme") != "P6" or not cfg.get("owner_approval_required"):
                raise ConfigError("S022 runs belong to H021 / P6 and need owner_approval_required")
            if mode == "null":
                if tuple(p.get("seeds", ())) not in p6h021.NULL_BATCHES or kind != "infrastructure":
                    raise ConfigError(f"S022 null runs are infrastructure batches {p6h021.NULL_BATCHES}")
            elif mode == "real":
                if kind != "research" or not all(k in p for k in ("threshold_c", "threshold_commit",
                                                                   "null_result_sha256", "spec_sha256",
                                                                   "panel_sha256", "diag_sha256")):
                    raise ConfigError("the S022 real evaluation is the research run and carries the pinned null "
                                      "provenance (threshold_c, threshold_commit, null_result_sha256, spec_sha256, "
                                      "panel_sha256, diag_sha256)")
            else:
                raise ConfigError("S022 modes: null or real")
    if scheme == config.CURRENT_SCHEME:
        c = cfg["costs"]
        if (c.get("commission_model") != config.COMMISSION_MODEL
                or float(c.get("commission_per_order", -1)) != config.COMMISSION_PER_ORDER):
            raise ConfigError(f"costs must use the fixed ${config.COMMISSION_PER_ORDER:g} per-order commission (D039)")
        if "slippage_bps" not in c:
            raise ConfigError("costs need slippage_bps (slippage is modelled separately from commission)")
        if kind in ("research", "sizing", "stress") and cfg["strategy_id"] not in ("S016", "S017", "S018", "S020", "S021", "S022",
                                                                                     "S023"):
            model = cfg.get("execution_model", "d044")
            if model not in config.RESEARCH_PORTFOLIOS:
                raise ConfigError(f"unknown execution_model {model!r}")
            approved = dict(config.RESEARCH_PORTFOLIOS[model])
            if kind == "sizing" and cfg.get("construction_variant") == "S2":
                # D083: C03's pre-declared $200K construction variant S2 (owner-approved, CP3e §2) holds
                # 20 positions; every other portfolio rule stays the approved one
                if not (int(cfg["portfolio"].get("max_positions", 0)) == int(cfg["params"].get("slots", -1)) == 20):
                    raise ConfigError("construction variant S2 uses 20 positions (max_positions = slots = 20)")
                approved["max_positions"] = 20
            if cfg["portfolio"] != approved:
                raise ConfigError(f"portfolio must be the approved rules for {model}: "
                                  f"{config.RESEARCH_PORTFOLIOS[model]} (D041/D044/D051)")
            if float(c["slippage_bps"]) != 10:
                raise ConfigError("base slippage is 10 bps per side (D024); stress multiples are separate experiments "
                                  "declared with costs.slippage_stress_multiple")
        if kind == "research" and float(cfg["cash"]) != config.RESEARCH_CASH:
            raise ConfigError("research experiments use the $100,000 primary account (D044); use kind 'sizing'")
        if kind == "sizing":
            if not str(cfg.get("account_size_test_of") or "").startswith("E"):
                raise ConfigError("sizing experiments must name the tested experiment in 'account_size_test_of' (D044)")
            if split not in ("IS", "VAL", "WF", "DEV"):
                raise ConfigError("sizing experiments use IS, VAL, WF or DEV")
    if float(cfg["universe"].get("min_market_cap", 0)) < config.MIN_MARKET_CAP:
        raise ConfigError("universe min_market_cap is below the approved $2B")


def lean_params(cfg: dict, holdout_unlocked: bool) -> str:
    """Contents of the generated qr_params.py uploaded next to the algorithm."""
    exp = {k: cfg[k] for k in ("experiment_id", "start", "end", "cash", "universe", "costs",
                               "portfolio", "params")}
    if cfg.get("warmup_start"):            # D114; absent keys keep earlier runs' generated files byte-identical
        exp["warmup_start"] = cfg["warmup_start"]
    exp["holdout_unlocked"] = bool(holdout_unlocked)
    return ("# Generated by qresearch.run — do not edit.\n"
            f"EXPERIMENT = {pprint.pformat(exp, sort_dicts=True, width=100)}\n")
