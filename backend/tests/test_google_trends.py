import pandas as pd

from app.connectors.google_trends import GoogleTrendsConnector, OBLIQUE_TERMS


def test_normalize_extracts_keyword_column_and_schema():
    raw = pd.DataFrame(
        {"gilets jaunes": [0, 5, 12], "isPartial": [False, False, False]},
        index=pd.to_datetime(["2018-06-01", "2018-06-02", "2018-06-03"]),
    )
    raw.index.name = "date"
    connector = GoogleTrendsConnector()
    df = connector.normalize(raw, keyword="gilets jaunes")

    assert list(df.columns) == ["source", "territoire", "date", "indicateur", "valeur", "metadonnees"]
    assert df["source"].unique().tolist() == ["google_trends"]
    assert df["valeur"].tolist() == [0.0, 5.0, 12.0]
    assert df["indicateur"].unique().tolist() == ["gilets jaunes"]


def test_normalize_empty_dataframe_returns_empty():
    connector = GoogleTrendsConnector()
    assert connector.normalize(pd.DataFrame(), keyword="x").empty


def test_oblique_terms_are_fixed_and_generic():
    # Panier fixe, meme liste pour tous les phenomenes -- pas de selection a posteriori.
    assert len(OBLIQUE_TERMS) == 5
    assert len(set(OBLIQUE_TERMS)) == 5
