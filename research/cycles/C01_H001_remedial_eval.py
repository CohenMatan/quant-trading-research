import json, sys, pandas as pd
sys.path.insert(0, "/home/user/quant-trading-research/src")
from qresearch import results, metrics, gates, stats
R = "/home/user/quant-trading-research/experiments"
ld = lambda e, f: results.read_csv_gz(f"{R}/{e}/{f}.csv.gz")
bench = ld("E901-07", "equity")
rows, rets, detail = [], {}, {}
for old, e in zip("E001-11 E001-12 E001-13 E001-14 E001-15".split(), "E001-16 E001-17 E001-18 E001-19 E001-20".split()):
    r = json.load(open(f"{R}/{e}/result.json")); cfg = json.load(open(f"{R}/{e}/config.json"))
    eq, tr, fi = ld(e, "equity"), ld(e, "trades"), ld(e, "fills")
    a, z = eq.date.iloc[0], eq.date.iloc[-1]
    b = metrics.slice_equity(bench, a, z)
    m = metrics.compute_metrics(eq, tr, fi); mb = metrics.compute_metrics(b)
    chk = gates.is_screen(eq, tr, b); detail[e] = chk
    s = r["harness_summary"]
    op = tr[(tr.status != "closed") & (tr.entry_date < "2017-11-29")]
    closed = tr[tr.status == "closed"]
    hold = (pd.to_datetime(closed.exit_date) - pd.to_datetime(closed.entry_date)).dt.days
    rets[e] = metrics.returns_from_equity(pd.Series(eq.equity.to_numpy(float), index=eq.date))
    old_r = json.load(open(f"{R}/{old}/result.json"))["metrics"]
    rows.append(dict(run=e, version=cfg["strategy_version"], status=r["status"], cagr=m["cagr"], sharpe=m["sharpe"], ew_sharpe=mb["sharpe"],
                     max_dd=m["max_drawdown"], trades=m.get("n_trades"), pf=m.get("profit_factor"), win=m.get("win_rate"),
                     max_hold_cal_days=int(hold.max()) if len(hold) else 0, stuck_open=len(op), windows_restored=s.get("windows_restored"),
                     stale_exits=s.get("stale_exits"), exposure=m.get("exposure_mean"),
                     screen="PASS" if gates.passed(chk) else "FAIL", n_pass=sum(c["ok"] for c in chk), n_gates=len(chk),
                     old_sharpe=old_r["sharpe"], old_cagr=old_r["cagr"], checks_failed=[c["check"] for c in r["integrity"] if not c["ok"]]))
t = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(t.round(3).to_string(index=False))
for e, chk in detail.items():
    print(e); [print("   ", "PASS" if c["ok"] else "FAIL", c["gate"], c["value"], c["required"]) for c in chk]
mat = pd.concat(rets.values(), axis=1, join="inner").dropna()
pbo = stats.pbo_cscv(mat.to_numpy(), n_blocks=16); print("PBO H001 remedial:", pbo)
json.dump(dict(table=rows, gates=detail, pbo=pbo), open("research/cycles/C01_H001_remedial_results.json", "w"), indent=1, default=str)
