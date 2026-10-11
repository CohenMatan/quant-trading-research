"""Data Infrastructure v2.1 (owner D206): X801 = the frozen X998 with exactly five line-level changes; the v2.1 table
holds nothing after 2021-12-31 and, restricted to 2017, agrees with the frozen Data v2 table component by component."""
import difflib
import importlib
import json
import sys

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))

X998 = ROOT / "strategies/X998_data_v2_export/main.py"
X801 = ROOT / "strategies/X801_data_v21_export/main.py"
ALLOWED = {
    "from qr_data_v21 import load_table",
    '        if self.qr["end"] not in ("2013-12-31", "2017-12-31", "2021-12-31"):',
    '        self.last_session = np.datetime64(min(self.qr["end"], "2021-12-31")).astype(np.int64)',
    "        if t < date(max(self.end.year, 2017), 1, 1):",
}


def test_x801_is_x998_with_five_changes():
    a, b = X998.read_text().splitlines(), X801.read_text().splitlines()
    added = [l[1:] for l in difflib.unified_diff(a, b, lineterm="", n=0) if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in difflib.unified_diff(a, b, lineterm="", n=0) if l.startswith("-") and not l.startswith("---")]
    code_added = [l for l in added if not l.startswith("#")]
    assert set(code_added) == ALLOWED and len(code_added) == 4
    assert all(l.startswith("# X801") or l.startswith("# rule identical") or l.startswith("# last-session")
               for l in added if l.startswith("#"))
    assert len(removed) == 4 and "from qr_data_v2 import load_table" in removed


def _tables():
    v2 = importlib.import_module("qr_data_v2").load_table()
    v21 = importlib.import_module("qr_data_v21").load_table()
    return v2, v21


def test_v21_table_end_and_2017_restriction():
    v2, v21 = _tables()
    assert v21["version"] == "data_v2.1" and v21["end"] == "2021-12-31" and v2["end"] == "2017-12-31"
    epoch_end = 8035                                                   # day number of 2021-12-31 since 2000-01-01
    end17 = 6574                                                       # 2017-12-31
    for sid, rows in v21["sec_v1"]["sic_history"].items():
        assert all(r[0] <= epoch_end for r in rows)
    for c in v21["sec_v1"]["corrections"].values():
        assert all(r[1] <= epoch_end for r in c["rows"])
    # restricted to <= 2017 the correction layer and identity rows equal the frozen Data v2 table
    def cut(sv):
        sic = {s: [r for r in rows if r[0] <= end17] for s, rows in sv["sic_history"].items()}
        corr = {s: [r for r in c["rows"] if r[1] <= end17] for s, c in sv["corrections"].items()}
        return {s: r for s, r in sic.items() if r}, {s: r for s, r in corr.items() if r}
    assert cut(v21["sec_v1"]) == cut(v2["sec_v1"])
    assert v21["ext"] == v2["ext"] and v21["diag"] == v2["diag"]
    # idv (diagnostic identity-value check only, never a rule): every Data v2 entry unchanged; a few periods ending by
    # 2010 gain an entry whose first SEC value was filed after 2017
    assert all(v21["idv"][c][pe] == v for c, per in v2["idv"].items() for pe, v in per.items())
    # every Data v2 registrant with filings keeps them (prefix rows decoded to absolute period ends)
    def periods(cols):
        out, pe = [], 0
        for d, lag, form in zip(cols[0], cols[1], cols[2]):
            pe += d
            out.append((pe, pe + lag, form))
        return out
    lost = 0
    for cik, cols in v2["f"].items():
        new = set(periods(v21["f"].get(cik, [[], [], []])))
        lost += sum(1 for r in periods(cols) if r not in new)
    assert lost == 0
    for cik, cols in v21["f"].items():
        assert all(fd <= epoch_end for _pe, fd, _f in periods(cols))


def test_reference_summary_matches_packed_table():
    ref = json.loads((ROOT / "research/phase11/data_v21/data_v21_reference.json").read_text())
    from qresearch import v2pack
    import hashlib
    _, v21 = _tables()
    assert hashlib.sha256(v2pack.raw_bytes(v21)).hexdigest() == ref["table_sha256"]
    for n, h in ref["file_sha256"].items():
        assert hashlib.sha256((ROOT / "src/qresearch/lean" / n).read_text().encode()).hexdigest() == h


def test_x801_equals_x998_on_the_fake_market(monkeypatch):
    """Same synthetic market and the same fake table: X801 (end 2017) reproduces X998's complete export."""
    import types
    from test_data_v2 import _fake_table, _market, X998 as X998P
    from test_p7_export import _host

    def mutate(f, nd):
        f.security_reference = types.SimpleNamespace(security_type="ST00000001", is_depositary_receipt=False,
                                                     is_primary_share=True)
        f.company_reference.country_id = "USA"
    out = {}
    for name, path, mod in (("x998", X998P, "qr_data_v2"), ("x801", str(X801.relative_to(ROOT)), "qr_data_v21")):
        m = types.ModuleType(mod)
        m.load_table = _fake_table
        monkeypatch.setitem(sys.modules, mod, m)
        a = _host(monkeypatch, _market(), path=path, cls="DataV2Export", params=dict(mode="export"), end="2017-12-31",
                  mutate=mutate, sec_off=True)
        a.qr_on_end()
        parts = sorted((x for x in a.msgs if x.startswith("QRV2|")), key=lambda x: int(x.split("|")[1]))
        st = json.loads("".join(x.split("|", 2)[2] for x in parts))
        for k in ("wall_s", "score_s", "max_rss_mb"):
            st.pop(k, None)
        st["panel"].pop("build_s", None)
        out[name] = st
    assert out["x801"] == out["x998"]
