from app.connectors.insee_departments import UNEMPLOYMENT_CONNECTOR

XML = """<?xml version="1.0"?><root>
{series}
</root>"""


def serie(ref_area):
    return f'<Series REF_AREA="{ref_area}" TITLE_FR="x"><Obs TIME_PERIOD="2026-Q1" OBS_VALUE="7.5"/></Series>'


def test_les_departements_corses_sont_conserves():
    """Régression : le filtre « isdigit » excluait D2A et D2B (94 départements au lieu de 96)."""
    refs = ["D01", "D33", "D95", "D2A", "D2B", "D971", "D974", "R11", "FM", "FR-D976", "D2C", "D20"]
    df = UNEMPLOYMENT_CONNECTOR.normalize(XML.format(series="\n".join(serie(r) for r in refs)))
    codes = set(df["territoire"])
    assert codes == {"01", "33", "95", "2A", "2B", "20"} or codes == {"01", "33", "95", "2A", "2B"}
    assert {"2A", "2B"} <= codes
    assert not codes & {"971", "974", "R11", "FM", "976", "2C"}


def test_les_96_departements_du_reseau_sont_tous_atteignables():
    from app.spatial_series import load_department_network

    reseau = set(load_department_network()["adjacency"])
    refs = [f"D{c}" for c in sorted(reseau)]
    df = UNEMPLOYMENT_CONNECTOR.normalize(XML.format(series="\n".join(serie(r) for r in refs)))
    assert set(df["territoire"]) == reseau and len(reseau) == 96
