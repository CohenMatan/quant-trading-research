# qr_industry.py — historical industry classification and the financial/REIT exclusion policy (D113). No QuantConnect
# imports; unit-tested offline (tests/test_industry_policy.py).
#
# Source: the SEC-assigned SIC code carried by each periodic filing of the registrant behind a security (XBRL RSS
# archive), effective from the day after that filing — historical, never current-status vendor metadata.
# Policy for a profitability/quality universe (owner item 10): on decision date T a security is
#   EXCLUDED 'REIT'       if its latest visible SIC is 6798 (real estate investment trusts);
#   EXCLUDED 'financial'  if its latest visible SIC is in 6000-6999 otherwise (banks, brokers, insurers incl. health
#                         insurers 6324, real estate, holding/investment offices);
#   else, when no SEC SIC is visible yet (foreign filers, pre-XBRL), the filing-structure rule decides:
#   EXCLUDED 'financial-format' if the latest visible report has the bank/insurer layout (qr_fundamentals);
#   otherwise KEPT. Candidate, benchmark and controls must apply the same function to the same universe.
from datetime import date

REIT_SIC = 6798
FIN_SIC = (6000, 6999)


class SICHistory:
    def __init__(self, table):
        self.t = {sid: [(date.fromisoformat(e), int(sic)) for e, sic, _cik in rows] for sid, rows in (table or {}).items()}

    def sic_on(self, sid, today):
        out = None
        for eff, sic in self.t.get(sid, ()):
            if eff <= today:
                out = sic
            else:
                break
        return out


def classify(sic, fin_format):
    """('REIT'|'financial'|'financial-format'|'operating'|'unclassified', source)."""
    if sic is not None:
        if sic == REIT_SIC:
            return "REIT", "SIC"
        if FIN_SIC[0] <= sic <= FIN_SIC[1]:
            return "financial", "SIC"
        return "operating", "SIC"
    if fin_format is True:
        return "financial-format", "filing structure"
    if fin_format is False:
        return "operating", "filing structure"
    return "unclassified", "none"


def excluded(category):
    return category in ("REIT", "financial", "financial-format")
